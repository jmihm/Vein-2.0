from datetime import date

from data_loading.invariant_file_types.InvariantFileType import InvariantFileType
from data_loading.invariant_file_types.InvariantFileType import SpecialDates

da_invariant = InvariantFileType(
    'da_lmp',
    [(SpecialDates.START_OF_TIME, date(2015, 3, 1)), (date(2015, 3, 1), SpecialDates.END_OF_TIME)],
    ['da_lmp.csv', 'da_expost_lmp.csv']
)

rt_invariant = InvariantFileType(
    'rt_lmp',
    [(SpecialDates.START_OF_TIME, SpecialDates.END_OF_TIME)],
    ['rt_lmp_final.csv']
)

bid_invariant = InvariantFileType(
    'bid',
    [(SpecialDates.START_OF_TIME, SpecialDates.END_OF_TIME)],
    ['bids_cb.csv']
)

look_ahead_invariant = InvariantFileType(
    'look_ahead',
    [(SpecialDates.START_OF_TIME, SpecialDates.END_OF_TIME)],
    ['rf_al.xls']
)

