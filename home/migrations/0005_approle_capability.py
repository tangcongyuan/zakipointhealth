# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20151201_0624'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=111)),
                ('appuser', models.ForeignKey(to='home.AppUser')),
                ('company', models.ForeignKey(to='home.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Capability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=48)),
                ('roles', models.ManyToManyField(related_name='allowed', to='home.AppRole')),
            ],
        ),
    ]
