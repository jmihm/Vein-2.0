from miso_tables.models import NPH, LookAhead, WeatherForecast, Node
import theano
import theano.tensor as T
import pickle
import numpy
from sklearn import preprocessing
from datetime import timedelta
import math
import pandas as pd

node = Node.objects.get(name="SME.MORROW_1")
data = NPH.objects.filter(node_name = node.name)
hour_offset = 2

lmps = [(x.dart_value, x.hour_ending, x.day) for x in data]


look_ahead_max = 24

lmps.sort(key=lambda x: (x[2], x[1]))

df = pd.DataFrame({"t0": lmps, "t1": lmps, "t2": lmps, "t3": lmps, "future":lmps})

# Shift ahead future by 24 hours
df.future = df.future.shift(-look_ahead_max)

df.t1 = df.t1.shift(1)
df.t2 = df.t1.shift(2)
df.t3 = df.t1.shift(3)

print(df)



assert False

new_lmps = []

for i, lmp in enumerate(matched_lmps[look_ahead_max:]):
    new_data = []
    for j in range(hour_offset-1, -1, -1):
        new_data.append(matched_lmps[i-j])
    new_lmps.append(new_data)

filtered = [x for x in new_lmps if x[-1][0][1] <= 6]

# Encode the hour of the day into polar coordinates
def encode_hour(hour):
    return [math.sin((2.*math.pi*hour/24.0)), math.cos((2.*math.pi*hour/24.0))]

# Encode they day of the year into polar coordinates
def encode_day(day):
    return [math.sin((2.*math.pi*day/360.0)), math.cos((2.*math.pi*day/360.0))]


print(filtered[0])
X = []
Y = []
for group in filtered:
    #print(group[0])
    xx = [x[0][0] for x in group]
    pred_hour = group[-1][1][1]
    pred_date = group[-1][1][2]
    #xx.append(one_hot_encode_hour(pred_hour))
    #xx.extend(one_hot_encode_hour(pred_hour))   # add one-hot encoded information about the hour we are predicting
    xx.extend(encode_hour(pred_hour))
    xx.extend(encode_day(pred_date.day))
    print(pred_date)
    print(pred_hour)
    try:
        pred_weather = WeatherForecast.objects.filter(predicted_date=pred_date)

                                               #latitude = node.latitude,
                                               #longitude=node.longitude)
        #pred_weather_prev = WeatherForecast.objects.get(predicted_date=pred_date - timedelta(days=1),
        #                                       predicted_hour=pred_hour,
        #                                       latitude = node.latitude,
        #                                       longitude=node.longitude)
        if pred_weather.count() != 24:
            print("Incorrect amount of weather found..skipping")
            continue
    except:
        print(pred_date, "Failed")
        continue
    try:
        look_ahead = LookAhead.objects.get(date=pred_date, hour_ending=pred_hour)
        xx.append(look_ahead.south_pred)
    except:
        print(pred_date, "Failed to find look ahead")
        continue
    for item in pred_weather:

        #xx.append(item.temperature)
        #xx.append(item.apparent_temp)
        #xx.append(item.humidity)

        xx.append(abs(65-item.apparent_temp))   # heating degrees
        xx.append(abs(65-item.temperature))
    Y.append(0 if group[-1][1][0] <= 0 else 1)
    X.append(xx)

X = preprocessing.minmax_scale(X, (0, 1))
print(len(X), len(Y))
print(X[0], Y[0])
print(X[500], Y[500])
print(Y.count(-1), Y.count(0), Y.count(1), Y.count(2))

vals = X.shape[0]
train_set_size = int(vals*.85)
valid_set_size = int(vals*.1)
test_set_size = int(vals*.05)

train_set = (numpy.asarray(X[:train_set_size]), numpy.asarray(Y[:train_set_size]))
valid_set = (numpy.asarray(X[train_set_size:train_set_size+valid_set_size]), numpy.asarray(Y[train_set_size:train_set_size+valid_set_size]))
test_set = (numpy.asarray(X[train_set_size+valid_set_size:]), numpy.asarray(Y[train_set_size+valid_set_size:]))

print(valid_set[0].shape)
print(valid_set[1].shape)
print(valid_set[1])

print(test_set[0].shape)
print(test_set[1].shape)
print(test_set[1])

f = open("node_trial.pkl", "wb")
pickle.dump((train_set, valid_set, test_set), f, 2)
f.close()

