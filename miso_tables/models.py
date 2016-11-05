from __future__ import unicode_literals

from django.db import models

class Node(models.Model):

    name = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=1)
    deprecated = models.BooleanField()
    created = models.DateField(auto_now_add=True)
    include_weather = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)

    @classmethod
    def get_field_for_delete(self):
        return False    # False implies we don't need to delete these

    @classmethod
    def get_model_id(cls):
        return 1

class NPH(models.Model):

    node_name = models.CharField(max_length=255, db_index=True)
    hour_ending = models.SmallIntegerField(db_index=True)
    day = models.DateField(db_index=True)
    rt_value = models.FloatField()
    da_value = models.FloatField()
    dart_value = models.FloatField()
    created = models.DateField(auto_now_add=True)

    @classmethod
    def get_field_for_delete(self):
        return "day"

    @classmethod
    def get_model_id(cls):
        return 2

class Bid(models.Model):

    participant_id = models.IntegerField(db_index=True)
    bid_id = models.IntegerField()
    type_of_bid = models.CharField(max_length=1)
    mw = models.FloatField()
    lmp = models.FloatField()
    date = models.DateField(db_index=True)
    hour_ending = models.SmallIntegerField()
    func_price_1 = models.FloatField(null=True)
    func_mw_1 = models.FloatField(null=True)
    func_price_2 = models.FloatField(null=True)
    func_mw_2 = models.FloatField(null=True)
    func_price_3 = models.FloatField(null=True)
    func_mw_3 = models.FloatField(null=True)
    func_price_4 = models.FloatField(null=True)
    func_mw_4 = models.FloatField(null=True)
    func_price_5 = models.FloatField(null=True)
    func_mw_5 = models.FloatField(null=True)
    func_price_6 = models.FloatField(null=True)
    func_mw_6 = models.FloatField(null=True)
    func_price_7 = models.FloatField(null=True)
    func_mw_7 = models.FloatField(null=True)
    func_price_8 = models.FloatField(null=True)
    func_mw_8 = models.FloatField(null=True)
    func_price_9 = models.FloatField(null=True)
    func_mw_9 = models.FloatField(null=True)
    created = models.DateField(auto_now_add=True)

    @classmethod
    def get_field_for_delete(cls):
        return "date"

    @classmethod
    def get_model_id(cls):
        return 3


class LookAhead(models.Model):
    date = models.DateField()
    hour_ending = models.IntegerField()

    north_pred = models.FloatField()
    north_actual = models.FloatField(null=True, blank=True)

    central_pred = models.FloatField()
    central_actual = models.FloatField(null=True, blank=True)

    south_pred = models.FloatField()
    south_actual = models.FloatField(null=True, blank=True)

    miso_pred = models.FloatField()
    miso_actual = models.FloatField(null=True, blank=True)

    @classmethod
    def get_field_for_delete(cls):
        return "date"

    @classmethod
    def get_model_id(cls):
        return 4


class WeatherForecast(models.Model):
    # The datetime when the prediction was made
    prediction_made_dt = models.DateTimeField()
    # The hour of the prediction
    predicted_hour = models.IntegerField()
    # The date of the prediction
    predicted_date = models.DateField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    cloud_cover = models.FloatField()
    apparent_temp = models.FloatField()
    pressure = models.FloatField()
    visibility = models.FloatField()
    summary = models.CharField(max_length=56)
    temperature = models.FloatField()
    dew_point = models.FloatField()
    humidity = models.FloatField()
    ozone = models.FloatField()
    wind_speed = models.FloatField()
    wind_bearing = models.FloatField()
    precip_intensity = models.FloatField()
    precip_probability = models.FloatField()

    @classmethod
    def get_field_for_delete(cls):
        return "prediction_made_dt"

    @classmethod
    def get_model_id(cls):
        return 5

supported_models = [NPH]

#supported_models = [WeatherForecast]

model_choices = [(x.get_model_id(), x) for x in supported_models]

# Assertion enforces that each model has a unique ID
assert len([x[0] for x in model_choices]) == len(set([x[0] for x in model_choices]))

class DataLoadingLog(models.Model):

    created = models.DateField(auto_now_add=True)
    date_loaded = models.DateField()
    model = models.CharField(max_length=3, choices=model_choices)
