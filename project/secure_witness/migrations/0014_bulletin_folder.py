# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0013_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletin',
            name='folder',
            field=models.ForeignKey(to='secure_witness.Folder', null=True),
            preserve_default=True,
        ),
    ]
