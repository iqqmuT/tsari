from django.shortcuts import render

from .models import Location

def start(request):
    """Starts session."""
    locations = Location.objects.all()
    return render(request, 'avdb/start.html', {
        'locations': locations,
    })
