# Generated by Django 2.0 on 2020-10-22 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b2b', '0035_removed_fb_page_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='fb_is_page_management',
            name='ig_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
