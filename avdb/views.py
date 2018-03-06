from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import ImportCSVTextForm
from .models import Location

def import_csv_form(request):
    if request.method == 'POST':
        form = ImportCSVTextForm(request.POST)
        if form.is_valid():
            # do something
            return HttpResponseRedirect('/imported')
    else:
        # show blank form
        form = ImportCSVTextForm()

    return render(request, 'avdb/import_csv_form.html', { 'form': form })

def start(request):
    """Starts session."""
    locations = Location.objects.all()
    return render(request, 'avdb/start.html', {
        'locations': locations,
    })
