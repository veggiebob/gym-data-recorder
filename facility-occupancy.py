from selenium import webdriver
import datetime
from time import sleep

options = webdriver.chrome.options.Options()
options.headless = True
driver = webdriver.Chrome(options=options)
while True:
  print('opening webpage...')
  with open('output.csv', 'a') as output_file:
    driver.get('https://recreation.rit.edu/facilityoccupancy')
    elems = driver.find_elements_by_css_selector('p.occupancy-count strong')
    elems = map(lambda x: x.get_attribute('innerHTML'), elems)
    elems = list(elems)
    data = f'{elems[0]},{elems[2]},{elems[4]}\n'
    row = datetime.datetime.now().strftime("%U,%u,%T,") + data
    print('writing an entry...')
    output_file.write(row)
    output_file.close()

  sleep(10 * 60) # only record every 10 minutes
