# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-30 02:49
from __future__ import unicode_literals

from django.db import migrations, models
import miso_tables.models


class Migration(migrations.Migration):

    dependencies = [
        ('miso_tables', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LookAhead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('hour_ending', models.IntegerField()),
                ('north_pred', models.FloatField()),
                ('north_actual', models.FloatField(blank=True, null=True)),
                ('central_pred', models.FloatField()),
                ('central_actual', models.FloatField(blank=True, null=True)),
                ('south_pred', models.FloatField()),
                ('south_actual', models.FloatField(blank=True, null=True)),
                ('miso_pred', models.FloatField()),
                ('miso_actual', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='dataloadinglog',
            name='model',
            field=models.CharField(choices=[(4, miso_tables.models.LookAhead)], max_length=3),
        ),
    ]