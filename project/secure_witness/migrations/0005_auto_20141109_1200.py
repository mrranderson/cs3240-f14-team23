# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0004_auto_20141109_1158'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={'permissions': (('decrypt_document', 'Can decrypt and use the file'),)},
        ),
    ]
