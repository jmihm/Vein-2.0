import os
import re
from datetime import date, timedelta, datetime

from data_loading.data_loaders import DataLoader
from data_loading.data_loaders import loader_utils
from miso_tables import models
from dateutil.parser import parse
import forecastio


# Forecast.io api key
api_key = "11022e89bcaf0bda485162ce8e966fac"

# This is the most recent information we have access to when making predictions
BEST_HOUR = 10

class WeatherLoader(DataLoader.DataLoader):

    def get_model_class(self):
        return models.WeatherForecast

    def get_priority(self):
        return 2

    def get_accessible_dates(self):
        # MISO provides data from the last n years, up until ~3 days before the present date
        n = 2
        n_years_ago = date.today().year - n
        start_date = date(n_years_ago, 1, 1)
        end_date = date.today() - timedelta(days=10)
        return loader_utils.get_date_range_set_inclusive(start_date, end_date)

    def insert_data_for_date(self, date):
        print("Adding weather for date: %s" % (date))
        dt = datetime(year=date.year, day=date.day, month=date.month,
                            hour=BEST_HOUR)
        nodes = models.Node.objects.filter(include_weather=True)
        forecasts = []
        for node in nodes:
            print('adding weather for node %s' % node.name)
            latitude = node.latitude
            longitude = node.longitude
            future_dt = dt + timedelta(days=1)

            forecast = forecastio.load_forecast(api_key, latitude, longitude,
                                                time=future_dt)
            by_hour = forecast.hourly()
            for hour_block in by_hour.data:
                print(loader_utils.utc_to_eastern(hour_block.time))
                print(hour_block.__dict__)

                eastern_dt = loader_utils.utc_to_eastern(hour_block.time)
                hour = eastern_dt.hour
                if hour == 0:
                    eastern_dt = eastern_dt - timedelta(days=1)
                    hour = 24
                print(dt)
                print(future_dt)
                print(eastern_dt)

                w = models.WeatherForecast(
                    prediction_made_dt = dt,
                    predicted_hour = hour,
                    predicted_date = eastern_dt,
                    latitude = latitude,
                    longitude = longitude,
                    cloud_cover = hour_block.cloudCover if hasattr(hour_block, "cloudCover") else 0,
                    apparent_temp = hour_block.apparentTemperature,
                    pressure = hour_block.pressure if hasattr(hour_block, "pressure") else 0,
                    visibility = hour_block.visibility if hasattr(hour_block, "visibility") else 0,
                    summary = hour_block.summary,
                    temperature = hour_block.temperature,
                    dew_point = hour_block.dewPoint if hasattr(hour_block, "dewPoint") else 0,
                    humidity = hour_block.humidity if hasattr(hour_block, "humidity") else 0,
                    ozone = hour_block.ozone if hasattr(hour_block, "ozone") else 0,
                    wind_speed = hour_block.windspeed if hasattr(hour_block, "windspeed") else 0,
                    wind_bearing = hour_block.windBearing if hasattr(hour_block, "windBearing") else 0,
                    precip_intensity = hour_block.precipIntensity if hasattr(hour_block, "precipIntensity") else 0,
                    precip_probability = hour_block.precipProbability if hasattr(hour_block, "precipProbability") else 0,
                )
                forecasts.append(w)
        models.WeatherForecast.objects.bulk_create(forecasts)



