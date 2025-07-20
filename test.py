from psycopg2 import sql

from dbconn import get_conn


def test_epoch_behavior_db():
    # a few sample times to check
    times = ['00:00:00', '06:00:00', '12:30:00', '18:00:00', '23:59:59']

    with (get_conn() as cur):
        print(" time      | secs_since_midnight | frac_of_day")
        print("-----------+---------------------+------------")
        for t in times:
            cur.execute("""
              SELECT
                extract(epoch FROM %s::time)      AS secs,
                extract(epoch FROM %s::time)/86400.0 AS frac
            """, (t, t))
            secs, frac = cur.fetchone()
            print(f" {t:<8} | {int(secs):>19} | {frac:>10.4f}")

        print('\n')
        q = sql.SQL("SELECT extract(epoch FROM (now() AT TIME ZONE {tz})::time) AS now, extract(epoch FROM (now() AT TIME ZONE {tz})::time)/86400.0 AS now_frac"
                    ).format(tz=sql.Literal('America/New_York'))
        cur.execute(q)
        now, now_frac = cur.fetchone()
        print(f"Current time in seconds since midnight: {int(now)}")
        print(f"Current time as fraction of the day: {now_frac:.4f}")

if __name__ == "__main__":
    test_epoch_behavior_db()