# Generated by Django 2.0 on 2020-07-23 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b2b', '0005_twitter_comment_management_sentiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitter_comment_management',
            name='sentiment_uppercase',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
