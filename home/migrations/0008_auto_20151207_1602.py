# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20151203_0645'),
    ]

    operations = [
        migrations.CreateModel(
            name='Power',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=48)),
            ],
        ),
        migrations.RemoveField(
            model_name='capability',
            name='roles',
        ),
        migrations.DeleteModel(
            name='Capability',
        ),
        migrations.AddField(
            model_name='approle',
            name='powers',
            field=models.ManyToManyField(to='home.Power'),
        ),
    ]
