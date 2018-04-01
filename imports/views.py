from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect

from avdb.models import \
    Convention, \
    Language, \
    Location, \
    LocationType
from .forms import ImportCSVFileForm

import csv
import logging
logger = logging.getLogger(__name__)

# delimiter character for CSV data
csv_delimiter = ';'
csv_quotechar = '"'

# ---------
# LOCATIONS
# ---------

location_columns = ['Location name', 'Address', 'Location type', 'Abbreviation']

def import_locations(request):
    error = None
    imported = []
    failed = []
    if request.method == 'POST':
        form = ImportCSVFileForm(request.POST, request.FILES)
        if form.is_valid():
            error, imported, failed = handle_locations_file(request.FILES['file'])
    else:
        # show blank form
        form = ImportCSVFileForm()

    return render(request, 'imports/import_locations.html', {
        'form': form,
        'error': error,
        'imported': imported,
        'failed': failed
    })

def handle_locations_file(f):
    try:
        reader = get_csv_reader(f)
    except UnicodeDecodeError:
        return ('Invalid CSV file. Make sure CSV is in UTF-8 format.', [], [])

    imported = []
    failed = []

    first_row = True
    for row in reader:
        row = convert_row(row)

        if first_row and not header_row_is_valid(row, location_columns):
            return ('Invalid locations CSV data. Header must be "%s"' % csv_delimiter.join(location_columns), [], [])

        if first_row:
            first_row = False
            continue

        try:
            loc_type = LocationType.objects.get(name=row[2]['val'])
            if loc_type is not None:
                # import location row
                location = Location(
                    name=row[0]['val'],
                    address=row[1]['val'],
                    loc_type=loc_type,
                    abbreviation=row[3]['val'],
                )
                location.save()
                imported.append(location)

        except ObjectDoesNotExist:
            row[2]['error'] = 'Invalid value'
            failed.append(row)

    return (None, imported, failed)

def header_row_is_valid(row, columns):
    """Returns true if given row matches defined columns."""
    if len(row) != len(columns):
        return False

    for i in range(0, len(row)):
        if row[i]['val'] != columns[i]:
            return False

    return True

# -----------
# CONVENTIONS
# -----------

convention_columns = ['Convention name', 'Language', 'Starts', 'Ends', 'Load in', 'Load out', 'Location']

def import_conventions(request):
    error = None
    imported = []
    failed = []
    if request.method == 'POST':
        form = ImportCSVFileForm(request.POST, request.FILES)
        if form.is_valid():
            error, imported, failed = handle_conventions_file(request.FILES['file'])
    else:
        # show blank form
        form = ImportCSVFileForm()

    return render(request, 'imports/import_conventions.html', {
        'form': form,
        'error': error,
        'imported': imported,
        'failed': failed
    })

def handle_conventions_file(f):
    try:
        reader = get_csv_reader(f)
    except UnicodeDecodeError:
        return ('Invalid CSV file. Make sure CSV is in UTF-8 format.', [], [])

    imported = []
    failed = []

    first_row = True
    for row in reader:

        row = convert_row(row)

        if first_row and not header_row_is_valid(row, convention_columns):
            return ('Invalid conventions CSV data. Header must be "%s"' % csv_delimiter.join(convention_columns), [], [])

        if first_row:
            first_row = False
            continue

        error = False

        try:
            language = Language.objects.get(code=row[1]['val'])
        except ObjectDoesNotExist:
            row[1]['error'] = 'Invalid value'
            error = True

        try:
            starts = handle_date(row[2]['val'])
        except TypeError:
            row[2]['error'] = 'Invalid value'
            error = True

        try:
            ends = handle_date(row[3]['val'])
        except TypeError:
            row[3]['error'] = 'Invalid value'
            error = True

        try:
            load_in = handle_datetime(row[4]['val'])
        except TypeError:
            row[4]['error'] = 'Invalid value'
            error = True

        try:
            load_out = handle_datetime(row[5]['val'])
        except TypeError:
            row[5]['error'] = 'Invalid value'
            error = True

        # get location by abbreviation
        location = Location.objects.filter(abbreviation=row[6]['val']).first()
        if location is None:
            row[6]['error'] = 'Invalid value'
            error = True

        if not error:
            # import convention row
            convention = Convention(
                name=row[0]['val'],
                lang=language,
                starts=starts,
                ends=ends,
                load_in=load_in,
                load_out=load_out,
                location=location,
            )
            convention.save()
            imported.append(convention)
        else:
            failed.append(row)

    return (None, imported, failed)


# ----
# UTIL
# ----

def get_csv_reader(f):
    decoded_file = f.read().decode('utf-8').splitlines()
    return csv.reader(decoded_file, delimiter=csv_delimiter, quotechar=csv_quotechar)

def convert_row(values):
    """Converts list of values to list of dicts with error information."""
    row = []
    for val in values:
        row.append({ 'val': val, 'error': None })
    return row

def handle_date(s):
    if s is None:
        raise TypeError('invalid date')
    return s

def handle_datetime(s):
    if s is None:
        raise TypeError('invalid date time')
    return "%s:00" % s
