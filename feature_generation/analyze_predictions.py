from datetime import date, timedelta
import json
from drivers.MisoDriver import MisoDriver

MWS = .5
OFFER_PRICE = -10.0
BID_PRICE = 50.0
m = MisoDriver()

def analyze_predictions(predicted_date=date.today() + timedelta(days=1),
                        debug=1):
    with open("./feature_generation/predictions_for_date/%s.json"
            % predicted_date) as f:
        data = json.loads(f.read())
        node_data = data["nodes"]
        for node_name, values in node_data.items():
            node_name = str(node_name)
            predictions, results = values["predictions"], values["results"]
            if debug > 0:
                print_results(node_name, results, data["parameters"]["conf_val"])
            select_predictions(node_name, predictions, predicted_date)
        if len(m.bets) > 0:
            m.submit_offers()



def print_results(node_name, results, conf_val):
    print(node_name)
    for k,v in results.items():
        print("  %s: %s" % (k, v))
    print"conf_val used: %s" % conf_val
    print("")

def select_predictions(node_name, predictions, date):
    print(node_name)
    hours = sorted(predictions.keys(), key=lambda x: int(x[2:]))
    for hour in hours:
        prediction_data = predictions[hour]
        print("  %s:" % hour)
        print("    Raw prediction: %s" % prediction_data["raw_prediction"])
        print("    p_value: %s" % prediction_data["p_value"])
        print("    Upper bound: %s" % prediction_data["upper_val"])
        print("    Lower bound: %s" % prediction_data["lower_val"])
        print("    Sigma: %s" % prediction_data["sigma"])
    add_bet = True
    while add_bet:
        selection = input("Enter the hour of the day you would like to bet or 0"
                          " if you don't want to bet:")
        if not type(selection) == int or "HE%s" % selection not in predictions.keys():
            add_bet = False
            print("Finished adding bets!")
        else:
            hour = int(selection)
            prediction = predictions["HE%s" % hour]
            pred_val = float(prediction["raw_prediction"])
            if pred_val < 0:
                m.add_bet(node_name, date, hour, MWS, BID_PRICE, "Bid")
            else:
                m.add_bet(node_name, date, hour, MWS, OFFER_PRICE, "Offer")


#analyze_predictions()





