"""tsari URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from avdb import views as avdb_views
from imports import views as imports_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('import/locations/', imports_views.import_locations, name='import_locations'),
    path('import/conventions/', imports_views.import_conventions, name='import_conventions'),
    path('import/contact_persons/', imports_views.import_contact_persons, name='import_contact_persons'),
    path('import/equipments/', imports_views.import_equipments, name='import_equipments'),
    path('import/units/', imports_views.import_units, name='import_units'),
    path('import/item_classes/', imports_views.import_item_classes, name='import_item_classes'),
    path('import/items/', imports_views.import_items, name='import_items'),
    path('import/', imports_views.index, name='import_index'),
    path('start/', avdb_views.start, name='start'),
]
