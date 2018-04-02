from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect

from avdb.models import \
    ContactPerson, \
    Convention, \
    Equipment, \
    EquipmentType, \
    Language, \
    Location, \
    LocationType, \
    Unit, \
    UnitType
from .forms import ImportCSVFileForm

import csv
from decimal import Decimal
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


# ---------------
# CONTACT PERSONS
# ---------------

contact_person_columns = ['Contact name', 'Phone', 'Email', 'Convention']

def import_contact_persons(request):
    error = None
    imported = []
    failed = []
    if request.method == 'POST':
        form = ImportCSVFileForm(request.POST, request.FILES)
        if form.is_valid():
            error, imported, failed = handle_contact_persons_file(request.FILES['file'])
    else:
        # show blank form
        form = ImportCSVFileForm()

    return render(request, 'imports/import_contact_persons.html', {
        'form': form,
        'error': error,
        'imported': imported,
        'failed': failed
    })

def handle_contact_persons_file(f):
    try:
        reader = get_csv_reader(f)
    except UnicodeDecodeError:
        return ('Invalid CSV file. Make sure CSV is in UTF-8 format.', [], [])

    imported = []
    failed = []

    first_row = True
    for row in reader:

        row = convert_row(row)

        if first_row and not header_row_is_valid(row, contact_person_columns):
            return ('Invalid conventions CSV data. Header must be "%s"' % csv_delimiter.join(contact_person_columns), [], [])

        if first_row:
            first_row = False
            continue

        error = False

        convention = Convention.objects.filter(name=row[3]['val']).first()
        if convention is None:
            row[3]['error'] = 'Invalid value'
            error = True

        if not error:
            # import convention row
            person = ContactPerson(
                name=row[0]['val'],
                phone=row[1]['val'],
                email=row[2]['val'],
                convention=convention,
            )
            person.save()
            imported.append(person)
        else:
            failed.append(row)

    return (None, imported, failed)


# ----------
# EQUIPMENTS
# ----------

equipment_columns = ['Equipment name', 'Type', 'Footprint', 'Pallet space', 'Gross weight']

def import_equipments(request):
    error = None
    imported = []
    failed = []
    if request.method == 'POST':
        form = ImportCSVFileForm(request.POST, request.FILES)
        if form.is_valid():
            error, imported, failed = handle_equipments_file(request.FILES['file'])
    else:
        # show blank form
        form = ImportCSVFileForm()

    return render(request, 'imports/import_equipments.html', {
        'form': form,
        'error': error,
        'imported': imported,
        'failed': failed
    })

def handle_equipments_file(f):
    try:
        reader = get_csv_reader(f)
    except UnicodeDecodeError:
        return ('Invalid CSV file. Make sure CSV is in UTF-8 format.', [], [])

    imported = []
    failed = []

    first_row = True
    for row in reader:

        row = convert_row(row)

        if first_row and not header_row_is_valid(row, equipment_columns):
            return ('Invalid conventions CSV data. Header must be "%s"' % csv_delimiter.join(equipment_columns), [], [])

        if first_row:
            first_row = False
            continue

        error = False

        try:
            equipment_type = EquipmentType.objects.get(name=row[1]['val'])
        except ObjectDoesNotExist:
            row[1]['error'] = 'Invalid value'
            error = True

        if not error:
            # import equipment row
            equipment = Equipment(
                name=row[0]['val'],
                equipment_type=equipment_type,
                footprint=row[2]['val'],
                pallet_space=row[3]['val'],
                gross_weight=row[4]['val'],
            )
            equipment.save()
            imported.append(equipment)
        else:
            failed.append(row)

    return (None, imported, failed)

# -----
# UNITS
# -----

unit_columns = ['Unit name', 'Equipment', 'Footprint', 'Pallet space', 'Type', 'Dead weight', 'Net weight', 'Gross weight', 'Width', 'Height', 'Depth', 'Built in items', 'Included in']

def import_units(request):
    error = None
    imported = []
    failed = []
    if request.method == 'POST':
        form = ImportCSVFileForm(request.POST, request.FILES)
        if form.is_valid():
            error, imported, failed = handle_units_file(request.FILES['file'])
    else:
        # show blank form
        form = ImportCSVFileForm()

    return render(request, 'imports/import_units.html', {
        'form': form,
        'error': error,
        'imported': imported,
        'failed': failed
    })

def handle_units_file(f):
    try:
        reader = get_csv_reader(f)
    except UnicodeDecodeError:
        return ('Invalid CSV file. Make sure CSV is in UTF-8 format.', [], [])

    imported = []
    failed = []

    first_row = True
    for row in reader:

        row = convert_row(row)

        if first_row and not header_row_is_valid(row, unit_columns):
            return ('Invalid conventions CSV data. Header must be "%s"' % csv_delimiter.join(unit_columns), [], [])

        if first_row:
            first_row = False
            continue

        error = False

        equipment = Equipment.objects.filter(name=row[1]['val']).first()
        if equipment is None:
            row[1]['error'] = 'Invalid value'
            error = True

        try:
            footprint = None
            if row[2]['val'] != '':
                footprint = Decimal(row[2]['val'])
        except InvalidOperation:
            row[2]['error'] = 'Invalid value'
            error = True

        try:
            pallet_space = None
            if row[3]['val'] != '':
                pallet_space = Decimal(row[3]['val'])
        except InvalidOperation:
            row[3]['error'] = 'Invalid value'
            error = True

        try:
            dead_weight = None
            if row[5]['val'] != '':
                dead_weight = int(row[5]['val'])
        except ValueError:
            row[5]['error'] = 'Invalid value'
            error = True

        try:
            net_weight = None
            if row[6]['val'] != '':
                net_weight = int(row[6]['val'])
        except ValueError:
            row[6]['error'] = 'Invalid value'
            error = True

        try:
            gross_weight = None
            if row[7]['val'] != '':
                gross_weight = int(row[7]['val'])
        except ValueError:
            row[7]['error'] = 'Invalid value'
            error = True

        try:
            width = None
            if row[8]['val'] != '':
                width = int(row[8]['val'])
        except ValueError:
            row[8]['error'] = 'Invalid value'
            error = True

        try:
            height = None
            if row[9]['val'] != '':
                height = int(row[9]['val'])
        except ValueError:
            row[9]['error'] = 'Invalid value'
            error = True

        try:
            depth = None
            if row[10]['val'] != '':
                depth = int(row[10]['val'])
        except ValueError:
            row[10]['error'] = 'Invalid value'
            error = True

        try:
            unit_type = UnitType.objects.get(name=row[4]['val'])
        except ObjectDoesNotExist:
            row[4]['error'] = 'Invalid value'
            error = True

        try:
            included_in = None
            if row[12]['val'] != '':
                included_in = Unit.objects.get(name=row[12]['val'])
        except ObjectDoesNotExist:
            row[12]['error'] = 'Invalid value'
            error = True

        if not error:
            # import unit row
            unit = Unit(
                name=row[0]['val'],
                equipment=equipment,
                footprint=footprint,
                pallet_space=pallet_space,
                unit_type=unit_type,
                dead_weight=dead_weight,
                net_weight=net_weight,
                gross_weight=gross_weight,
                width=width,
                height=height,
                depth=depth,
                built_in_items=row[11]['val'],
                included_in=included_in,
            )
            unit.save()
            imported.append(unit)
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
