# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('secure_witness', '0015_auto_20141123_1356'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBul',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('location', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('docfile', models.FileField(null=True, upload_to=b'documents', blank=True)),
                ('doc_key', models.CharField(default=b'', max_length=200)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='permission',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='description',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='doc_key',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='docfile',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='location',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='title',
        ),
        migrations.AddField(
            model_name='bulletin',
            name='reader',
            field=models.ForeignKey(related_name='reader', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bulletin',
            name='author',
            field=models.ForeignKey(related_name='author', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
