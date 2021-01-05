# Generated by Django 2.0 on 2020-07-17 11:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social_django', '0010_uid_db_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='canned_response_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('positive_response_text', models.TextField(blank=True, null=True)),
                ('neutral_response_text', models.TextField(blank=True, null=True)),
                ('negative_response_text', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Canned Response Details',
                'verbose_name_plural': 'Canned Responses',
            },
        ),
        migrations.CreateModel(
            name='customer_chiptiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chip_title', models.CharField(max_length=200, null=True)),
                ('capture_facebook', models.BooleanField(default=False)),
                ('capture_twitter', models.BooleanField(default=False)),
                ('capture_instagram', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='customer_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('company_logo', models.ImageField(default='media/no-img.jpg', upload_to='media/')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('mobile_no', models.PositiveIntegerField(blank=True, null=True)),
                ('business_info', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Social Media Profiles',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='fb_comment_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField()),
                ('message', models.TextField()),
                ('fb_comment_id', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_replied', models.BooleanField(default=False)),
                ('raw_response', models.TextField(blank=True)),
                ('customer_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management')),
            ],
        ),
        migrations.CreateModel(
            name='fb_is_page_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_access_token', models.CharField(max_length=255)),
                ('app_access_token', models.CharField(max_length=255)),
                ('page_access_token', models.CharField(max_length=255)),
                ('client_token', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('customer_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management')),
            ],
            options={
                'verbose_name': 'FB IS Management Details',
                'verbose_name_plural': 'FB IS Management Details',
            },
        ),
        migrations.CreateModel(
            name='fb_post_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField()),
                ('message', models.TextField(blank=True, null=True)),
                ('fb_post_id', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('raw_response', models.TextField(blank=True)),
                ('customer_chip_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_chiptiles')),
                ('customer_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management')),
            ],
        ),
        migrations.CreateModel(
            name='ig_comment_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField()),
                ('message', models.TextField()),
                ('ig_comment_id', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_replied', models.BooleanField(default=False)),
                ('raw_response', models.TextField(blank=True)),
                ('customer_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management')),
            ],
        ),
        migrations.CreateModel(
            name='ig_post_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField()),
                ('message', models.TextField(blank=True, null=True)),
                ('ig_post_id', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('raw_response', models.TextField(blank=True)),
                ('customer_chip_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_chiptiles')),
                ('customer_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management')),
            ],
        ),
        migrations.CreateModel(
            name='twitter_comment_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField()),
                ('message', models.TextField()),
                ('tweet_reply_id', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_replied', models.BooleanField(default=False)),
                ('raw_response', models.TextField(blank=True)),
                ('resposne_sent', models.TextField(blank=True, null=True)),
                ('customer_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management')),
            ],
        ),
        migrations.CreateModel(
            name='twitter_post_management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField()),
                ('message', models.TextField(blank=True, null=True)),
                ('tweet_id', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('raw_response', models.TextField(blank=True)),
                ('customer_chip_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_chiptiles')),
                ('customer_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management')),
                ('twitter_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_django.UserSocialAuth')),
            ],
        ),
        migrations.AddField(
            model_name='twitter_comment_management',
            name='twitter_post_ref',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.twitter_post_management'),
        ),
        migrations.AddField(
            model_name='ig_comment_management',
            name='ig_post_ref',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.ig_post_management'),
        ),
        migrations.AddField(
            model_name='fb_comment_management',
            name='fb_post_ref',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.fb_post_management'),
        ),
        migrations.AddField(
            model_name='customer_chiptiles',
            name='customer_ref',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management'),
        ),
        migrations.AddField(
            model_name='customer_chiptiles',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='canned_response_management',
            name='customer_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b2b.customer_management'),
        ),
    ]
