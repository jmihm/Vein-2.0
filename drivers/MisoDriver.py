import requests
from datetime import date, datetime, timedelta
import xmltodict
from dateutil.parser import parse
import time

cert_file_path = "./drivers/cert.pem"
key_file_path = "./drivers/key.pem"
headers = {'Content-Type': 'text/xml'}

cert = (cert_file_path, key_file_path)

xml_template = """<?xml version="1.0"?>
    <env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
    <env:Header/>
    <env:Body>
    %s
    </env:Body>
    </env:Envelope>
    """

def write_info(s):
    with open("./logs/miso.log", 'a') as f:
        f.write("%s\n" %str(s))
        f.write("------------------------------------------------\n\n")


class MisoDriver():

    def __init__(self):
        self.cert = cert
        self.bets = []
        self.query = ""


    def make_request(self, request):
        xml = xml_template % request
        r = requests.post("https://markets.midwestiso.org/darteor/xml/query",
                          cert=self.cert, data=xml, headers=headers, stream=True)
        return r.text


    def get_lmps(self, query_key, date, nodes=None):
        xml = """<QueryRequest xmlns="http://markets.midwestiso.org/dart/xml">
         <Query%s day="%s">
         <All/>
         </Query%s>
         </QueryRequest>
        """ % (query_key[0], str(date), query_key[0])

        text = self.make_request(xml)
        if "PG-EXCESSIVEREQUESTS" in text:
            print("Too many requests!")
            time.sleep(30)
            text = self.make_request(xml)

        d = xmltodict.parse(text)
        ret_nodes = dict()
        try:
            for node in d["Envelope"]["Body"]["QueryResponse"][query_key[0]][query_key[1]]:
                node_name = node["@location"]
                if nodes is not None and node_name not in nodes:
                    continue
                hours = dict()
                for data in node[query_key[2]]:
                    hours[data["@hour"]] = data["LMP"]
                ret_nodes[node_name] = hours
        except BaseException as e:
            print("Error:", e)
            return
        return ret_nodes

    def get_rt_lmps(self, date, nodes=None):
        rt_query = ("RealTimeIntegratedLMP", "IntPricingNode", "IntPricingNodeHourly")
        return self.get_lmps(rt_query, date, nodes)


    def get_da_lmps(self, date, nodes=None):
        da_query = ("DayAheadLMP", "PricingNode", "PricingNodeHourly")
        return self.get_lmps(da_query, date, nodes)


    def get_node_results(self, hours, nodes, offset=0):
        da_lmps = self.get_da_lmps(date.today() - timedelta(days=offset), nodes)
        rt_lmps = self.get_rt_lmps(date.today() - timedelta(days=offset), nodes)
        results = dict()
        for node in nodes:
            if not node["node_name"] in results:
                results[node["node_name"]] = {}
            for hour in hours:
                da_val = da_lmps[node][str(hour)]
                rt_val = rt_lmps[node][str(hour)]
                results[node][hour] = float(da_val) - float(rt_val)
                results[node]["da_val"] = da_val
                results[node]["rt_val"] = rt_val
        return results


    def get_bet_results(self, bets):
        da_lmps = self.get_da_lmps(bets[0]["date"], [x["node_name"] for x in bets])
        rt_lmps = None
        if parse(bets[0]["date"]).date() <= date.today():
            rt_lmps = self.get_rt_lmps(bets[0]["date"], [x["node_name"] for x in bets])
        results = []
        for bet in bets:
            da_val = da_lmps[bet["node_name"]][str(bet["hour"])]
            bet["da_val"] = da_val
            bet["date"] = bet["date"]
            if rt_lmps is not None:
                rt_val = rt_lmps[bet["node_name"]][str(bet["hour"])]
                diff = float(da_val) - float(rt_val)
                bet["rt_val"] = rt_val
                bet["diff"] = diff
            results.append(bet)
        return results


    def get_locational_results(self, locations):
        xml = "<QueryRequest>"
        for location, date in locations:
            xml += """<QueryDayAheadLMP day="%s">
                 <LocationName>%s</LocationName>
                 </QueryDayAheadLMP>""" % (date, location)
        for location, date in locations:
            xml += """<QueryRealTimeIntegratedLMP day="%s">
                 <LocationName>%s</LocationName>
                 </QueryRealTimeIntegratedLMP>""" % (date, location)
        xml += "</QueryRequest> "
        self.query += xml


    def submit_offers(self):
        print("Submitting the following offers:")
        for bet in self.bets:
            print("\t", bet)
        sure = raw_input("Would you like to continue? (Y/N):")
        if sure != "Y":
            print("Not submitting\nClearing bets...")
            self.bets = []
            return
        xml = '<SubmitRequest xmlns="http://markets.midwestiso.org/dart/xml">\n'
        for bet in self.bets:
            xml += """<%s day="%s">
                <Block location="%s">
                    <BlockHourly hour="%s">
                        <BlockSegment MW="%s" price="%s"/>
                    </BlockHourly>
                </Block>
            </%s>\n""" % (bet["type"], bet["date"], bet["node_name"], bet["hour"], bet["mws"], bet["price"],
                          bet["type"])
        xml += '</SubmitRequest>'
        response = self.make_request(xml)
        print(response)
        if "Success" in response:
            print("Successfully submitted bets!")
            self.bets = []
        else:
            print("Unsuccessful response")
            print(response)


    def submit_offers_ui(self):
        print("Submitting the following offers:")
        for bet in self.bets:
            print("\t", bet)
        xml = '<SubmitRequest xmlns="http://markets.midwestiso.org/dart/xml">\n'
        for bet in self.bets:
            xml += """<%s day="%s">
                <Block location="%s">
                    <BlockHourly hour="%s">
                        <BlockSegment MW="%s" price="%s"/>
                    </BlockHourly>
                </Block>
            </%s>\n""" % (bet["type"], bet["date"], bet["node_name"], bet["hour"], bet["mws"], bet["price"],
                          bet["type"])
        xml += '</SubmitRequest>'
        response = self.make_request(xml)
        if "Success" in response:
            self.bets = []
            successful = True
        else:
            self.bets = []
            raise BaseException(response)
        return successful


    def add_offer(self, node, date, hour, mws, price):
        assert type(hour) == int and type(mws) == float and type(price) == float and type(node) == str
        offer = {"node_name": str(node.upper()),
                 "date": str(date),
                 "hour": int(hour),
                 "mws": round(mws, 1),
                 "price": "%.2f" % price,
                 "type": "VirtualOffer"
                 }
        self.bets.append(offer)
        print("Added offer:", offer)
        print("Note: Offers not submitted until submission function called.")


    def add_bid(self, node, date, hour, mws, price):
        assert type(hour) == int and type(mws) == float and type(price) == float and type(node) == str
        offer = {"node_name": str(node.upper()),
                 "date": str(date),
                 "hour": int(hour),
                 "mws": round(mws, 1),
                 "price": "%.2f" % price,
                 "type": "VirtualBid"
                 }
        self.bets.append(offer)
        print("Added bid:", offer)
        print("Note: Bids not submitted until submission function called.")


    def add_bet(self, node, date, hour, mws, price, type):
        if type == "Offer":
            self.add_offer(node, date, hour, mws, price)
        elif type == "Bid":
            self.add_bid(node, date, hour, mws, price)
        else:
            print("Invalid input.")

def printBets(bets):
    print("Displaying bets:")
    for bet in bets:
        print("%s) %s %s %s, mws: %s" %(bet["node_id"], bet["node_name"], bet["date"], bet["hour"], bet["mws"]))
        print("\tda_val: %s, rt_val: %s, diff: %s, profit: %s\n" %(bet["da_val"], bet["rt_val"], bet["diff"], bet["profit"]))





## DEPRECATED CODE BELOW
## KEEP FOR XML EXAMPLES
##
##
"""
sample_xml  = <QueryRequest>
 <QueryMarketResults day="2015-04-20">
 <LocationName>TVA.WHITEOAK</LocationName>
 </QueryMarketResults>
</QueryRequest>


data = {"locationName": "EAI.INDEPEND2",
        "day":"2015-04-21",
        "org.apache.struts.taglib.html.TOKEN": "84d4efbcaf285999f8bf24ebd448e7cc",
        "portfolioName": "other"}
#headers = {'Content-Type': 'text/html'}
"""
#r = requests.get("https://markets.midwestiso.org/MISO/", cert=cert, headers=headers)
#print r.text
#
#from utilities import create_browser

#br = create_browser()
#br.add_client_certificate("https://markets.midwestiso.org/MISO/", key_file_path, cert_file_path)
#r = br.open("https://markets.midwestiso.org/MISO/")
#print r.read()
#d = MisoDriver()
#response = d.make_request(sample_xml)
#print response
#print "Beginning within MISO driver!!..."
#driver = MisoDriver()
#driver.add_to_portfolio()
#results = driver.get_all_bet_results()
#printBets(results)
#nodes = ['WPS.COLUMBIA2', 'WEC.GLACRHLS', 'CLEC.HUNTER3']
#vals = driver.get_bet_results([1], nodes, 0)
#print vals
#rt_lmps = driver.get_rt_lmps(date(month=3, year=2015, day=24))
#print rt_lmps


#def add_to_portfolio(self):
#    xml = """<SubmitRequest><Portfolios>
#    <Portfolio name="042815" action="AddTo">"""
#    for bet in list(db.bets.find())[-2:-1]:
#        xml += "<LocationName>" \
#               "%s" \
#               "</LocationName>\n" % bet["node_name"]
#    xml += """</Portfolio>
#           </Portfolios>
#           </SubmitRequest>"""
#    print(xml)
#    print(self.make_request(xml))


#def get_all_bet_results(self):
#    print("Gathering bet results...")
#    locations = []
#    for bet in db.bets.find():
#        if bet["rt_lmp"] is not None:
#            continue
#        locations.append((bet["node_name"], bet["date"]))
#    self.get_locational_results(locations)
#    results = self.make_request(self.query)
#    if "Error" in results:
#        print("Error:", results)
#        return
#    print(self.query)
#    d = xmltodict.parse(results)
#    d = d["Envelope"]["Body"]["QueryResponse"]
#    for item in d["RealTimeIntegratedLMP"]:
#        day = item["@day"]
#         if not "IntPricingNode" in item.keys(): continue
#         node_name = item["IntPricingNode"]["@location"]
#         bets = db.bets.find({"date": day, "node_name": node_name})
#         assert bets.count() == 1
#         bet = bets[0]
#         hour = bet["hour"]
#         for hour_data in item["IntPricingNode"]["IntPricingNodeHourly"]:
#             if type(hour_data) == unicode: continue
#             if str(hour_data["@hour"]) == str(hour):
#                 rt_lmp = hour_data["LMP"]
#                 bet["rt_lmp"] = float(rt_lmp)
#                 db.bets.update({"_id": bet["_id"]}, bet)
#     for item in d["DayAheadLMP"]:
#         day = item["@day"]
#         node_name = item["PricingNode"]["@location"]
#         bets = db.bets.find({"date": day, "node_name": node_name})
#         assert bets.count() == 1
#         bet = bets[0]
#         hour = bet["hour"]
#         for hour_data in item["PricingNode"]["PricingNodeHourly"]:
#             if str(hour_data["@hour"]) == str(hour):
#                 print("Adding da_lmp...")
#                 da_lmp = hour_data["LMP"]
#                 bet["da_lmp"] = float(da_lmp)
#                 if bet["rt_lmp"] is not None:
#                     bet["diff"] = bet["da_lmp"] - bet["rt_lmp"]
#                     print("Results:", bet["node_name"], bet["bet_type"], bet["diff"])
#                 db.bets.update({"_id": bet["_id"]}, bet)
"""
def get_bet_queryset_results(self, queryset, force=False):
    print "Gathering bet results..."

    hours = [x.hour for x in queryset]
    assert len(set(hours)) == 1
    hour = hours[0]
    locations = [(x.node_name, x.operating_date) for x in queryset]
    self.get_locational_results(locations)
    results = self.make_request(self.query)
    query = self.query
    if "Error" in results:
        print "Error:", results
        assert False
    #print self.query
    d = xmltodict.parse(results)
    d = d["Envelope"]["Body"]["QueryResponse"]
    rt_vals = d["RealTimeIntegratedLMP"]
    if not type(rt_vals) is list:
        rt_vals = [rt_vals]
    print"---------------"
    print "RT Vals"
    print rt_vals
    for item in rt_vals:
        print "Item found!"
        if type(item) is unicode or not "IntPricingNode" in item.keys():
            print "Unicode error..skipping"
            continue
        day = item["@day"]
        node_name = item["IntPricingNode"]["@location"]
        bets = Bet.objects.filter(operating_date=day, node_name=node_name, hour=hour)
        assert bets.count() == 1
        bet = bets[0]
        data = item["IntPricingNode"]["IntPricingNodeHourly"]

        # Case where data is a single result
        if "@hour" in data:
            if str(data["@hour"]) == str(hour):
                rt_lmp = data["LMP"]
                bet.rt_lmp = float(rt_lmp)
                bet.save()
        # Case where data is a list
        else:
            for hour_data in data:
                if type(hour_data) == unicode:
                    print "Unicode error 2, skipping"
                    continue
                if str(hour_data["@hour"]) == str(hour):
                    print "Updating bets!"
                    rt_lmp = hour_data["LMP"]
                    bet.rt_lmp = float(rt_lmp)
                    bet.save()
    da_vals = d["DayAheadLMP"]
    if not type(da_vals) is list:
        da_vals = [da_vals]
    for item in da_vals:
        day = item["@day"]
        node_name = item["PricingNode"]["@location"]
        bets = Bet.objects.filter(operating_date=day, node_name=node_name, hour=hour)
        assert bets.count() == 1
        bet = bets[0]
        for hour_data in item["PricingNode"]["PricingNodeHourly"]:
            if str(hour_data["@hour"]) == str(hour):
                da_lmp = hour_data["LMP"]
                bet.da_lmp = float(da_lmp)
                if bet.rt_lmp != 0:
                    bet.diff = float(bet.da_lmp) - float(bet.rt_lmp)
                    #print "Results:", bet["node_name"], bet["bet_type"], bet["diff"]
                bet.save()
    self.query = ""
    return results
    """
"""
def store_bets(self):
   bulk_insert = []
   for bet in self.bets:
       node_ids = db.nodes.find({"name":bet["node_name"]})
       assert node_ids.count() == 1
       node_id = node_ids[0]["id"]
       bet["node_id"] = node_id
       bet["da_lmp"] = bet["rt_lmp"] = bet["diff"] = bet["profit"] = None
       bet["created"] = datetime.now()
       bulk_insert.append(bet)
   if bulk_insert:
       db.bets.insert(bulk_insert)
       print("Bets inserted into the database successfully!")
"""

"""
   def update_todays_results(self, offset=0):
       bets = list(db.bets.find({"date": str(date.today())}))
       results = self.get_bet_results(bets)
       for bet in results:
           db.bets.update({"_id": bet["_id"]}, bet)
       return results
   """