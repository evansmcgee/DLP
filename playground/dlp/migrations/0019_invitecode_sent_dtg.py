# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-27 16:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dlp', '0018_remove_invitecode_sent_dtg'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitecode',
            name='sent_dtg',
            field=models.DateTimeField(default='1981-04-15 05:15'),
            preserve_default=False,
        ),
    ]
