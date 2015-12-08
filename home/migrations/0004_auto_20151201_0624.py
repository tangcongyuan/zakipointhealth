# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20151201_0548'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ZakiUser',
            new_name='AppUser',
        ),
    ]
