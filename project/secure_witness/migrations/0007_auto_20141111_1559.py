# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('secure_witness', '0006_auto_20141109_1204'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=200)),
                ('has_read', models.BooleanField(default=False)),
                ('message', models.TextField()),
                ('is_request', models.BooleanField(default=False)),
                ('is_update', models.BooleanField(default=False)),
                ('bulletin', models.ForeignKey(to='secure_witness.Bulletin')),
                ('recipient', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bulletin',
            name='is_public',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bulletin',
            name='is_searchable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
