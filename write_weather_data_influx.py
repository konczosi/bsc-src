
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
CITY_ID = os.getenv('CITY_ID')
WEATHER_API_URL = os.getenv('WEATHER_API_URL')

TOKEN = os.getenv('TOKEN')
ORG = os.getenv('ORG')
BUCKET = os.getenv('BUCKET_H')
IF_URL = os.getenv('INFLUX_URL')

def get_weather_data():
    query_params = {'id': CITY_ID,'appid': WEATHER_API_KEY, 'units': 'metric'}
    response = requests.get(WEATHER_API_URL, params=query_params)
    if response.status_code == 200:
        result = response.json()['main']
        outside_temperature = result["temp"]
        outside_humidity = result["humidity"]
        outside_pressure = result["pressure"]
        outside_feels_like = result["feels_like"]
        data = {
            'temperature': float(outside_temperature),
            'humidity': float(outside_humidity),
            'pressure': float(outside_pressure),
            'feels_like' :float(outside_feels_like)
        }
    else:
        exit()

    return data

def main():
    with InfluxDBClient(url=IF_URL, token=TOKEN, org=ORG) as client:  # type: ignore
        write_api = client.write_api(write_options=SYNCHRONOUS)
        weather_data = get_weather_data()

        data_to_write = {
            "measurement": "api",
            "tags": {
                "location": "outdoor"
            },
            "fields": {
                'temperature': weather_data['temperature'],
                'humidity': weather_data['humidity'],
                'pressure': weather_data['pressure'],
                'feels_like': weather_data['feels_like']
            },
            "time": datetime.utcnow()
        }
        write_api.write(BUCKET, ORG, data_to_write, write_precision='s')  # type: ignore

if __name__ == "__main__":
    main()