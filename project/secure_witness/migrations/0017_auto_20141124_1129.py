# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secure_witness', '0016_auto_20141124_1128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permission',
            name='reader',
        ),
        migrations.DeleteModel(
            name='Permission',
        ),
        migrations.RemoveField(
            model_name='userbul',
            name='author',
        ),
        migrations.DeleteModel(
            name='UserBul',
        ),
    ]
