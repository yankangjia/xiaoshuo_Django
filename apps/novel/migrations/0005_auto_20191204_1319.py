# Generated by Django 2.0.2 on 2019-12-04 05:19

from django.db import migrations
import shortuuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0004_auto_20191204_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novelchapter',
            name='id',
            field=shortuuidfield.fields.ShortUUIDField(blank=True, editable=False, max_length=22, primary_key=True, serialize=False),
        ),
    ]
