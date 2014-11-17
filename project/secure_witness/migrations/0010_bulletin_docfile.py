# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0009_bulletin_is_encrypted'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletin',
            name='docfile',
            field=models.FileField(default=b'settings.MEDIA_ROOT/temp', upload_to=b'documents'),
            preserve_default=True,
        ),
    ]
