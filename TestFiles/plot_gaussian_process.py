import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.gaussian_process import GaussianProcess
import pickle
import collections
import random

file_name = "EES.SABINE1.pkl"
# EES used for presentation
with open("./feature_generation/generated_data/%s" % file_name, 'rb') as f:
    try:
        X, y = pickle.load(f, encoding='latin1')
    except:
        X, y = pickle.load(f)


rng = np.random.RandomState(42)
yy = []
yy_ = []
cum_profit_results = {}
raw_profit_results = {}

print(X.shape)
print(y.shape)
gp = GaussianProcess(corr="squared_exponential", theta0=.5, nugget=1)

gps = [(gp, .26, "40%"), (gp, .674, "50%"), (gp, .842, "60%"),(gp, 1.04, "70%"), (gp, 1.28, "80%"), (gp, 1.645, "90%")]

colors = iter(cm.rainbow(np.linspace(0, 1, len(gps))))

train_size = .8

for clf, conf, name in gps:
    total = len(X)
    size = int(total * train_size)
    print(total, size)
    X_train = X[:size]
    X_test = X[size:]
    y_train = y[:size]
    y_test = y[size:]
    clf.fit(X_train, y_train)
    predictions, MSE = clf.predict(X_test, eval_MSE=True)
    sigma = np.sqrt(MSE)


    cum_profits = [0]
    raw_profits = []
    hours = [0]
    for i, pred in enumerate(predictions):
        conf_val = conf * sigma[i]
        if pred-conf_val > 0:
            cum_profits.append(cum_profits[-1] + y_test[i])
            raw_profits.append(y_test[i])
            hours.append(i)
        if pred+conf_val <= 0:
            raw_profits.append(-1.*y_test[i])
            cum_profits.append(cum_profits[-1] + -1.*y_test[i])
            hours.append(i)
    print(name, cum_profits[-1])
    plt.plot(hours, cum_profits, label=name, color=next(colors))
    cum_profit_results[name] = cum_profits[:]
    raw_profit_results[name] = (raw_profits[:], hours[:])

for gp, conf, name in gps:

    cum_profits = cum_profit_results[name]
    raw_profits, hours = raw_profit_results[name]
    print("Model %s:" % name)
    print("\t%s total profit" % (cum_profits[-1]))
    neg_profits, new_profits = [], []
    t = 0
    prev_val = 0
    for i, val in enumerate(raw_profits):
        t += val
        hour = hours[i]
        if hour/70!=prev_val and i != 0:
            if t < 0:
                neg_profits.append(t)
            new_profits.append(t)
            t = 0
            prev_val = hour/70
    try:
        i = np.argmax(np.maximum.accumulate(cum_profits) - cum_profits)
        j = np.argmax(cum_profits[:i])
        drawdown = round(cum_profits[j] - cum_profits[i], 3)
        print("\t%s total drawdown" % drawdown)
    except:
        print("Error calculating drawdown")
    try:
        print("\t%s Sortino" % (round(np.mean(new_profits)/np.std(neg_profits), 3)))
    except:
        print("Error calculating sortino")


plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xlabel("Hour")
plt.ylabel("Profit ($)")
plt.title("GP profit over time")
x1,x2,y1,y2 = plt.axis()

plt.show()