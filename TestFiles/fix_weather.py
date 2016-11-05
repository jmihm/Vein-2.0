from miso_tables.models import WeatherForecast
import datetime

"""
# This script fixes a strange weather bug that needs to be resolved in
# weather loader where certain hours are placed on the wrong day
d1 = datetime.date(year=2014, month=1, day=2)
while d1 < datetime.date.today() - datetime.timedelta(days=9):
    d2 = d1 + datetime.timedelta(days=1)
    forecasts = WeatherForecast.objects.filter(predicted_date=d2)
    for forecast in forecasts:
        if forecast.predicted_hour >= 19 and forecast.predicted_hour <= 23:
            forecast.predicted_date = d1
            forecast.save()
    d1 = d1 + datetime.timedelta(days=1)
"""

forecasts = WeatherForecast.objects.all()
for forecast in forecasts:
    if forecast.predicted_date == forecast.prediction_made_dt.date():
        forecast.predicted_date = forecast.prediction_made_dt + datetime.timedelta(days=1)
        forecast.save()
        print("Saved")
        #print(forecast.predicted_date, forecast.predicted_hour, forecast.prediction_made_dt)

"""
d1 = datetime.date(year=2014, month=1, day=2)
while d1 < datetime.date.today() - datetime.timedelta(days=9):
    forecasts = WeatherForecast.objects.filter(predicted_date=d1)
    #print(forecasts.count())
    if forecasts.count() != 24:
        print(d1)
        print("Error found")
        for fore in forecasts:
            print(fore.predicted_date, fore.predicted_hour)

#for weatherObject in WeatherForecast.objects.all().group_by("predicted_date"):
"""