# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20151207_1602'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='approle',
            name='name',
        ),
    ]
