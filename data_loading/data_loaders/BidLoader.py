from datetime import date, timedelta, datetime

from data_loading.data_loaders import DataLoader
from data_loading.data_loaders import loader_utils
from data_loading.invariant_file_types import invariant_utils

from data_loading.invariant_file_types import file_invariants
from miso_tables import models


class BidLoader(DataLoader.DataLoader):

    def get_model_class(self):
        return models.Bid

    def get_priority(self):
        return 2

    def get_accessible_dates(self):
        two_years_ago = date.today().year - 2
        start_date = date(two_years_ago, 1, 1)
        end_date = date.today() - timedelta(days=95)
        return loader_utils.get_date_range_set_inclusive(start_date, end_date)

    def insert_data_for_date(self, date):
        bid_data = invariant_utils.getFile(file_invariants.bid_invariant, date)
        headers, entries = self.process_bid_data(bid_data)
        bids = []
        for entry in entries:

            end_datetime = datetime.strptime(entry[headers['Date/Time End (EST)']], '%m/%d/%Y %H:%M:%S')

            handle_bid_price = lambda x: float(x) if x.replace('.', '').isdigit() else None

            bid = models.Bid(
                participant_id = int(entry[headers['Market Participant Code']]),
                bid_id = int(entry[headers['Bid ID']]),
                type_of_bid = entry[headers['Type of Bid']],
                mw = float(entry[headers['MW']]),
                lmp = float(entry[headers['LMP']]),
                date = end_datetime.date(),
                hour_ending = end_datetime.hour,

                # Finish loading step functions. Need to figure out how to handle the case that these fields are not
                # specified.
                func_price_1 = handle_bid_price(entry[headers['PRICE1']]),
                func_mw_1 = handle_bid_price(entry[headers['MW1']]),
                func_price_2 = handle_bid_price(entry[headers['PRICE2']]),
                func_mw_2 = handle_bid_price(entry[headers['MW2']]),
                func_price_3 = handle_bid_price(entry[headers['PRICE3']]),
                func_mw_3 = handle_bid_price(entry[headers['MW3']]),
                func_price_4 = handle_bid_price(entry[headers['PRICE4']]),
                func_mw_4 = handle_bid_price(entry[headers['MW4']]),
                func_price_5 = handle_bid_price(entry[headers['PRICE5']]),
                func_mw_5 = handle_bid_price(entry[headers['MW5']]),
                func_price_6 = handle_bid_price(entry[headers['PRICE6']]),
                func_mw_6 = handle_bid_price(entry[headers['MW6']]),
                func_price_7 = handle_bid_price(entry[headers['PRICE7']]),
                func_mw_7 = handle_bid_price(entry[headers['MW7']]),
                func_price_8 = handle_bid_price(entry[headers['PRICE8']]),
                func_mw_8 = handle_bid_price(entry[headers['MW8']]),
                func_price_9 = handle_bid_price(entry[headers['PRICE9']]),
                func_mw_9 = handle_bid_price(entry[headers['MW9']])
            )
            bids.append(bid)
        models.Bid.objects.bulk_create(bids)

    def process_bid_data(self, bid_data):
        lines = bid_data.strip().split('\r\n')
        header_line = lines[0]
        # make sure that the header is well-formatted
        assert header_line.startswith('Region,Market')
        header_names = header_line.split(',')
        headers = dict()
        for i, header_name in enumerate(header_names):
            headers[header_name] = i
        lines = lines[1:]
        entries = [line.split(',') for line in lines]
        return headers, entries

