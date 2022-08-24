from bs4 import BeautifulSoup
import requests
import datetime

CSV_NAME = 'output_pd.csv'
DAYOFWEEK_INDEX = { i: day for i, day in zip(range(7), ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']) }

def get_time():
    return pd.Timestamp(datetime.datetime.now())

def get_current_gym_data():
    '''
    Returns: (lower, upper, aquatic)
    '''
    res = requests.get('https://recreation.rit.edu/facilityoccupancy')
    website = BeautifulSoup(res.text, 'html.parser')
    num_elements = website.find_all('p', class_='occupancy-count')
    int_data = list(map(lambda elem: int(elem.strong.text), num_elements))
    data = int_data[0], int_data[2], int_data[4]
    return data

def get_row():
    '''
    Returns a row of GYM data AND a TIMESTAMP
    '''
    lower, upper, aquatic = get_data()
    t = get_time()
    row = dict(lower=lower,
               upper=upper,
               aquatic=aquatic,
               time=t,
               day=t.weekday())
    return row

def read_csv_data():
    '''
    Returns the currently existing data, or an empty table with the columns
    '''
    try:
        data = pd.read_csv(csv_name)
        data.time = pd.to_datetime(data.time)
        return data
    except:
        return pd.DataFrame(columns=['time', 'lower', 'upper', 'aquatic', 'day'])

def save_data(data):
    '''
    Save the data
    '''
    data.to_csv(CSV_NAME, index=False)
    
def add_datapoint(data):
    '''
    Add a datapoint to the data set
    '''
    row = get_row()
    data.loc[len(data)] = row
    return data

