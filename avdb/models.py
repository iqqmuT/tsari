from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# for debugging
#import logging
#logger = logging.getLogger(__name__)

# Database diagram:
# https://www.lucidchart.com/documents/view/321a7808-dc9c-4990-bc55-a52a212aa426

class Language(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=8)

    def __str__(self):
        return self.name + ' (' + self.code + ')'

    class Meta:
        ordering = ['name']

class LocationType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Location(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    loc_type = models.ForeignKey(LocationType, null=True, on_delete=models.SET_NULL)
    abbreviation = models.CharField(max_length=16)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Convention(models.Model):
    name = models.CharField(max_length=128)
    lang = models.ForeignKey(Language, null=True, on_delete=models.SET_NULL)
    starts = models.DateField(blank=True, null=True)
    ends = models.DateField(blank=True, null=True)
    load_in = models.DateTimeField(blank=True, null=True)
    load_out = models.DateTimeField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.lang is not None:
            return "%s (%s)" % (self.name, self.lang.code)
        return self.name

    class Meta:
        ordering = ['starts', 'name']

class ContactPerson(models.Model):
    name = models.CharField(max_length=64)
    phone = models.CharField(max_length=128, blank=True)
    email = models.CharField(max_length=128, blank=True)
    convention = models.ForeignKey(Convention, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TransportOrder(models.Model):
    name = models.CharField(max_length=256, blank=True)
    from_convention = models.ForeignKey(
        Convention,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='from_convention',
    )
    to_convention = models.ForeignKey(
        Convention,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='to_convention',
    )
    from_loc = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='from_loc',
    )
    to_loc = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='to_loc',
    )
    from_loc_load_out = models.DateTimeField(null=True, blank=True)
    to_loc_load_in = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=512, blank=True)
    unit_notes = models.CharField(max_length=512, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        s = self.name + ' '

        from_s = ''
        if self.from_convention is not None:
            from_s = self.from_convention
        else:
            from_s = self.from_loc

        to_s = ''
        if self.to_convention is not None:
            to_s = self.to_convention
        else:
            to_s = self.to_loc

        return "%s: %s → %s" % (self.name, from_s, to_s)

    class Meta:
        ordering = ['name']

class EquipmentType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Equipment(models.Model):
    name = models.CharField(max_length=256)
    equipment_type = models.ForeignKey(EquipmentType, null=True, on_delete=models.SET_NULL)
    footprint = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2)
    pallet_space = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2)
    space_calculated = models.BooleanField(default=False)
    gross_weight = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def unit_field_sum(self, field):
        """Returns sum of given item field."""
        total = 0
        for unit in self.unit_set.all():
            # sum only parent units
            if unit.included_in is None:
                value = getattr(unit, field)
                if value is not None:
                    total += value
        return total

    def calculate_footprint(self):
        self.footprint = self.unit_field_sum('footprint')
        return self.footprint

    def calculate_pallet_space(self):
        self.pallet_space = self.unit_field_sum('pallet_space')
        return self.footprint

    def calculate_space(self):
        self.calculate_footprint()
        self.calculate_pallet_space()
        self.space_calculated = True

    def update_gross_weight(self):
        self.gross_weight = self.unit_field_sum('gross_weight')
        return self.save()

class TransportOrderLine(models.Model):
    transport_order = models.ForeignKey(TransportOrder, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s, %s" % (self.transport_order, self.equipment)

    class Meta:
        ordering = ['transport_order__name', 'equipment__name']


class UnitType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Unit(models.Model):
    name = models.CharField(max_length=256)
    equipment = models.ForeignKey(Equipment, null=True, on_delete=models.SET_NULL)
    footprint = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2)
    pallet_space = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2)
    unit_type = models.ForeignKey(UnitType, null=True, on_delete=models.SET_NULL)
    dead_weight = models.IntegerField(null=True, blank=True)
    net_weight = models.IntegerField(null=True, blank=True)
    gross_weight = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)
    built_in_items = models.CharField(max_length=256, blank=True)
    # parent unit
    included_in = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='includes',
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def child_unit_field_sum(self, field):
        """Returns sum of given child unit field."""
        total = 0
        for unit in self.includes.all():
            value = getattr(unit, field)
            if value is not None:
                total += value
        return total

    def item_field_sum(self, field):
        """Returns sum of given item field."""
        total = 0
        for item in self.item_set.all():
            value = getattr(item, field)
            if value is not None:
                total += value
        return total

    def update_weight(self):
        self.net_weight = self.child_unit_field_sum('gross_weight')
        self.net_weight += self.item_field_sum('weight')

        # net weight changed, update gross weight too
        if self.dead_weight is not None:
            self.gross_weight = self.dead_weight + self.net_weight

        return self.save()

    def clean(self):
        if self.dead_weight is not None and self.net_weight is not None and self.gross_weight is not None:
            if self.dead_weight + self.net_weight != self.gross_weight:
                raise ValidationError(_('Incorrect weight values. Rule: dead weight + net weight = gross weight. You can also leave dead or gross weight empty to be calculated.'))

    def save(self, *args, **kwargs):
        if self.net_weight is not None:
            # fill missing gross or dead weight automatically
            if self.gross_weight is None and self.dead_weight is None:
                self.dead_weight = 0

            if self.gross_weight is None and self.dead_weight is not None:
                self.gross_weight = self.dead_weight + self.net_weight

            if self.dead_weight is None and self.gross_weight is not None:
                self.dead_weight = self.gross_weight - self.net_weight

        # Calling the real save() method
        super().save(*args, **kwargs)

        if self.included_in is not None:
            # update parent unit weight
            self.included_in.update_weight()
        else:
            # no parent unit, update equipment gross weight
            self.equipment.update_gross_weight()

class TransportOrderUnit(models.Model):
    transport_order = models.ForeignKey(TransportOrder, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    included = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s, %s" % (self.transport_order, self.unit)

    class Meta:
        ordering = ['transport_order__name', 'unit__name']


class ItemType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Item(models.Model):
    name = models.CharField(max_length=256)
    brand = models.CharField(max_length=128, blank=True)
    model = models.CharField(max_length=128, blank=True)
    serial_number = models.CharField(max_length=64, blank=True)
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    weight = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)
    failure = models.BooleanField(default=False)
    length = models.IntegerField(null=True, blank=True)
    connector = models.CharField(max_length=128, blank=True)
    unit = models.ForeignKey(Unit, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Calling the real save() method
        super().save(*args, **kwargs)

        # update unit weight fields
        if self.unit is not None:
            self.unit.update_weight()

    class Meta:
        ordering = ['name']

class ItemFailure(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=512)
    reporter = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']


# Status models

class TransportOrderStatusType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Abstract base class for *Status models
class BaseStatus(models.Model):
    status = models.ForeignKey(TransportOrderStatusType, null=True, on_delete=models.SET_NULL)
    reporter = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TransportOrderLineStatus(BaseStatus):
    """
    TransportOrderLineStatus does not need FK to TransportOrder,
    it can be solved through TransportOrderLine.
    """
    to_line = models.ForeignKey(TransportOrderLine, on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']
        verbose_name_plural = 'Transport order line status'


class OrderUnitStatus(BaseStatus):
    to_unit = models.ForeignKey(TransportOrderUnit, on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']
        verbose_name_plural = 'Order unit status'


class OrderItemStatus(BaseStatus):
    transport_order = models.ForeignKey(TransportOrder, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']
        verbose_name_plural = 'Order item status'
