# Generated by Django 2.0 on 2020-09-10 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b2b', '0025_canned_response_management_social_accounts'),
    ]

    operations = [
        migrations.CreateModel(
            name='persona_location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='customer_persona',
            name='loaction_id',
            field=models.ManyToManyField(to='b2b.persona_location'),
        ),
    ]
