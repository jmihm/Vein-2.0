# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miso_tables', '0002_auto_20160330_0249'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherForecast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prediction_dt', models.DateTimeField()),
                ('latitude', models.DecimalField(max_digits=9, decimal_places=6)),
                ('longitude', models.DecimalField(max_digits=9, decimal_places=6)),
                ('hour', models.IntegerField()),
                ('cloud_cover', models.FloatField()),
                ('apparent_temp', models.FloatField()),
                ('pressure', models.FloatField()),
                ('visibility', models.FloatField()),
                ('summary', models.CharField(max_length=56)),
                ('temperature', models.FloatField()),
                ('dew_point', models.FloatField()),
                ('humidity', models.FloatField()),
                ('ozone', models.FloatField()),
                ('wind_speed', models.FloatField()),
                ('wind_bearing', models.FloatField()),
                ('precip_intensity', models.FloatField()),
                ('precip_probability', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='node',
            name='include_weather',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='node',
            name='latitude',
            field=models.DecimalField(default=0, max_digits=9, decimal_places=6),
        ),
        migrations.AddField(
            model_name='node',
            name='longitude',
            field=models.DecimalField(default=0, max_digits=9, decimal_places=6),
        ),
    ]
