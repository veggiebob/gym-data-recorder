import requests
from bs4 import BeautifulSoup
import psycopg2
import json
import datetime

from dbconn import get_conn


def get_current_gym_data():
    """
    Returns: (lower, upper, aquatic)
    """
    res = requests.get('https://recreation.rit.edu/facilityoccupancy')
    website = BeautifulSoup(res.text, 'html.parser')
    num_elements = website.find_all('p', class_='occupancy-count')
    int_data = list(map(lambda elem: int(elem.strong.text), num_elements))
    data = int_data[0], int_data[2], int_data[4]
    return data

def lambda_handler(event, context):
    lower, upper, aquatic = get_current_gym_data()
    # current_time = datetime.datetime.now()
    # time_with_timezone = current_time.astimezone()
    with get_conn() as cursor:
        cursor.execute("INSERT INTO gym_occupancy (lower, upper, aquatic, time) VALUES (%s, %s, %s, now())",
                          (lower, upper, aquatic))
        cursor.connection.commit()
    return {
        'statusCode': 200,
        'body': {
            'lower': lower,
            'upper': upper,
            'aquatic': aquatic,
            'timestamp': datetime.datetime.now().isoformat()
        }
    }

if __name__ == "__main__":
    event = {}
    context = {}
    result = lambda_handler(event, context)
    print(result)