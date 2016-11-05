from datetime import timedelta
import pytz

def get_date_range_set_inclusive(start_date, end_date):
    def gen():
        curr_date = start_date
        while curr_date <= end_date:
            yield curr_date
            curr_date = curr_date + timedelta(days = 1)

    return set(list(gen()))



def naive_to_eastern_no_dst(naive_datetime):
    """Adds the eastern timezone to a naive datetime without
    changing the date. EG: if the hour was 3 before it will still be 3
    but no daylight savings time"""
    eastern = pytz.timezone("US/Eastern")
    return eastern.localize(naive_datetime, is_dst=False)


def utc_to_eastern(naive_datetime):
    """Converts a utc datetime to one with the eastern timezone """
    utc = pytz.timezone("UTC")
    eastern = pytz.timezone("US/Eastern")
    utc_dt = utc.localize(naive_datetime)
    eastern_dt = utc_dt.astimezone(eastern)
    return eastern_dt

def eastern_to_utc(naive_datetime):
    """Converts an eastern timezone to a UTC one"""
    utc = pytz.timezone("UTC")
    eastern = pytz.timezone("US/Eastern")
    eastern_dt = eastern.localize(naive_datetime)
    utc_dt = eastern_dt.astimezone(utc)
    return utc_dt