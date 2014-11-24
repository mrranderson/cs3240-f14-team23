# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0017_auto_20141124_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bulletin',
            name='reader',
        ),
    ]
