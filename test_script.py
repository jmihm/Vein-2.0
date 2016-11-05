from miso_tables import models
from data_loading import LoaderSystem
from datetime import date, datetime
from feature_generation import generate_data, select_nodes, analyze_predictions

node_names = ["EES.SABINE1", "WEC.AZ", "SME.BENN_GT"]

common_conf_vals = {
    "40%": .26,
    "50%": .674,
    "60%": .842,
    "70%": 1.04,
    "80%": 1.28,
    "90%": 1.645
}
train_size = .8         # percent of the data to use when training the model
conf = common_conf_vals["50%"]
max_predict_hour = 10   # latest hour in the day to predict on


#ls = LoaderSystem.LoaderSystem()
#ls.insert_accessible_unloaded_dates()

for node_name in node_names:
    generate_data.generate_data(node_name)
    select_nodes.train_gps(train_size, conf, max_predict_hour)

# This function will output the results and predictions and allow a user to
# select nodes to bet on
analyze_predictions.analyze_predictions()




#ls.insert_date_for_model(d, models.NPH)



#from daemon import CeleryBeatDaemon, CeleryWorkerDaemon
#import time
#beat = CeleryBeatDaemon.CeleryBeatDaemon()
#worker = CeleryWorkerDaemon.CeleryWorkerDaemon()

#beat.restart(['-A', 'celery_tasks'])
#worker.restart(['-A', 'celery_tasks'])

#beat.stop()
#worker.stop()
