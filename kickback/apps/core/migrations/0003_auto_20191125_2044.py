# Generated by Django 2.2.6 on 2019-11-25 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_sessionsongs_is_curr_song'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sessionsongs',
            old_name='session_id',
            new_name='session',
        ),
    ]
