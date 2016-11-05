import re
from datetime import date, timedelta

from data_loading.data_loaders import DataLoader
from data_loading.data_loaders import loader_utils
from data_loading.invariant_file_types import invariant_utils

from data_loading.invariant_file_types import file_invariants
from miso_tables import models


class NPH_HistoricalLoader(DataLoader.DataLoader):

    def get_model_class(self):
        return models.NPH

    def get_priority(self):
        return 2

    def get_accessible_dates(self):
        # MISO provides data from the last n years, up until ~3 days before the present date
        n = 2
        n_years_ago = date.today().year - n
        start_date = date(n_years_ago, 1, 1)
        end_date = date.today() - timedelta(days=3)
        return loader_utils.get_date_range_set_inclusive(start_date, end_date)

    def insert_data_for_date(self, date):
        #if date < date.today() - timedelta(days=3):
        da_data = invariant_utils.getFile(file_invariants.da_invariant, date)
        rt_data = invariant_utils.getFile(file_invariants.rt_invariant, date)
        processed_da = self.process_csv_data(da_data)
        processed_rt = self.process_csv_data(rt_data)
        #else:
        #driver = MisoDriver()
        #da_lmps = driver.get_da_lmps(date)
        #rt_lmps = driver.get_rt_lmps(date)
        #processed_da = self.process_driver_da_rt_data(da_lmps)
        #processed_rt = self.process_driver_da_rt_data(rt_lmps)
        self.insert_processed_da_rt_data(processed_da, processed_rt, date)

    def process_csv_data(self, data):
        lines = data.strip().split('\n')
        csv_header = lines[4]
        assert csv_header.startswith('Node,Type,Value')

        line_regex = r'^(.+?)\,(.+?)\,(.+?)\,(.+?)$'
        lines = lines[5:]

        processed_data = dict()

        for line in lines:
            match = re.match(line_regex, line)
            if not match:
                raise Exception('Line did not match regex.')

            (node_name, node_type, node_value, hourly_data) = match.groups()
            hour_ending_values = [float(x) for x in hourly_data.split(',')]
            # ensure that we are reading all of the HE values for each line.
            assert len(hour_ending_values) == 24

            for hour_ending_m1, hour_ending_value in enumerate(hour_ending_values):
                hour_ending = hour_ending_m1 + 1
                processed_data[(node_name, hour_ending)] = hour_ending_value

        return processed_data

    #def process_driver_da_rt_data(self, data):
    #    processed_data = dict()
    #    for node_name, node_lmps in data.items():
    #        for hour_ending, lmp_value in node_lmps.items():
    #            processed_data[(node_name, int(hour_ending))] = float(lmp_value)
    #    return processed_data

    def insert_processed_da_rt_data(self, processed_da, processed_rt, date):
        # ensure that the data sets match up for nodes / hours.
        assert processed_da.keys() == processed_rt.keys()
        keys = processed_da.keys()
        nphs = []
        for key in keys:
            (node_name, hour_ending) = key
            nph = models.NPH(
                node_name = node_name,
                hour_ending = hour_ending,
                day = date,
                da_value = processed_da[key],
                rt_value = processed_rt[key],
                dart_value = processed_da[key] - processed_rt[key]
            )
            nphs.append(nph)
        models.NPH.objects.bulk_create(nphs)








