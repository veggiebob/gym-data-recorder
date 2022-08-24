import datetime
from time import sleep
import fetch_data

while True:
  data = fetch_data.read_csv_data()
  new_data = fetch_data.add_datapoint(data)
  fetch_data.save_data(new_data)
  sleep(10 * 60) # only record every 10 minutes
