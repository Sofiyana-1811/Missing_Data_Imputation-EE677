import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re

def extractNumber(data):
    match = re.search(r'\d+', data)

    if match:
        number = match.group()
        return float(number)
    return np.nan

def cleanData(weather_data, date):
    time = pd.to_datetime(date+' '+weather_data[0])
    temperature_in_F = float(weather_data[1].replace('Â°F',""))
    temperature = round((temperature_in_F - 32) * 5/9, 2)
    pressure = extractNumber(weather_data[2])
    wind = extractNumber(weather_data[3])
    visibility = extractNumber(weather_data[4])
    cloud_cover = weather_data[5]
    weather_data = [time, temperature, pressure, wind, visibility, cloud_cover]
    return weather_data

def getData(date):
    try:
        link = f'https://weatherspark.com/h/d/149040/{date}/Historical-Weather'
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        day_data = []
        for minutes in range(0, 23 * 60 + 30, 30):
            hours, mins = divmod(minutes, 60)
            id = f"metar-{hours:02d}-{mins:02d}"
            rows = soup.find_all('tr', id=id)
            for row in rows:
                if 'History-MetarReports-superseded' in row['class']:
                    continue
                row_data = row.find_all('td')
                # for data in row_data:
                if(len(row_data)==2):
                    continue
                elif len(row_data)==6:
                    weather_data = [x.text.strip() for x in row_data]
                    weather_data = cleanData(weather_data, date)
                    day_data.append(weather_data)
                else:
                    print(f"Data size mismatch in {date}")
        return np.array(day_data)
    except:
        print(f"Error occured while reading {date}")

def writeData(data, date):
    path = f'weather_data/weather-{date}.xlsx'
    columns = ['Time', 'Temperature', 'Pressure', 'Wind', 'Visibility', 'Cloud_Cover']
    df = pd.DataFrame(data, columns = columns) 
    df.to_excel(path, index=False)

year = 2023  
for month in range(1, 13):
    for day in range(1, 32):
        try:
            date = datetime.date(year, month, day)            
            data = getData(date.strftime("%Y/%m/%d"))
            writeData(data, date.strftime("%B-%d-%Y"))
        except ValueError:
            pass