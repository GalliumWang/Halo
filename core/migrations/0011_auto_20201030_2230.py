# Generated by Django 2.2.14 on 2020-10-30 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20201030_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='rating_sum',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
