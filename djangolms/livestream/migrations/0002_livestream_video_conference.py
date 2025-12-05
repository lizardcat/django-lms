# Generated migration for LiveStream Jitsi integration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('livestream', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='livestream',
            name='video_conference',
            field=models.OneToOneField(
                blank=True,
                help_text='Associated Jitsi video conference for actual streaming',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='livestream',
                to='livestream.videoconference'
            ),
        ),
    ]
