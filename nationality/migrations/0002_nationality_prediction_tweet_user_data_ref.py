# Generated by Django 2.0 on 2020-07-03 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nationality', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='nationality_prediction',
            name='tweet_user_data_ref',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='nationality.tweet_user_data'),
            preserve_default=False,
        ),
    ]
