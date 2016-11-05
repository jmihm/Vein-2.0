from miso_tables.models import NPH, LookAhead, WeatherForecast, Node
import pickle
import numpy
from sklearn import preprocessing
import math


#node_name = "SME.MORROW_1"
#node_name = "WEC.ERG1"

#node = Node.objects.get(name=node_name)
node = Node.objects.order_by("?").first()
data = NPH.objects.filter(node_name = node.name)
hour_offset = 2

lmps = [(x.dart_value, x.hour_ending, x.day) for x in data]
lmps.sort(key=lambda x: (x[2], x[1]))

look_ahead_max = 24

matched_lmps = []
for i, lmp in enumerate(lmps[look_ahead_max:]):
    matched_lmps.append([lmps[i], lmp])




new_lmps = []

for i, lmp in enumerate(matched_lmps[look_ahead_max:]):
    new_data = []
    for j in range(hour_offset-1, -1, -1):
        if i - j < 0:
            break
        new_data.append(matched_lmps[i-j])
    if new_data:
        new_lmps.append(new_data)

filtered = [x for x in new_lmps if x[-1][0][1] <= 10]

# Encode the hour of the day into polar coordinates
def encode_hour(hour):
    return [math.sin((2.*math.pi*hour/24.0)), math.cos((2.*math.pi*hour/24.0))]

# Encode they day of the year into polar coordinates
def encode_day(day):
    return [math.sin((2.*math.pi*day/360.0)), math.cos((2.*math.pi*day/360.0))]


print(filtered[0])
print(filtered[10])

X = []
Y = []
Y_cat = []

min_bound = -.2
max_bound = .2

def add_weather(forecast_set):
    item = forecast_set[0]
    vals = []
    vals.append(abs(65-item.apparent_temp))
    vals.append(abs(65-item.temperature))
    vals.append(item.humidity)
    vals.append(item.apparent_temp)
    vals.append(item.temperature)
    vals.append(abs(65-item.apparent_temp)**2)
    vals.append(abs(65-item.temperature)**2)
    vals.append(item.humidity**2)
    return vals

for group in filtered:
    #for item in group:
    #    print item
    #print(group[0])

    xx = [x[0][0] for x in group]

    pred_hour = group[-1][1][1]
    pred_date = group[-1][1][2]
    #print(xx)
    print("Predicting date %s, hour: %s" % (pred_date, pred_hour))
    print("Result: %s" % group[-1][1][0])
    #input()
    xx.extend(encode_hour(pred_hour))
    xx.extend(encode_day(pred_date.day))

    #try:
    #    pred_weather = WeatherForecast.objects.filter(predicted_date=pred_date,
    #                                           latitude = node.latitude,
    #                                           longitude=node.longitude)#
#
 #       if pred_weather.count() != 24:
  #          print("Incorrect amount of weather found %s..skipping" % pred_weather.count())
   #         continue
    #except:
     #   print(pred_date, "Failed")
      #  continue
    try:
        look_ahead = LookAhead.objects.get(date=pred_date, hour_ending=pred_hour)
        xx.append(look_ahead.south_pred)
    except:
        print(pred_date, "Failed to find look ahead")
        continue
    """
    try:
        if pred_hour == 1:
            xx.extend(add_weather(pred_weather.filter(predicted_hour=1)))
            xx.extend(add_weather(pred_weather.filter(predicted_hour=2)))
            xx.extend(add_weather(pred_weather.filter(predicted_hour=3)))
        elif pred_hour == 24:
            xx.extend(add_weather(pred_weather.filter(predicted_hour=22)))
            xx.extend(add_weather(pred_weather.filter(predicted_hour=23)))
            xx.extend(add_weather(pred_weather.filter(predicted_hour=24)))
        else:
            xx.extend(add_weather(pred_weather.filter(predicted_hour=pred_hour-1)))
            xx.extend(add_weather(pred_weather.filter(predicted_hour=pred_hour)))
            xx.extend(add_weather(pred_weather.filter(predicted_hour=pred_hour+1)))
    except:
        print(pred_date, "Failed to find hours?")
        continue
    """


    true_val = group[-1][1][0]
    Y.append(true_val)
    Y_cat.append(1 if true_val > 0 else 0)
    X.append(xx)


print(len(X), len(Y))
print(X[0], Y[0])
print(X[500], Y[500])
print(Y.count(-1), Y.count(0), Y.count(1), Y.count(2))

vals = len(X)
train_set_size = int(vals*.85)
valid_set_size = int(vals*.1)
test_set_size = int(vals*.05)

scaler = preprocessing.MinMaxScaler((0, 1))
X_train = scaler.fit_transform(numpy.asarray(X[:train_set_size]))
y_train = numpy.asarray(Y[:train_set_size])
y_cat_train = numpy.asarray(Y_cat[:train_set_size])

X_valid = scaler.transform(numpy.asarray(X[train_set_size:train_set_size+valid_set_size]))
y_valid = numpy.asarray(Y[train_set_size:train_set_size+valid_set_size])
y_cat_valid = numpy.asarray(Y_cat[train_set_size:train_set_size+valid_set_size])

X_test = scaler.transform(numpy.asarray(X[train_set_size+valid_set_size:]))
y_test = numpy.asarray(Y[train_set_size+valid_set_size:])
y_cat_test = numpy.asarray(Y_cat[train_set_size+valid_set_size:])

train_set = (X_train, y_train, y_cat_train)
valid_set = (X_valid, y_valid, y_cat_valid)
test_set = (X_test, y_test, y_cat_test)


print(valid_set[0].shape)
print(valid_set[1].shape)
print(valid_set[1])

print(test_set[0].shape)
print(test_set[1].shape)
print(test_set[1])
print(node.name)
f = open("node_trial_squared_v2_%s.pkl" % node.name[:3], "wb")
pickle.dump((train_set, valid_set, test_set), f, 2)
f.close()
