# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0022_auto_20141127_0057'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletin',
            name='currently_encrypted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
