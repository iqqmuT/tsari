from django.shortcuts import render

from .models import Location

def start(request):
    """Starts session."""
    locations = Location.objects.all()
    return render(request, 'avdb/start.html', {
        'locations': locations,
    })

def table_test(request):
    return render(request, 'avdb/table_test.html', {})
