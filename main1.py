import requests
from bs4 import BeautifulSoup
import pandas as pd

# Find the last page number.
response = requests.get("https://nextspaceflight.com/launches/past/?search=")
data = response.text
soup = BeautifulSoup(data, 'html.parser')
last_page_soup = soup.select_one('.mdc-button--raised:nth-of-type(2)')
last_page = int(last_page_soup.get('onclick').split('=')[2].split('&')[0])

final_data = []

for page_no in range(1, last_page + 1):  # loop through every page.
    response = requests.get(f"https://nextspaceflight.com/launches/past/?page={page_no}&search=")
    data = response.text
    soup = BeautifulSoup(data, 'html.parser')
    missions_in_page = soup.select('h5')
    location_and_datetime_soup = soup.select(
        '.mdl-card__supporting-text')  # no distinctive classes inside the page hence extracting it outside itself.
    mission_details_link_soup = soup.select('.mdc-button:first-child')

    for i in range(len(missions_in_page)):  # loop through all missions in one page.
        mission_details_link = mission_details_link_soup[i].get('onclick')[35:-1]
        response = requests.get(f"https://nextspaceflight.com/launches/details/{mission_details_link}")
        data = response.text
        soup = BeautifulSoup(data, 'html.parser')
        details_soup = soup.select_one('title')
        mission_status_soup = soup.select_one('.status')
        organisation_soup = soup.select_one('.a:first-child .mdl-cell:first-child')
        mission_data_soup = soup.select_one('.a:first-child .mdl-cell:nth-of-type(2)')
        mission_price_soup = soup.select_one('.a:first-child .mdl-cell:nth-of-type(3)')
        location_datetime_split = location_and_datetime_soup[i].get_text(strip=True, separator="#").split(
            '#')  # Splitting time and location into two parts.
        record = {
            "Organisation": organisation_soup.getText(),
            "Location": location_datetime_split[1],
            "Datetime": location_datetime_split[0],
            "Details": details_soup.getText(),
            "Status": mission_data_soup.getText(strip=True).split(': ')[1],
            "Price": mission_price_soup.getText(strip=True)[8:-8],
            "Mission_status": mission_status_soup.getText(strip=True)
        }
        final_data.append(record)

    for mission in final_data:  # convert price to float and replace bad price data with empty strings.
        try:
            mission['Price'] = float(mission['Price'])
        except ValueError:
            mission['Price'] = ''

print(final_data)

# create and add scraped data to a csv file.
pd.DataFrame(final_data).to_csv("mission_launches.csv")
