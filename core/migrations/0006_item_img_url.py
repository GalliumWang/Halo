# Generated by Django 2.2.14 on 2020-10-30 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201030_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='img_url',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
