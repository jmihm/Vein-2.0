import forecastio
import pytz
from datetime import datetime
from datetime import timedelta
import requests
import json

api_key = "11022e89bcaf0bda485162ce8e966fac"

# Lat and long for NYC


def naive_to_eastern(naive_datetime):
    eastern = pytz.timezone("US/Eastern")
    return eastern.localize(naive_datetime)

def naive_to_utc(naive_datetime):
    utc = pytz.timezone("UTC")
    return utc.localize(naive_datetime)

def utc_to_eastern(naive_datetime):
    utc = pytz.timezone("UTC")
    eastern = pytz.timezone("US/Eastern")
    utc_dt = utc.localize(naive_datetime)
    eastern_dt = utc_dt.astimezone(eastern)
    return eastern_dt

def eastern_to_utc(naive_datetime):
    utc = pytz.timezone("UTC")
    eastern = pytz.timezone("US/Eastern")
    eastern_dt = eastern.localize(naive_datetime)
    utc_dt = eastern_dt.astimezone(utc)
    return utc_dt


lat = 31.116913
lng = -89.438324

#d = datetime.now() - timedelta(days=1)
d = datetime(year=2016, month=3, day=30, hour=10)
#e = pytz.timezone("US/Eastern")
#d = e.localize(d)
"""
if d is None:
    url = 'https://api.forecast.io/forecast/%s/%s,%s' \
              '?units=%s' % (api_key, lat, lng)
else:
    url_time = d.replace(microsecond=0).isoformat()  # API returns 400 for microseconds
    url = 'https://api.forecast.io/forecast/%s/%s,%s,%s?extend=hourly'  % (api_key, lat, lng, url_time)

forecastio_reponse = requests.get(url)
json_data = forecastio_reponse.json()
print(json.dumps(json_data))
"""


forecast = forecastio.load_forecast(api_key, lat, lng, time=d)
byHour = forecast.hourly()
print(forecast.__dict__)
print(byHour.summary)
print(byHour.icon)

for hourlyData in byHour.data:
    print("%s: %s" % (utc_to_eastern(hourlyData.time), hourlyData.temperature))

