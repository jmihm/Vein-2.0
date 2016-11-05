from datetime import date, timedelta

from data_loading.data_loaders import DataLoader
from data_loading.data_loaders import loader_utils
from drivers.MisoDriver import MisoDriver
from miso_tables import models


class NPH_MisoLoader(DataLoader.DataLoader):

    def get_model_class(self):
        return models.NPH

    def get_priority(self):
        return 1

    def get_accessible_dates(self):
        start_date = date.today() - timedelta(days=3)
        end_date = date.today()
        return loader_utils.get_date_range_set_inclusive(start_date, end_date)

    def insert_data_for_date(self, date):
        driver = MisoDriver()
        da_lmps = driver.get_da_lmps(date)
        rt_lmps = driver.get_rt_lmps(date)
        processed_da = self.process_driver_da_rt_data(da_lmps)
        processed_rt = self.process_driver_da_rt_data(rt_lmps)
        self.insert_processed_da_rt_data(processed_da, processed_rt, date)

    def process_driver_da_rt_data(self, data):
        processed_data = dict()
        for node_name, node_lmps in data.items():
            for hour_ending, lmp_value in node_lmps.items():
                processed_data[(node_name, int(hour_ending))] = float(lmp_value)
        return processed_data

    def insert_processed_da_rt_data(self, processed_da, processed_rt, date_):
        # ensure that the data sets match up for nodes / hours.
        keys = processed_rt.keys()
        print(date_)
        print(date.today())
        if date_ != date.today():
            assert processed_da.keys() == processed_rt.keys()
        else:
            for key in keys:
                assert key in processed_da
        nphs = []
        for key in keys:
            (node_name, hour_ending) = key
            nph = models.NPH(
                node_name = node_name,
                hour_ending = hour_ending,
                day = date_,
                da_value = processed_da[key],
                rt_value = processed_rt[key],
                dart_value = processed_da[key] - processed_rt[key]
            )
            nphs.append(nph)
        models.NPH.objects.bulk_create(nphs)

