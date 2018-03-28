from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect

from avdb.models import Location, \
    LocationType
from .forms import ImportCSVTextForm, ImportLocationsCSVForm

import csv
import logging
logger = logging.getLogger(__name__)

# delimiter character for CSV data
csv_delimiter = ';'
csv_quotechar = '"'

def import_csv_form(request):
    if request.method == 'POST':
        form = ImportCSVTextForm(request.POST)
        if form.is_valid():
            # do something
            return HttpResponseRedirect('/imported')
    else:
        # show blank form
        form = ImportCSVTextForm()

    return render(request, 'imports/import_csv_form.html', { 'form': form })


def import_locations(request):
    error = None
    imported = []
    failed = []
    if request.method == 'POST':
        form = ImportLocationsCSVForm(request.POST, request.FILES)
        if form.is_valid():
            error, imported, failed = handle_uploaded_locations_file(request.FILES['file'])
    else:
        # show blank form
        form = ImportLocationsCSVForm()

    return render(request, 'imports/import_locations.html', {
        'form': form,
        'error': error,
        'imported': imported,
        'failed': failed
    })

def handle_uploaded_locations_file(f):
    logger.error('READING WHOLE UPLOADED FILE')

    try:
        decoded_file = f.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file, delimiter=csv_delimiter, quotechar=csv_quotechar)
    except UnicodeDecodeError:
        return ('Invalid CSV file. Make sure CSV is in UTF-8 format.', [], [])

    imported_locations = []
    failed_rows = []

    first_row = True
    for row in reader:
        #logger.error(', '.join(row))
        # validate csv data, check header row
        if first_row and (len(row) != 4 or row[0] != 'Location name' or row[1] != 'Address' or row[2] != 'Location type' or row[3] != 'Abbreviation'):
            return ('Invalid locations CSV data. Header should be "Location name;Address;Location type;Abbreviation"', [], [])

        if first_row:
            first_row = False
            continue

        try:
            loc_type = LocationType.objects.get(name=row[2])
            if loc_type is not None:
                # import location row
                location = Location(
                    name=row[0],
                    address=row[1],
                    loc_type=loc_type,
                    abbreviation=row[3],
                )
                location.save()
                imported_locations.append(location)

        except ObjectDoesNotExist:
            failed_rows.append(row)

    return (None, imported_locations, failed_rows)
