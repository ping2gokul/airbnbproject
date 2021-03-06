# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-01 09:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('HotelApp', '0004_auto_20170430_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RoomType', models.CharField(max_length=255)),
                ('Capacity', models.IntegerField(default=0)),
                ('BedOption', models.CharField(max_length=255)),
                ('Price', models.IntegerField(default=0)),
                ('View', models.CharField(max_length=255)),
                ('TotalRooms', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HotelApp.Hotels')),
            ],
            options={
                'verbose_name_plural': 'Room',
            },
        ),
    ]
