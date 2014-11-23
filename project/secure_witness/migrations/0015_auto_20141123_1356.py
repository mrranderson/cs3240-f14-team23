# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('secure_witness', '0014_bulletin_folder'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('location', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('docfile', models.FileField(null=True, upload_to=b'documents', blank=True)),
                ('doc_key', models.CharField(default=b'', max_length=200)),
                ('reader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bulletin',
            name='doc_key',
            field=models.CharField(default=b'', max_length=200),
            preserve_default=True,
        ),
    ]
