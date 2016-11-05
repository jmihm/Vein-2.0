import datetime
from miso_tables.models import WeatherForecast, Node

node = Node.objects.get(name="BREC.COLE1")
hour_offset = 2

d = datetime.date(year=2014, day=1, month=1)
while d < datetime.date(year=2014, day=1, month=6):
    pred_weather = WeatherForecast.objects.filter(predicted_date=d,
                                               latitude = node.latitude,
                                               longitude=node.longitude)
    d += datetime.timedelta(days=1)
    print(pred_weather.count())

    if pred_weather.count() > 24:
        for i in range(1, 25):
            vals = pred_weather.filter(predicted_hour=i)
            if vals.count() == 2:
                vals[0].delete()

