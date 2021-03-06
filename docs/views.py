from datetime import timedelta, datetime

from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.http import urlencode

from avdb.models import Convention, \
    Equipment, \
    TransportOrder, \
    TransportOrderLine

import logging
logger = logging.getLogger(__name__)

def get_year_transport_orders(year):
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)

    tos = TransportOrder.objects.filter(
        Q(from_loc_load_out__range=(start, end)) |
        Q(to_loc_load_in__range=(start, end)) |
        Q(from_convention__load_out__range=(start, end)) |
        Q(to_convention__load_in__range=(start, end))
    ).filter(disabled=False).order_by('created')

    to_ids = []
    all_similar = set()
    for to in tos:
        if to not in all_similar:
            similar = _find_similar_tos(to)
            to_ids.append(similar[0])
            for s in similar:
                all_similar.add(s)

    # sort list of transport orders alphabetically
    to_ids.sort(key=lambda to: str(to))
    return to_ids

@user_passes_test(lambda u: u.is_superuser)
def transport_orders(request, year):
    tos = get_year_transport_orders(year)
    return render(request, 'docs/transport_orders.html', {
        'tos': tos,
        'year': year,
    })

@user_passes_test(lambda u: u.is_superuser)
def print_transport_orders(request, year):
    tos = get_year_transport_orders(year)

    # add totals
    for to in tos:
        # calculate totals
        totals = {
            'units': 0,
            'pallet_space': 0,
            'footprint': 0,
            'weight': 0,
            'capacity': 0,
            'max_height': 0,
        }
        similar_tos = _find_similar_tos(to)
        for sto in similar_tos:
            for to_line in sto.transportorderline_set.filter(equipment__disabled=False):
                totals['units'] += to_line.equipment.get_parent_units().count()
                totals['pallet_space'] += to_line.equipment.pallet_space
                totals['footprint'] += to_line.equipment.footprint
                totals['weight'] += to_line.equipment.weight_kg()
                totals['capacity'] += to_line.equipment.capacity()
                if to_line.equipment.max_height() / 1000 > totals['max_height']:
                    totals['max_height'] = to_line.equipment.max_height() / 1000
        to.totals = totals


    return render(request, 'docs/print_transport_orders.html', {
        'tos': tos,
        'year': year,
    })


@user_passes_test(lambda u: u.is_superuser)
def transport_order(request, to_id):
    to = get_object_or_404(TransportOrder, pk=to_id)
    tos = _find_similar_tos(to)

    # all transport order lines
    to_lines = []
    # calculate totals
    totals = {
        'units': 0,
        'pallet_space': 0,
        'footprint': 0,
        'weight': 0,
        'capacity': 0,
        'max_height': 0,
    }
    for sto in tos:
        #logger.error('TO: %s' % sto)
        for to_line in sto.transportorderline_set.filter(equipment__disabled=False):
            to_lines.append(to_line)
            totals['units'] += to_line.equipment.get_parent_units().count()
            totals['pallet_space'] += to_line.equipment.pallet_space
            totals['footprint'] += to_line.equipment.footprint
            totals['weight'] += to_line.equipment.weight_kg()
            totals['capacity'] += to_line.equipment.capacity()
            if to_line.equipment.max_height() / 1000 > totals['max_height']:
                totals['max_height'] = to_line.equipment.max_height() / 1000

    # sort to_lines by equipment name
    to_lines = sorted(to_lines, key=lambda to_line: to_line.equipment.name)

    maps_url = 'https://www.google.com/maps/search/?'
    from_qr = ''
    to_qr = ''
    if to.get_from_loc() is not None and to.get_from_loc().address is not None:
        from_qr = maps_url + urlencode({
            'api': '1',
            'query': maps_url + to.get_from_loc().address
        })

    if to.get_to_loc() is not None and to.get_to_loc().address is not None:
        #to_qr = maps_url + urlencode(to.get_to_loc().address, False)
        to_qr = maps_url + urlencode({
            'api': '1',
            'query': to.get_to_loc().address
        })

    dir_qr = ''
    if to.get_from_loc() is not None and to.get_to_loc() is not None:
        dir_qr = 'https://www.google.com/maps/dir/?'
        params = {
            'api': '1',
            'origin': to.get_from_loc().address,
            'destination': to.get_to_loc().address,
            'travelmode': 'driving',
        }
        dir_qr += urlencode(params)

    return render(request, 'docs/transport_order.html', {
        'to': to,
        'totals': totals,
        'to_lines': to_lines,
        'from_qr': from_qr,
        'to_qr': to_qr,
        'dir_qr': dir_qr,
        'now': datetime.now(),
    })

@user_passes_test(lambda u: u.is_superuser)
def conventions(request, year):
    conventions = Convention.objects.filter(starts__year=year)
    return render(request, 'docs/conventions.html', {
        'year': year,
        'conventions': conventions,
    })

@user_passes_test(lambda u: u.is_superuser)
def convention_equipments(request, pk):
    convention = get_object_or_404(Convention, pk=pk)
    tos = TransportOrder.objects.filter(disabled=False, to_convention=convention)

    # all transport order lines
    to_lines = []
    # calculate totals
    totals = {
        'units': 0,
        'pallet_space': 0,
        'footprint': 0,
        'weight': 0,
        'capacity': 0,
        'max_height': 0,
    }
    for sto in tos:
        #logger.error('TO: %s' % sto)
        for to_line in sto.transportorderline_set.filter(equipment__disabled=False):
            to_lines.append(to_line)
            totals['units'] += to_line.equipment.get_parent_units().count()
            totals['pallet_space'] += to_line.equipment.pallet_space
            totals['footprint'] += to_line.equipment.footprint
            totals['weight'] += to_line.equipment.weight_kg()
            totals['capacity'] += to_line.equipment.capacity()
            if to_line.equipment.max_height() / 1000 > totals['max_height']:
                totals['max_height'] = to_line.equipment.max_height() / 1000

    # sort to_lines by equipment name
    to_lines = sorted(to_lines, key=lambda to_line: to_line.equipment.name)

    return render(request, 'docs/convention_equipments.html', {
        'convention': convention,
        'equipments': [],
        'totals': totals,
        'to_lines': to_lines,
        'now': datetime.now(),
    })

def _find_similar_tos(to):
    """Returns similar TOs which share same load in and out times, and locations."""
    tos = TransportOrder.objects.filter(
        disabled=False,
        from_loc=to.from_loc,
        to_loc=to.to_loc,
        from_loc_load_out=to.from_loc_load_out,
        to_loc_load_in=to.to_loc_load_in,
    )

    if to.from_convention is not None:
        from_conventions = Convention.objects.filter(
            location=to.from_convention.location,
            load_out=to.from_convention.load_out,
        )
        tos = tos.filter(from_convention__in=from_conventions)

    if to.to_convention is not None:
        to_conventions = Convention.objects.filter(
            location=to.to_convention.location,
            load_in=to.to_convention.load_in,
        )
        tos = tos.filter(to_convention__in=to_conventions)
    return tos
