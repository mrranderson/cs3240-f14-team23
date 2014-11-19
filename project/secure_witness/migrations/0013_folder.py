# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0012_auto_20141117_1204'),
    ]

    operations = [
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('parent_folder', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='secure_witness.Folder', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
