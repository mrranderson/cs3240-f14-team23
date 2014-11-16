# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0008_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletin',
            name='is_encrypted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
