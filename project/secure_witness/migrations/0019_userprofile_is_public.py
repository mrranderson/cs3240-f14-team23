# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0018_remove_bulletin_reader'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_public',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
