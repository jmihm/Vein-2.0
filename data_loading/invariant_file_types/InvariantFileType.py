from datetime import date
from data_loading.invariant_file_types.SpecialDates import SpecialDates


class InvariantFileType(object):

    def __init__(self, name, date_pairs, internal_names):
        assert len(date_pairs) == len(internal_names) and len(date_pairs) > 0
        self.name = name
        self.date_pairs = date_pairs
        self.internal_names = internal_names
        self.assert_date_range_is_complete()

    def get_name(self):
        return self.name

    def assert_date_range_is_complete(self):
        if self.date_pairs[0][0] != SpecialDates.START_OF_TIME:
            raise Exception("Date range doesnt start at the beginning of time.")
        if self.date_pairs[-1][1] != SpecialDates.END_OF_TIME:
            raise Exception("Date range doesnt end at the end of time.")

        last_end_date = SpecialDates.START_OF_TIME
        for (start_date, end_date) in self.date_pairs:
            if start_date != last_end_date:
                raise Exception("Date range has holes in it.")
            last_end_date = end_date

    def is_date_in_range(self, date, start_date, end_date):
        if start_date == SpecialDates.START_OF_TIME and end_date == SpecialDates.END_OF_TIME:
            return True
        elif start_date == SpecialDates.START_OF_TIME:
            return date < end_date
        elif end_date == SpecialDates.END_OF_TIME:
            return date >= start_date
        else:
            return start_date <= date < end_date    # Bug fixed here where it was <= end_date when it should just be less than;

    def get_type_at_date(self, date):
        for ((start_date, end_date), internal_name) in zip(self.date_pairs, self.internal_names):
            print(internal_name, date, start_date, end_date)
            if self.is_date_in_range(date, start_date, end_date):
                return internal_name