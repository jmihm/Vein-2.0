import os
import re
from datetime import date, timedelta

from data_loading.data_loaders import DataLoader
from data_loading.data_loaders import loader_utils
from data_loading.invariant_file_types import invariant_utils

from data_loading.invariant_file_types import file_invariants
from miso_tables import models
from dateutil.parser import parse


class LookAheadLoader(DataLoader.DataLoader):

    def get_model_class(self):
        return models.LookAhead

    def get_priority(self):
        return 2

    def get_accessible_dates(self):
        # MISO provides data from the last n years, up until ~3 days before the present date
        n = 2
        n_years_ago = date.today().year - n
        start_date = date(n_years_ago, 1, 1)
        end_date = date.today() - timedelta(days=10)
        return loader_utils.get_date_range_set_inclusive(start_date, end_date)

    def insert_data_for_date(self, date):
        file_path = invariant_utils.getPersistentFile(file_invariants.look_ahead_invariant, date)
        csv_string = invariant_utils.csv_from_excel(file_path)
        self.process_csv_data(csv_string)
        os.remove(file_path)     # Since this is a .xls file we must clean it up at the end

    def process_csv_data(self, data):
        lines = data.strip().split('\n')
        lines = lines[7:]

        for line in lines[:24]:
            _, date, hour_ending, n_pred, n_actual, c_pred, c_actual, s_pred, s_actual, miso_pred, miso_actual = (x.strip() for x in line.split(","))
            hour_ending = int(float(hour_ending))
            n_pred = float(n_pred)
            n_actual = float(n_actual) if n_actual != "" else None
            c_pred = float(c_pred)
            c_actual = float(c_actual) if c_actual != "" else None
            s_pred = float(s_pred)
            s_actual = float(s_actual) if s_actual != "" else None
            miso_pred = float(miso_pred)
            miso_actual = float(miso_actual) if miso_actual != "" else None
            la = models.LookAhead(
                date = parse(date),
                hour_ending = hour_ending,
                north_pred = n_pred,
                north_actual = n_actual,
                central_pred = c_pred,
                central_actual = c_actual,
                south_pred = s_pred,
                south_actual = s_actual,
                miso_pred = miso_pred,
                miso_actual = miso_actual
            )
            la.save()
        print(date)










