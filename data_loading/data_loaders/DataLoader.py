from datetime import date


class DataLoader(object):

    def get_model_class(self):
        raise NotImplemented

    def get_priority(self):
        raise NotImplemented

    def get_accessible_dates(self):
        raise NotImplemented

    def insert_data_for_date(self, date):
        raise NotImplemented


