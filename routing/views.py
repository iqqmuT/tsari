import json
from datetime import datetime, timedelta
from dateutil import parser as dateparser

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from avdb.models import \
    Convention, \
    Equipment, \
    Location, \
    LocationType, \
    TransportOrder, \
    TransportOrderLine

import logging
logger = logging.getLogger(__name__)

# TO data structure
# {
#   'disabled': False,
#   'equipment': 1,
#   'week': '2018-05-28T09:00:00+00:00',
#   'from': {
#     'location': 9,
#     'load_out': '2018-06-19T08:00:00+00:00'
#   },
#   'to': {
#     'location': 4,
#     'convention': 7,
#     'load_in': '2018-06-19T09:00:00+00:00'
#   },
#   'name': 'First TO',
#   'notes': 'Notes',
#   'unitNotes': 'Uniittinotes'
# }

#@user_passes_test(lambda u: u.is_superuser)
def index(request, year):
    video_eqs = Equipment.objects.filter(equipment_type__name='Video')
    audio_eqs = Equipment.objects.filter(equipment_type__name='Audio')
    elec_eqs = Equipment.objects.filter(equipment_type__name='Electricity')

    # get time period
    first = _get_first_convention(year)
    last = _get_last_convention(year)

    if first is None or last is None:
        return HttpResponseNotFound("No conventions found for year %d" % year)
    start_date = first.load_in
    end_date = last.load_out

    # move start_date backwards to previous monday + 1 week
    start_date = start_date - timedelta(days=start_date.weekday() + 7)

    # move end_date forwards by week
    end_date = end_date + timedelta(weeks=2)

    weeks = []
    monday = start_date
    while monday < end_date:
        weeks.append({
            'monday': _get_previous_monday(monday),
            'sunday': _get_next_sunday(monday),
            'number': monday.isocalendar()[1],
        })
        monday = monday + timedelta(weeks=1)

    to_data = []

    equipment_groups = [
        _handle_equipments(video_eqs, weeks, to_data),
        _handle_equipments(audio_eqs, weeks, to_data),
        _handle_equipments(elec_eqs, weeks, to_data),
    ]

    return render(request, 'routing/index.html', {
        'year': year,
        'equipment_groups': equipment_groups,
        'weeks': weeks,
        'conventions': json.dumps(_get_conventions_json()),
        'start': start_date,
        'end': end_date,
        'other_locations': _get_other_locations(),
        'locations_json': json.dumps(_get_locations_json()),
        'json': json.dumps(to_data),
    })

# Save JSON request
def save(request, year):
    data = json.loads(request.body.decode('utf-8'))

    # Disable all existing TransportOrders for this year,
    # and enable only those we are editing/creating
    _disable_all_tos(year)

    # Remove existing TransportOrderLines for this year
    # We will re-create new TransportOrderLines
    eq_ids = set()
    for to_data in data['tos']:
        eq_ids.add(to_data['equipment'])
    for id in eq_ids:
        _remove_tols(id, year)

    for to_data in data['tos']:
        if to_data['disabled'] == False:
            tol = _save_to_data(to_data)

    return JsonResponse({ 'ok': True })

def _save_to_data(to_data):
    """Saves TransportOrder data."""
    to = _get_or_create_to(to_data)
    if to is None:
        # could not create TO
        return None
    week = dateparser.parse(to_data['week'])
    monday = _get_previous_monday(week)
    sunday = _get_next_sunday(week)

    # create new TransportOrderLine
    tol = TransportOrderLine(
        equipment=Equipment.objects.get(pk=to_data['equipment']),
        transport_order=to,
    )
    tol.save()
    return tol

def _disable_all_tos(year):
    """Disables all TransportOrders from given year."""
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)

    tos = TransportOrder.objects.filter(
        Q(from_loc_load_out__range=(start, end)) | Q(to_loc_load_in__range=(start, end)) | Q(from_convention__load_out__range=(start, end)) | Q(to_convention__load_in__range=(start, end))
    )
    for to in tos:
        to.disabled = True
        to.save()

def _get_or_create_to(to_data):
    """Gets or creates TransportOrder with given data."""

    from_location = None
    from_convention = None
    from_load_out = None
    if 'from' in to_data.keys():
        if 'convention' in to_data['from'].keys():
            id = to_data['from']['convention']
            from_convention = Convention.objects.get(pk=id)
        if 'location' in to_data['from'].keys():
            id = to_data['from']['location']
            from_location = Location.objects.get(pk=id)
        if from_convention is None and 'load_out' in to_data['from'].keys() and _is_valid_datetime(to_data['from']['load_out']):
            from_load_out = dateparser.parse(to_data['from']['load_out'])

    to_location = None
    to_convention = None
    to_load_in = None
    if 'from' in to_data.keys():
        if 'convention' in to_data['to'].keys():
            id = to_data['to']['convention']
            to_convention = Convention.objects.get(pk=id)
        if 'location' in to_data['to'].keys():
            id = to_data['to']['location']
            to_location = Location.objects.get(pk=id)
        if to_convention is None and 'load_out' in to_data['to'].keys() and _is_valid_datetime(to_data['to']['load_in']):
            to_load_out = to_data['to']['load_in']

    if from_location is None or to_location is None:
        # can't create TransportOrder with empty Locations
        return None

    to, created = TransportOrder.objects.get_or_create(
        from_convention=from_convention,
        to_convention=to_convention,
        from_loc=from_location,
        to_loc=to_location,
        from_loc_load_out=from_load_out,
        to_loc_load_in=to_load_in,
    )
    # update other fields
    if 'name' in to_data.keys():
        to.name = to_data['name']

    if 'notes' in to_data.keys():
        to.notes = to_data['notes']

    if 'unitNotes' in to_data.keys():
        to.unit_notes = to_data['unitNotes']
 
    to.disabled = False
    to.save()
    return to

def _is_valid_datetime(s):
    try:
        dateparser.parse(s)
        return True
    except ValueError:
        logger.error("Invalid datetime '%s'" % s)
        return False

def _get_previous_monday(d):
    """Returns previous monday from given datetime."""
    monday = d - timedelta(days=d.weekday())
    # set time to 00:00:00
    return datetime(monday.year, monday.month, monday.day, 0, 0, 0)

def _get_next_sunday(d):
    sunday = d + timedelta(days=6-d.weekday())
    # set time to 23:59:59
    return datetime(sunday.year, sunday.month, sunday.day, 23, 59, 59)

def _get_first_convention(year):
    try:
        return Convention.objects.filter(load_in__year=year).earliest('load_in')
    except Convention.DoesNotExist:
        return None

def _get_last_convention(year):
    try:
        return Convention.objects.filter(load_out__year=year).latest('load_out')
    except Convention.DoesNotExist:
        return None

def _get_conventions_json():
    data = {}
    for conv in Convention.objects.all():
        d = {
            'name': conv.routing_name()
        }
        if conv.load_in is not None:
            d['load_in'] = conv.load_in.isoformat()

        if conv.load_out is not None:
            d['load_out'] = conv.load_out.isoformat()

        data[conv.id] = d

    return data

def _get_locations_json():
    data = {}
    for loc in Location.objects.all():
        d = {
            'name': loc.name,
        }
        data[loc.id] = d

    return data

def _get_earliest_to(year):
    try:
        return TransportOrder.objects.filter(from_loc_load_out__year=year).earliest('from_loc_load_out')
    except TransportOrder.DoesNotExist:
        return None

def _get_latest_to(year):
    try:
        return TransportOrder.objects.filter(to_loc_load_in__year=year).latest('to_loc_load_in')
    except TransportOrder.DoesNotExist:
        return None

def _handle_equipments(equipments, weeks, to_data):
    objs = []
    first = True
    for equipment in equipments:
        eq_weeks = []
        selected = "Select"
        start_location = selected
        latest_location = None
        latest_convention = None
        for week in weeks:
            # transport data
            tod = {
                #'transportOrder': None,
                'disabled': False,
                'equipment': equipment.pk,
                'week': week['monday'].isoformat(),
                'from': {
                    #'location': latest_location,
                    #'convention': latest_convention,
                },
                'to': {
                    #'location': latest_location,
                    #'convention': latest_convention,
                }
            }
            if latest_location is not None:
                tod['from']['location'] = latest_location
                tod['to']['location'] = latest_location
            if latest_convention is not None:
                tod['from']['convention'] = latest_convention
                tod['to']['convention'] = latest_convention

            # find matching TransportOrderLine and fill information from there to toData object
            tols = _find_tols(equipment.pk, week['monday'], week['sunday'])
            if len(tols):
                to = tols.first().transport_order
                tod['name'] = to.name
                tod['notes'] = to.notes
                tod['unitNotes'] = to.unit_notes
                if to.from_loc is not None:
                    tod['from']['location'] = to.from_loc.pk
                    if first:
                        selected = to.from_loc.name
                        start_location = to.from_loc.name
                    if len(eq_weeks) > 0:
                        eq_weeks[len(eq_weeks)-1]['selected'] = to.from_loc.name

                if to.from_convention is not None:
                    tod['from']['convention'] = to.from_convention.pk
                    tod['from']['location'] = to.from_convention.location.pk
                    if to.from_convention.load_out is not None:
                        tod['from']['load_out'] = to.from_convention.load_out.isoformat()
                    if first:
                        selected = to.from_convention.routing_name()
                        start_location = to.from_convention.routing_name()
                    if len(eq_weeks) > 0:
                        eq_weeks[len(eq_weeks)-1]['selected'] = to.from_convention.routing_name()

                if to.from_loc_load_out is not None:
                    tod['from']['load_out'] = to.from_loc_load_out.isoformat()
                
                if to.to_loc is not None:
                    tod['to']['location'] = to.to_loc.pk
                    selected = to.to_loc.name
                    latest_location = to.to_loc.pk
                if to.to_convention is not None:
                    tod['to']['convention'] = to.to_convention.pk
                    tod['to']['location'] = to.to_convention.location.pk
                    if to.to_convention.load_in is not None:
                        tod['to']['load_in'] = to.to_convention.load_in.isoformat()
                    selected = to.to_convention.routing_name()
                    latest_convention = to.to_convention.pk
                if to.to_loc_load_in is not None:
                    tod['to']['load_in'] = to.to_loc_load_in.isoformat()
 
            to_data.append(tod)

            # week data
            w = {
                'week': week,
                'to_idx': len(to_data) - 1, # index for to_data
                'convention': None,
                'conventions': _get_conventions(week['monday'], week['sunday']),
                'other_locations': _get_other_locations(),
                'selected': selected,
            }
            eq_weeks.append(w)

        objs.append({
            'eq': equipment,
            'weeks': eq_weeks,
            'start_location': start_location,
        })
        first = False
    return objs

convention_cache = {}
def _get_conventions(start, end):
    key = start.isoformat() + end.isoformat()
    if key not in convention_cache.keys():
        convention_cache[key] = Convention.objects.filter(
            starts__gte=start,
            ends__lte=end,
        )
    return convention_cache[key]

location_cache = {}
def _get_other_locations():
    """Returns all locations except convention venues."""
    if 'all' not in location_cache.keys():
        conv_venue = LocationType.objects.get(name='Convention venue')
        location_cache['all'] = Location.objects.exclude(loc_type=conv_venue)
    return location_cache['all']

def _find_tols(equipment_id, start, end):
    """Returns existing TransportOrderLines matching with given arguments."""
    #logger.error('Trying to find TOL')
    #logger.error(equipment_id)
    #logger.error(start_time)
    #logger.error(end_time)
    tols = TransportOrderLine.objects.filter(
        equipment__id=equipment_id).filter(
        Q(transport_order__from_loc_load_out__range=(start, end)) | Q(transport_order__to_loc_load_in__range=(start, end)) | Q(transport_order__from_convention__load_out__range=(start, end)) | Q(transport_order__to_convention__load_in__range=(start, end))
    )
    return tols

def _remove_tols(equipment_id, year):
    """Removes all TransportOrderLines for given equipment id and from that year."""
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)

    TransportOrderLine.objects.filter(
        equipment__id=equipment_id,
        transport_order__from_loc_load_out__range=(start, end),
    ).delete()

    TransportOrderLine.objects.filter(
        equipment__id=equipment_id,
        transport_order__to_loc_load_in__range=(start, end),
    ).delete()

    TransportOrderLine.objects.filter(
        equipment__id=equipment_id,
        transport_order__from_convention__load_out__range=(start, end),
    ).delete()

    TransportOrderLine.objects.filter(
        equipment__id=equipment_id,
        transport_order__to_convention__load_in__range=(start, end),
    ).delete()
