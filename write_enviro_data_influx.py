from datetime import datetime
from dotenv import load_dotenv
import time
import os
from bme280 import BME280
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()
TOKEN = os.getenv('TOKEN')
ORG = os.getenv('ORG')
BUCKET = os.getenv('BUCKET_H')
IF_URL = os.getenv('INFLUX_URL')

def get_sensor_data():
    bme280 = BME280()
    bme280.get_temperature()
    time.sleep(1)
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    illuminance = ltr559.get_lux()
    
    data = {
        'temperature': float(temperature),
        'pressure': float(pressure),
        'humidity': float(humidity),
        'illuminance': float(illuminance)
    }

    return data

def main():
    with InfluxDBClient(url=IF_URL, token=TOKEN, org=ORG) as client:  # type: ignore
        write_api = client.write_api(write_options=SYNCHRONOUS)
        sensor_data = get_sensor_data()

        data_to_write = [
            {
                "measurement": "sensor",
                "tags": {
                    "location": "indoor"},
                "fields": {
                    'temperature': sensor_data['temperature'],
                    'humidity': sensor_data['humidity'],
                    'pressure': sensor_data['pressure'],
                    'illuminance': sensor_data['illuminance'],
                },
                "time": datetime.utcnow()
            }
        ]
        write_api.write(BUCKET, ORG, data_to_write , write_precision='s') # type: ignore

if __name__ == "__main__":
    main()