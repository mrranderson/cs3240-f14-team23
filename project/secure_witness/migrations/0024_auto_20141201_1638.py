# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0023_bulletin_currently_encrypted'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={},
        ),
        migrations.AddField(
            model_name='document',
            name='doc_key',
            field=models.CharField(default=b'', max_length=200),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='docfile',
            field=models.FileField(null=True, upload_to=b'documents', blank=True),
            preserve_default=True,
        ),
    ]
