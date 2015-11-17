# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Capability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=48)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('group', models.OneToOneField(primary_key=True, serialize=False, to='auth.Group')),
                ('co_type', models.CharField(max_length=10, choices=[(b'admin_co', b'Administration'), (b'channel', b'Channel'), (b'employer', b'Employer')])),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=48)),
            ],
        ),
        migrations.CreateModel(
            name='AppUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user', home.models.AuthObject),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='capability',
            name='roles',
            field=models.ManyToManyField(related_name='allowed', to='home.UserRole'),
        ),
    ]
