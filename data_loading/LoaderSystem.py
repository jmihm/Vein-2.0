from datetime import date, timedelta

from data_loading.data_loaders import NodeLoader, NPH_HistoricalLoader, BidLoader, \
    LookAheadLoader, NPH_MisoLoader
from miso_tables import models
from data_loading.invariant_file_types.SpecialDates import SpecialDates


class NoAvailableLoader(Exception):
    pass


class LoaderSystem(object):

    def file_loaders(self):
        return [
            #BidLoader.BidLoader(),
            #NodeLoader.NodeLoader(),
            NPH_HistoricalLoader.NPH_HistoricalLoader(),
            NPH_MisoLoader.NPH_MisoLoader(),
            #LookAheadLoader.LookAheadLoader(),
            #WeatherLoader.WeatherLoader(),
        ]

    def get_file_loaders(self):
        loaders = dict()
        for loader in self.file_loaders():
            model_class = loader.get_model_class()
            if model_class in loaders:
                loaders[model_class].append(loader)
            else:
                loaders[model_class] = [loader]

        for loader_list in loaders.values():
            loader_list.sort(key = lambda l: l.get_priority())

        return loaders

    def highest_priority_loader_with_data_for_date(self, model_class, date):
        for loader in self.get_file_loaders()[model_class]:
            if date in loader.get_accessible_dates():
                return loader
        raise NoAvailableLoader("No available loader for model: %s, on date %s." % (model_class, date))

    # Function takes a model and a date and will delete all entries for that given date and model, used so we can
    # clean up old database references
    def clean_data_by_model_and_date(self, loading_date, model_class):
        delete_key = model_class.get_field_for_delete()
        if delete_key:
            delete_objects = model_class.objects.filter(**{delete_key:loading_date})
            if delete_objects.count():
                print("Found existing objects:\n\tAction: Deleting")
            delete_objects.delete()

    def update_data_loading_log(self, loading_date, model_class):
        model_number = model_class.get_model_id()

        # already_in_database will return a number that should be 0, otherwise, delete
        already_in_database = models.DataLoadingLog.objects.filter(
            date_loaded = loading_date,
            model = model_number
        )
        # TODO : John, I think we need to delete the files too. This is just removing the log, we want to kill
        # all entries associated with this part of the log when we delete the log.

        already_in_database.delete()
        entry = models.DataLoadingLog(
            date_loaded = loading_date,
            model = model_number
        )
        entry.save()

    # TODO there should only be one created date for each loaded date. If you try to overwrite data that is already in
    # the database with this method, it should clean out old references.
    # TODO: Chris, potential solution to above issue implemented. Check and confirm it is a good solution
    # todo: (see "clean_data_by_model_and_date" function)
    def insert_date_for_model(self, date, model_class):
        # First delete objects if they already exist for that date
        self.clean_data_by_model_and_date(date, model_class)
        loader = self.highest_priority_loader_with_data_for_date(model_class, date)

        loader.insert_data_for_date(date)
        self.update_data_loading_log(date, model_class)

    def get_all_accessible_dates_for_model_class(self, model_class):
        loaders = self.get_file_loaders()[model_class]
        dates = set([])
        for loader in loaders:
            dates = dates.union(loader.get_accessible_dates())
        return dates

    def get_all_loaded_dates_for_model_class(self, model_class):
        model_number = model_class.get_model_id()
        cursor = models.DataLoadingLog.objects.filter(model = model_number)
        loaded_dates = set([x.date_loaded for x in cursor])
        return loaded_dates

    def insert_accessible_unloaded_dates_for_model_class(self, model_class, earliest_date = SpecialDates.START_OF_TIME):
        accessible_dates = self.get_all_accessible_dates_for_model_class(model_class)
        loaded_dates = self.get_all_loaded_dates_for_model_class(model_class)
        unloaded_accessible_dates = list(accessible_dates - loaded_dates)

        if earliest_date != SpecialDates.START_OF_TIME:
            unloaded_accessible_dates = [d for d in unloaded_accessible_dates if d >= earliest_date]
        unloaded_accessible_dates.sort()
        if date.today() - timedelta(days=1) in accessible_dates:
            # remove half-entered data from yesterday (only really an issue with NPH_MisoLoader
            unloaded_accessible_dates.append(date.today() - timedelta(days=1))
        if date.today() in accessible_dates:
            # Same issue as above, except if we run multiple times on the same day
            unloaded_accessible_dates.append(date.today())

        for unloaded_accessible_date in unloaded_accessible_dates:
            self.insert_date_for_model(unloaded_accessible_date, model_class)



    def insert_accessible_unloaded_dates(self, earliest_date = SpecialDates.START_OF_TIME):
        for model_class in models.supported_models:
            self.insert_accessible_unloaded_dates_for_model_class(model_class, earliest_date)
