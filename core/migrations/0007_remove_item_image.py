# Generated by Django 2.2.14 on 2020-10-30 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_item_img_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='image',
        ),
    ]
