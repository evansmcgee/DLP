# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-21 20:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dlp', '0035_teams'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageViews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField(max_length=255)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dlp.MessageBoard')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
