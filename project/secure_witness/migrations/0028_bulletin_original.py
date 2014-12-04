# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0027_bulletin_private_folders'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletin',
            name='original',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
