import dataclasses
from psycopg2 import sql

from dbconn import get_conn


@dataclasses.dataclass
class ResponseRecord:
    """
    Represents a single record in the response data.
    Response data is a list of these records, which may be unordered.
    """
    day: int # 0-6, where 0 is Monday
    x: float # [0, 1] representing the time of day as a fraction
    y: float # [0, infinity) representing the sampled value of occupancy at that time.

def lambda_handler(event, context):
    """
    Queries gym population data and aggregates by day.
    event: {
        week_mode: bool,  # If true, aggregates by week; otherwise, by day. (currently ignored)
    }
    """
    data = get_lower_upper_histogram(48)

    return {
        'statusCode': 200,
        'body': {
            'data': data,
        }
    }

def get_lower_upper_histogram(buckets: int):
    if buckets < 1:
        raise ValueError("`buckets` must be >= 1")

    # 2) build the query with psycopg2.sql
    q = sql.SQL("""
        WITH
          bucket_series AS (
            SELECT generate_series(0, {b}-1) AS bucket
          ),
          dow_series AS (
            SELECT generate_series(0, 6) AS day_of_week
          ),
          aggregated AS (
            SELECT
              extract(dow FROM created_at)::int                               AS day_of_week,
              floor((extract(epoch FROM time) / 86400.0) * {b})::int          AS bucket,
              avg(lower)::double precision                                    AS avg_lower,
              avg(upper)::double precision                                    AS avg_upper,
              avg(aquatic)::double precision                                  AS avg_aquatic
            FROM public.gym_occupancy
            GROUP BY 1, 2
          )
        SELECT
          d.day_of_week,
          ((b.bucket + 0.5) / {b})::double precision                        AS day_frac,
          COALESCE(a.avg_lower,   0::double precision)                     AS avg_lower,
          COALESCE(a.avg_upper,   0::double precision)                     AS avg_upper,
          COALESCE(a.avg_aquatic, 0::double precision)                     AS avg_aquatic
        FROM dow_series    AS d
        CROSS JOIN bucket_series AS b
        LEFT JOIN aggregated     AS a
          ON a.day_of_week = d.day_of_week
         AND a.bucket      = b.bucket
        ORDER BY d.day_of_week, b.bucket;
        """).format(
        b=sql.Literal(buckets),
    )

    # 3) execute and fetch
    with get_conn() as cursor:
        cursor.execute(q)
        return [{'day': day, 'x': x, 'y': lower + upper} for (day, x, lower, upper, aq) in cursor.fetchall()]


if __name__ == "__main__":
    event = {}
    context = {}
    result = lambda_handler(event, context)
    print(result)