import os
import requests
from datetime import date
import xlrd

def getFile(invariant_type, date):
    type_at_date = invariant_type.get_type_at_date(date)
    print(type_at_date)
    base_url = 'https://www.misoenergy.org/Library/Repository/Market%%20Reports/%s_%s'
    date_string = date.strftime('%Y%m%d')
    url = base_url % (date_string, type_at_date)
    print(url)
    data = requests.get(url)
    if data.status_code != 200:
        raise Exception("Unable to load data for invariant type: %s on date %s." % (invariant_type.get_name(), date))
    return data.text


# Used for downloading .xls files, we must persist them and therefore
# they should be deleted by the loader
def getPersistentFile(invariant_type, date):
    type_at_date = invariant_type.get_type_at_date(date)
    base_url = 'https://www.misoenergy.org/Library/Repository/Market%%20Reports/%s_%s'
    date_string = date.strftime('%Y%m%d')
    url = base_url % (date_string, type_at_date)
    result = requests.get(url, stream=True)
    name = url.split("/")[-1]
    with open("./data_loading/files/%s" % name, 'wb') as f:
        for chunk in result.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
        path = f.name
    return path

# Gets rid of a lot of headaches by just converting .xls files to .csv
def csv_from_excel(file_path):
    wb = xlrd.open_workbook(file_path)
    sh = wb.sheet_by_index(0)
    text = ""
    for rownum in range(sh.nrows):
        text += "\n%s" % sh.row_values(rownum)
    return text.replace("'", "").replace("[", "").replace("]", "").strip()


#from data_loading.invariant_file_types.file_invariants import look_ahead_invariant

#file_name = getPersistantFile(look_ahead_invariant, date(year=2014, day=1, month=1))
#print(csv_from_excel(file_name))


