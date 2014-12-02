# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0025_remove_document_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bulletin',
            name='private_folder',
        ),
    ]
