# Generated by Django 2.0 on 2020-07-19 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b2b', '0003_auto_20200718_0559'),
    ]

    def insertData(apps, schema_editor):
        sentiment = ['positive', 'negative', 'neutral']
        sentimentMaster = apps.get_model('b2b', 'sentimentMaster')
        for i in sentiment:
            sentiment_data = sentimentMaster(sentiment=i)
            sentiment_data.save()

    operations = [
        migrations.CreateModel(
            name='sentimentMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentiment', models.CharField(blank=True, max_length=255, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
        ),

        migrations.RunPython(insertData),
    ]
