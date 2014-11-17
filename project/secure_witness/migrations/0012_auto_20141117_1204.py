# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0011_auto_20141117_1043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='pub_key',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='private_key',
            field=models.CharField(default=b'', max_length=500),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='public_key',
            field=models.CharField(default=b'', max_length=500),
            preserve_default=True,
        ),
    ]
