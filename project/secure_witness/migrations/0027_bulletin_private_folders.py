# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0026_remove_bulletin_private_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletin',
            name='private_folders',
            field=models.ManyToManyField(related_name='bulletin_private', null=True, to='secure_witness.Folder'),
            preserve_default=True,
        ),
    ]
