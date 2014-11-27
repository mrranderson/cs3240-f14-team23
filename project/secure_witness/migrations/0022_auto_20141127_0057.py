# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0021_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletin',
            name='private_folder',
            field=models.ForeignKey(related_name='bulletin_private', to='secure_witness.Folder', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bulletin',
            name='folder',
            field=models.ForeignKey(related_name='bulletin_parent', to='secure_witness.Folder', null=True),
            preserve_default=True,
        ),
    ]
