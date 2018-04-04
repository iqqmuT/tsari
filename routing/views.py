from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone

from avdb.models import \
    Convention, \
    Equipment, \
    Location, \
    TransportOrder, \
    TransportOrderLine

import logging
logger = logging.getLogger(__name__)

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
    end_date = end_date + timedelta(weeks=1)

    weeks = []
    monday = start_date
    while monday < end_date:
        weeks.append({
            'monday': monday,
            'sunday': monday + timedelta(days=6),
            'number': monday.isocalendar()[1],
        })
        monday = monday + timedelta(weeks=1)

    logger.error(weeks)

    equipment_groups = [
        _handle_equipments(video_eqs, weeks),
        _handle_equipments(audio_eqs, weeks),
        _handle_equipments(elec_eqs, weeks),
    ]

    return render(request, 'routing/index.html', {
        'year': year,
        'equipment_groups': equipment_groups,
        'weeks': weeks,
        'start': start_date,
        'end': end_date,
        'all_locations': Location.objects.all(),
    })

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


def _handle_equipments(equipments, weeks):
    objs = []
    for equipment in equipments:
        eq_weeks = []
        for week in weeks:
            w = {
                'week': week,
                'transport_order': None,
                'convention': None,
                'conventions': _get_conventions(week['number']),
            }
            w['other_locations'] = _get_other_locations(w['conventions'])
            eq_weeks.append(w)

        objs.append({
            'eq': equipment,
            'weeks': eq_weeks,
        })
    return objs

convention_cache = {}
def _get_conventions(week):
    if week not in convention_cache.keys():
        convention_cache[week] = Convention.objects.all()
    return convention_cache[week]

location_cache = {}
def _get_other_locations(conventions):
    key = ','.join(str(x) for x in conventions)
    if key not in location_cache.keys():
        location_ids = conventions.values_list('location__id', flat=True)
        location_cache[key] = Location.objects.all().exclude(id__in=location_ids)
    return location_cache[key]
