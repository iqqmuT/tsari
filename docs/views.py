from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from avdb.models import Equipment, \
    TransportOrder, \
    TransportOrderLine

@user_passes_test(lambda u: u.is_superuser)
def transport_order(request, to_id):
    to = get_object_or_404(TransportOrder, pk=to_id)

    # calculate totals
    totals = {
        'units': 0,
        'pallet_space': 0,
        'footprint': 0,
    }
    for to_line in to.transportorderline_set.all():
        totals['units'] += to_line.equipment.get_parent_units().count()
        totals['pallet_space'] += to_line.equipment.pallet_space
        totals['footprint'] += to_line.equipment.footprint
            
    return render(request, 'docs/transport_order.html', {
        'to': to,
        'totals': totals,
    })
