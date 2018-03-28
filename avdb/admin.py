from django.contrib import admin

from .models import *

admin.site.register(Language)
admin.site.register(LocationType)
admin.site.register(Location)
admin.site.register(Convention)
admin.site.register(ContactPerson)
admin.site.register(TransportOrder)
admin.site.register(EquipmentType)
admin.site.register(Equipment)
admin.site.register(TransportOrderLine)
admin.site.register(UnitType)
admin.site.register(Unit)
admin.site.register(TransportOrderUnit)
admin.site.register(ItemType)
admin.site.register(Item)
admin.site.register(ItemFailure)
admin.site.register(TransportOrderStatusType)
admin.site.register(TransportOrderLineStatus)
admin.site.register(OrderUnitStatus)
admin.site.register(OrderItemStatus)
