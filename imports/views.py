from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect

from avdb.models import \
    ContactPerson, \
    Convention, \
    Equipment, \
    EquipmentType, \
    Item, \
    ItemType, \
    Language, \
    Location, \
    LocationType, \
    Unit, \
    UnitType
from .forms import ImportCSVFileForm

import csv
from decimal import Decimal, InvalidOperation

import logging
logger = logging.getLogger(__name__)

# delimiter character for CSV data
csv_delimiter = ';'
csv_quotechar = '"'

@user_passes_test(lambda u: u.is_superuser)
def index(request):
    return render(request, 'imports/index.html')

# ---------
# LOCATIONS
# ---------

location_columns = ['Name', 'Address', 'Entrance', 'Loc type', 'Abbreviation']

@user_passes_test(lambda u: u.is_superuser)
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
            logger.error(row)
            return ('Invalid koo locations CSV data. Header must be "%s"' % csv_delimiter.join(location_columns), [], [])

        if first_row:
            first_row = False
            continue

        try:
            loc_type = LocationType.objects.get(pk=row[3]['val'])
            if loc_type is not None:
                # import location row
                location = Location(
                    name=row[0]['val'],
                    address=row[1]['val'],
                    entrance=row[2]['val'],
                    loc_type=loc_type,
                    abbreviation=row[4]['val'],
                )
                location.save()
                imported.append(location)

        except ObjectDoesNotExist:
            row[3]['error'] = 'Invalid value'
            failed.append(row)

    return (None, imported, failed)

# -----------
# CONVENTIONS
# -----------

convention_columns = ['Name', 'Lang', 'Starts', 'Ends', 'Load in', 'Load out', 'Location', 'Contact person']

@user_passes_test(lambda u: u.is_superuser)
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
            language = Language.objects.get(pk=row[1]['val'])
        except ObjectDoesNotExist:
            row[1]['error'] = 'Invalid value'
            error = True

        try:
            starts = None
            if row[2]['val'] != '':
                starts = handle_date(row[2]['val'])
        except TypeError:
            row[2]['error'] = 'Invalid value'
            error = True

        try:
            ends = None
            if row[3]['val'] != '':
                ends = handle_date(row[3]['val'])
        except TypeError:
            row[3]['error'] = 'Invalid value'
            error = True

        try:
            load_in = None
            if row[4]['val'] != '':
                load_in = handle_datetime(row[4]['val'])
        except TypeError:
            row[4]['error'] = 'Invalid value'
            error = True

        try:
            load_out = None
            if row[5]['val'] != '':
                load_out = handle_datetime(row[5]['val'])
        except TypeError:
            row[5]['error'] = 'Invalid value'
            error = True

        try:
            location = Location.objects.get(pk=row[6]['val'])
        except ObjectDoesNotExist:
            row[6]['error'] = 'Invalid value'
            error = True

        try:
            contact_person = None
            if row[7]['val'] != '':
                contact_person = ContactPerson.objects.get(pk=row[7]['val'])
        except ObjectDoesNotExist:
            row[7]['error'] = 'Invalid value'
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
                contact_person=contact_person,
            )
            convention.save()
            imported.append(convention)
        else:
            failed.append(row)

    return (None, imported, failed)


# ---------------
# CONTACT PERSONS
# ---------------

contact_person_columns = ['Name', 'Phone', 'Email']

@user_passes_test(lambda u: u.is_superuser)
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

        logger.error(row)
        # import convention row
        person = ContactPerson(
            name=row[0]['val'],
            phone=row[1]['val'],
            email=row[2]['val'],
        )
        person.save()
        imported.append(person)

    return (None, imported, failed)


# ----------
# EQUIPMENTS
# ----------

equipment_columns = ['Name', 'Type', 'Footprint', 'Pallet space', 'Space calculated']

@user_passes_test(lambda u: u.is_superuser)
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

        try:
            footprint = None
            if row[2]['val'] != '':
                footprint = Decimal(row[2]['val'].replace(',', '.'))
        except InvalidOperation:
            row[2]['error'] = 'Invalid value'
            error = True

        try:
            pallet_space = None
            if row[3]['val'] != '':
                pallet_space = Decimal(row[3]['val'].replace('.', '.'))
        except InvalidOperation:
            row[3]['error'] = 'Invalid value'
            error = True

        space_calculated = row[4]['val'] != ''

        if not error:
            # import equipment row
            equipment = Equipment(
                name=row[0]['val'],
                equipment_type=equipment_type,
                footprint=footprint,
                pallet_space=pallet_space,
                space_calculated=space_calculated,
            )
            equipment.save()
            imported.append(equipment)
        else:
            failed.append(row)

    return (None, imported, failed)

# -----
# UNITS
# -----

unit_columns = ['Name', 'Equipment', 'Footprint', 'Pallet space', 'Type', 'Dead weight', 'Net weight', 'Gross weight', 'Width', 'Height', 'Depth', 'Built in items', 'Included in']

@user_passes_test(lambda u: u.is_superuser)
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
                footprint = Decimal(row[2]['val'].replace(',', '.'))
        except InvalidOperation:
            row[2]['error'] = 'Invalid value'
            error = True

        try:
            pallet_space = None
            if row[3]['val'] != '':
                pallet_space = Decimal(row[3]['val'].replace(',', '.'))
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

# -----
# ITEMS
# -----

item_columns = ['Name', 'Brand', 'Model', 'Serial number', 'Type', 'Weight', 'Width', 'Height', 'Depth', 'Failure', 'Length', 'Connector', 'Unit']

@user_passes_test(lambda u: u.is_superuser)
def import_items(request):
    error = None
    imported = []
    failed = []
    if request.method == 'POST':
        form = ImportCSVFileForm(request.POST, request.FILES)
        if form.is_valid():
            error, imported, failed = handle_items_file(request.FILES['file'])
    else:
        # show blank form
        form = ImportCSVFileForm()

    return render(request, 'imports/import_items.html', {
        'form': form,
        'error': error,
        'imported': imported,
        'failed': failed
    })

def handle_items_file(f):
    try:
        reader = get_csv_reader(f)
    except UnicodeDecodeError:
        return ('Invalid CSV file. Make sure CSV is in UTF-8 format.', [], [])

    imported = []
    failed = []

    first_row = True
    for row in reader:

        row = convert_row(row)

        if first_row and not header_row_is_valid(row, item_columns):
            return ('Invalid conventions CSV data. Header must be "%s"' % csv_delimiter.join(item_columns), [], [])

        if first_row:
            first_row = False
            continue

        error = False

        try:
            item_type = ItemType.objects.get(name=row[4]['val'])
        except InvalidOperation:
            row[4]['error'] = 'Invalid value'
            error = True

        try:
            weight = None
            if row[5]['val'] != '':
                weight = int(row[5]['val'])
        except ValueError:
            row[5]['error'] = 'Invalid value'
            error = True

        try:
            width = None
            if row[6]['val'] != '':
                width = int(row[6]['val'])
        except ValueError:
            row[6]['error'] = 'Invalid value'
            error = True

        try:
            height = None
            if row[7]['val'] != '':
                height = int(row[7]['val'])
        except ValueError:
            row[7]['error'] = 'Invalid value'
            error = True

        try:
            depth = None
            if row[8]['val'] != '':
                depth = int(row[8]['val'])
        except ValueError:
            row[8]['error'] = 'Invalid value'
            error = True

        failure = row[9]['val'] != ''

        try:
            length = None
            if row[10]['val'] != '':
                depth = int(row[10]['val'])
        except ValueError:
            row[10]['error'] = 'Invalid value'
            error = True

        try:
            unit = None
            if row[12]['val'] != '':
                unit = Unit.objects.get(name=row[12]['val'])
        except ObjectDoesNotExist:
            row[12]['error'] = 'Invalid value'
            error = True

        if not error:
            # import item row
            item = Item(
                name=row[0]['val'],
                brand=row[1]['val'],
                model=row[2]['val'],
                serial_number=row[3]['val'],
                item_type=item_type,
                weight=weight,
                width=width,
                height=height,
                depth=depth,
                failure=failure,
                length=length,
                connector=row[11]['val'],
                unit=unit,
            )
            item.save()
            imported.append(item)
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

def header_row_is_valid(row, columns):
    """Returns true if given row matches defined columns."""

    # skip BOM UTF-8 character inserted by Excel
    if row[0]['val'][0] == u'\ufeff':
        row[0]['val'] = row[0]['val'][1:]

    if len(row) != len(columns):
        return False

    for i in range(0, len(row)):
        if row[i]['val'] != columns[i]:
            return False

    return True

def handle_date(s):
    if s is None:
        raise TypeError('invalid date')
    return s

def handle_datetime(s):
    if s is None:
        raise TypeError('invalid date time')
    return "%s:00" % s
