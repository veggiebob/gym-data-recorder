import requests
from bs4 import BeautifulSoup
import datetime

from dbconn import get_conn


def get_current_gym_data():
    """
    Returns: (lower, upper, aquatic)
    """
    res = requests.get('https://recreation.rit.edu/facilityoccupancy')
    website = BeautifulSoup(res.text, 'html.parser')
    elements = website.find_all('div', class_='occupancy-card')
    if len(elements) < 3:
        raise ValueError("Expected at least 3 occupancy cards, found: {}".format(len(elements)))
    titles = [elem.find('h2').text.lower() for elem in elements]
    occupancies = [int(elem.find('p', class_='occupancy-count').text) for elem in elements]
    occupancy_data = { 'lower': 0, 'upper': 0, 'aquatic': 0 }
    for title, occupancy in zip(titles, occupancies):
        for key in occupancy_data:
            if key in title:
                occupancy_data[key] = occupancy
                break
    return occupancy_data['lower'], occupancy_data['upper'], occupancy_data['aquatic']

def lambda_handler(event, context):
    lower, upper, aquatic = get_current_gym_data()
    # current_time = datetime.datetime.now()
    # time_with_timezone = current_time.astimezone()
    with get_conn() as cursor:
        cursor.execute("INSERT INTO gym_occupancy (lower, upper, aquatic, time_collected) VALUES (%s, %s, %s, now())",
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