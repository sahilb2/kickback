# Generated by Django 2.2.6 on 2019-10-31 02:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sessions',
            fields=[
                ('session_id', models.CharField(max_length=6, primary_key=True, serialize=False, verbose_name='Session ID')),
                ('session_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Session Name')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='User ID')),
                ('username', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SessionSongs',
            fields=[
                ('song_id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='Song ID')),
                ('spotify_uri', models.CharField(max_length=22, verbose_name='Song URI')),
                ('next_song_id', models.IntegerField(blank=True, null=True, verbose_name='Next Song ID')),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Sessions', verbose_name='Session ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.User', verbose_name='Added By User')),
            ],
        ),
        migrations.AddField(
            model_name='sessions',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.User', verbose_name='Session Owner'),
        ),
    ]
