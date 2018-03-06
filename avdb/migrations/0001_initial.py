# Generated by Django 2.0.1 on 2018-03-06 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('phone', models.CharField(blank=True, max_length=128)),
                ('email', models.CharField(blank=True, max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Convention',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('starts', models.DateField(blank=True, null=True)),
                ('ends', models.DateField(blank=True, null=True)),
                ('load_in', models.DateTimeField(blank=True, null=True)),
                ('load_out', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['starts', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('footprint', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('pallet_space', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('space_calculated', models.BooleanField(default=False)),
                ('gross_weight', models.IntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='EquipmentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('brand', models.CharField(blank=True, max_length=128)),
                ('model', models.CharField(blank=True, max_length=128)),
                ('serial_number', models.CharField(blank=True, max_length=64)),
                ('weight', models.IntegerField(blank=True, null=True)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('depth', models.IntegerField(blank=True, null=True)),
                ('failure', models.BooleanField(default=False)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('connector', models.CharField(blank=True, max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ItemFailure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=512)),
                ('reporter', models.CharField(max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.Item')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('code', models.CharField(max_length=8)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('address', models.CharField(max_length=256)),
                ('abbreviation', models.CharField(max_length=16)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='OrderItemStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reporter', models.CharField(max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.Item')),
            ],
            options={
                'verbose_name_plural': 'Order item status',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='OrderUnitStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reporter', models.CharField(max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Order unit status',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='TransportOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=256)),
                ('from_loc_load_out', models.DateTimeField(blank=True, null=True)),
                ('to_loc_load_in', models.DateTimeField(blank=True, null=True)),
                ('notes', models.CharField(blank=True, max_length=512)),
                ('unit_notes', models.CharField(blank=True, max_length=512)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('from_convention', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_convention', to='avdb.Convention')),
                ('from_loc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_loc', to='avdb.Location')),
                ('to_convention', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_convention', to='avdb.Convention')),
                ('to_loc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_loc', to='avdb.Location')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TransportOrderLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.Equipment')),
                ('transport_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.TransportOrder')),
            ],
            options={
                'ordering': ['transport_order__name', 'equipment__name'],
            },
        ),
        migrations.CreateModel(
            name='TransportOrderLineStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reporter', models.CharField(max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Transport order line status',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='TransportOrderStatusType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('footprint', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('pallet_space', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('dead_weight', models.IntegerField(blank=True, null=True)),
                ('net_weight', models.IntegerField(blank=True, null=True)),
                ('gross_weight', models.IntegerField(blank=True, null=True)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('depth', models.IntegerField(blank=True, null=True)),
                ('built_in_items', models.CharField(blank=True, max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('equipment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.Equipment')),
                ('included_in', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='includes', to='avdb.Unit')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UnitType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='unit',
            name='unit_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.UnitType'),
        ),
        migrations.AddField(
            model_name='transportorderlinestatus',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.TransportOrderStatusType'),
        ),
        migrations.AddField(
            model_name='transportorderlinestatus',
            name='to_line',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.TransportOrderLine'),
        ),
        migrations.AddField(
            model_name='orderunitstatus',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.TransportOrderStatusType'),
        ),
        migrations.AddField(
            model_name='orderunitstatus',
            name='transport_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.TransportOrder'),
        ),
        migrations.AddField(
            model_name='orderunitstatus',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.Unit'),
        ),
        migrations.AddField(
            model_name='orderitemstatus',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.TransportOrderStatusType'),
        ),
        migrations.AddField(
            model_name='orderitemstatus',
            name='transport_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.TransportOrder'),
        ),
        migrations.AddField(
            model_name='location',
            name='loc_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.LocationType'),
        ),
        migrations.AddField(
            model_name='item',
            name='item_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.ItemType'),
        ),
        migrations.AddField(
            model_name='item',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.Unit'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='equipment_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.EquipmentType'),
        ),
        migrations.AddField(
            model_name='convention',
            name='lang',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avdb.Language'),
        ),
        migrations.AddField(
            model_name='convention',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.Location'),
        ),
        migrations.AddField(
            model_name='contactperson',
            name='convention',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avdb.Convention'),
        ),
    ]
