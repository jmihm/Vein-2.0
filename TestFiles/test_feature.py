from miso_tables.models import NPH, LookAhead, WeatherForecast, Node
from datetime import datetime, timedelta
import numpy as np

node_name = 'SME.MORROW_1'

raw_data = {(row.day, row.hour_ending) : row.dart_value
            for row in NPH.objects.filter(node_name=node_name)}

times = sorted(raw_data.keys())

X, y = [], []
for (date, hour_ending) in times:
    (d1, h1) = (date - timedelta(days=1), ((hour_ending-1) % 24)+1)
    (d2, h2) = (date - timedelta(days=(1 if hour_ending > 1 else 2)), ((hour_ending-2) % 24)+1)


    if not ((d1, h1) in raw_data and (d2, h2) in raw_data):
        continue

    feature = [raw_data[(d1, h1)],
               raw_data[(d2, h2)],
               np.cos(2*np.pi*hour_ending/24),
               np.sin(2*np.pi*hour_ending/24),
               np.cos(2*np.pi*date.isoweekday()/7),
               np.sin(2*np.pi*date.isoweekday()/7)]
    label = [raw_data[(date, hour_ending)]]
    X.append(feature)
    y.append(label)

X = np.mat(X)
y = np.mat(y)

