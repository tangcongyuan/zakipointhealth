# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('home', '0005_approle_capability'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlfaUser',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='appuser',
            name='user',
        ),
        migrations.AlterField(
            model_name='approle',
            name='appuser',
            field=models.ForeignKey(to='home.AlfaUser'),
        ),
        migrations.DeleteModel(
            name='AppUser',
        ),
    ]
