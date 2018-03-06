from django.contrib import admin

from .models import *

admin.site.register(Language)
admin.site.register(LocationType)
admin.site.register(Location)
admin.site.register(Convention)
admin.site.register(ContactPerson)
admin.site.register(Shipment)
admin.site.register(Equipment)
admin.site.register(UnitType)
admin.site.register(Unit)
admin.site.register(ItemType)
admin.site.register(Item)
admin.site.register(ItemFailure)
admin.site.register(LoadingList)
admin.site.register(ShipmentStatusType)
admin.site.register(EquipmentShipmentStatus)
admin.site.register(UnitShipmentStatus)
admin.site.register(ItemShipmentStatus)
