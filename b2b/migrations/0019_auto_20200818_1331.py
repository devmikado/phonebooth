# Generated by Django 2.0 on 2020-08-18 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('b2b', '0018_auto_20200818_1328'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personaculturemaster',
            old_name='social_auth_id',
            new_name='culture_id',
        ),
        migrations.RenameField(
            model_name='personalocationsmaster',
            old_name='social_auth_id',
            new_name='loaction_id',
        ),
    ]
