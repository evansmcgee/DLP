# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 13:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dlp', '0004_auto_20160924_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitecode',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
