from django.test import TestCase
from .models import Equipment, UnitType, Unit, ItemType, Item

class WeightTestCase(TestCase):
    def setUp(self):
        # create equipment
        equipment = Equipment.objects.create(name='Stuff')
        # create unit types: rack, rack drawer
        rack_type = UnitType.objects.create(name='Rack')
        rack_drawer_type = UnitType.objects.create(name='Rack drawer')
        # create unit
        rack = Unit.objects.create(
            name='Rack',
            equipment=equipment,
            dead_weight=2000,
            unit_type=rack_type,
        )
        # create rack drawer
        rack_drawer = Unit.objects.create(
            name='Rack drawer',
            equipment=equipment,
            unit_type=rack_drawer_type,
            dead_weight=500,
            included_in=rack,
        )
        # create item type: device
        device_type = ItemType.objects.create(name='Device')
        # create item
        item = Item.objects.create(
            name='Device 1 in rack',
            item_type=device_type,
            unit=rack_drawer,
            weight=1500,
            width=50,
            height=40,
            depth=30,
        )

    def test_weight_calculation(self):
        """
        Equipment
         - Rack (dead 1000 g)
           - Drawer (dead 500 g)
             - Device 1 (1500 g)
             - Device 2 (1000 g)
        """
        equipment = Equipment.objects.get(name='Stuff')
        self.assertEqual(str(equipment), 'Stuff')

        rack = Unit.objects.get(name='Rack')
        self.assertEqual(str(rack), 'Rack')

        rack_drawer = Unit.objects.get(name='Rack drawer')
        self.assertEqual(str(rack_drawer), 'Rack drawer')

        device1 = Item.objects.get(name='Device 1 in rack')
        self.assertEqual(str(device1), 'Device 1 in rack')

        # rack drawer weight should be calculated automatically
        self.assertEqual(rack_drawer.net_weight, 1500)

        # rack weight should be calculated automatically
        self.assertEqual(rack.net_weight, 2000)

        # equipment gross weight should be calculated automatically
        self.assertEqual(equipment.gross_weight, 4000)

        # add second device
        # create item type: device
        device_type = ItemType.objects.get(name='Device')
        # create item
        item = Item.objects.create(
            name='Device 2 in rack',
            item_type=device_type,
            unit=rack_drawer,
            weight=1000,
            width=50,
            height=40,
            depth=30,
        )

        # rack drawer weight should be updated automatically
        rack_drawer.refresh_from_db()
        self.assertEqual(rack_drawer.net_weight, 2500)

        # rack drawer weight should be updated automatically
        rack.refresh_from_db()
        self.assertEqual(rack_drawer.gross_weight, 3000)

        # equipment weight should be updated automatically
        equipment.refresh_from_db()
        self.assertEqual(equipment.gross_weight, 5000)
