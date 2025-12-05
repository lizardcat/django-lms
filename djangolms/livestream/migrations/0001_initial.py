# Generated migration for livestream app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveStream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('stream_key', models.CharField(editable=False, max_length=100, unique=True)),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('LIVE', 'Live'), ('ENDED', 'Ended'), ('CANCELLED', 'Cancelled')], default='SCHEDULED', max_length=20)),
                ('scheduled_start', models.DateTimeField()),
                ('scheduled_end', models.DateTimeField()),
                ('actual_start', models.DateTimeField(blank=True, null=True)),
                ('actual_end', models.DateTimeField(blank=True, null=True)),
                ('enable_recording', models.BooleanField(default=True)),
                ('recording_url', models.URLField(blank=True)),
                ('allow_chat', models.BooleanField(default=True)),
                ('allow_qa', models.BooleanField(default=True)),
                ('max_viewers', models.IntegerField(default=1000, help_text='Maximum concurrent viewers')),
                ('current_viewers', models.IntegerField(default=0)),
                ('peak_viewers', models.IntegerField(default=0)),
                ('total_views', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='livestreams', to='courses.course')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_streams', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-scheduled_start'],
            },
        ),
        migrations.CreateModel(
            name='VideoConference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Meeting title', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Meeting description/agenda')),
                ('room_name', models.CharField(editable=False, help_text='Unique Jitsi room identifier', max_length=200, unique=True)),
                ('scheduled_start', models.DateTimeField(help_text='Scheduled start time')),
                ('scheduled_end', models.DateTimeField(help_text='Scheduled end time')),
                ('actual_start', models.DateTimeField(blank=True, null=True)),
                ('actual_end', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('LIVE', 'Live'), ('ENDED', 'Ended'), ('CANCELLED', 'Cancelled')], default='SCHEDULED', max_length=20)),
                ('require_password', models.BooleanField(default=False, help_text='Require password to join')),
                ('password', models.CharField(blank=True, help_text='Meeting password (if required)', max_length=50)),
                ('enable_recording', models.BooleanField(default=False, help_text='Allow meeting recording')),
                ('enable_lobby', models.BooleanField(default=False, help_text='Participants wait in lobby for host approval')),
                ('max_participants', models.IntegerField(default=50, help_text='Maximum number of participants')),
                ('restrict_to_course', models.BooleanField(default=True, help_text='Only enrolled students can join (if linked to course)')),
                ('recording_url', models.URLField(blank=True, help_text='Recording URL after meeting ends')),
                ('total_participants', models.IntegerField(default=0)),
                ('peak_participants', models.IntegerField(default=0)),
                ('duration_minutes', models.IntegerField(default=0, help_text='Actual meeting duration')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(blank=True, help_text='Optional: link to a course', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='video_conferences', to='courses.course')),
                ('host', models.ForeignKey(help_text='Meeting host (instructor or student)', on_delete=django.db.models.deletion.CASCADE, related_name='hosted_conferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Video Conference',
                'verbose_name_plural': 'Video Conferences',
                'ordering': ['-scheduled_start'],
            },
        ),
        migrations.CreateModel(
            name='StreamViewer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('is_currently_watching', models.BooleanField(default=True)),
                ('total_watch_time_seconds', models.IntegerField(default=0)),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viewers', to='livestream.livestream')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watched_streams', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StreamRecording',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('video_file', models.FileField(blank=True, null=True, upload_to='stream_recordings/%Y/%m/')),
                ('video_url', models.URLField(blank=True, help_text='External URL if hosted elsewhere')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='stream_thumbnails/')),
                ('duration_seconds', models.IntegerField(default=0)),
                ('file_size_mb', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_public', models.BooleanField(default=False, help_text='Allow non-enrolled students to view')),
                ('view_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('stream', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='recording', to='livestream.livestream')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StreamChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_pinned', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='livestream.livestream')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='QAQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('is_answered', models.BooleanField(default=False)),
                ('answer', models.TextField(blank=True)),
                ('answered_at', models.DateTimeField(blank=True, null=True)),
                ('upvotes', models.IntegerField(default=0)),
                ('is_pinned', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('answered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='answered_questions', to=settings.AUTH_USER_MODEL)),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qa_questions', to='livestream.livestream')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stream_questions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-upvotes', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='QuestionUpvote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upvote_records', to='livestream.qaquestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('question', 'user')},
            },
        ),
        migrations.CreateModel(
            name='VideoConferenceParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('duration_minutes', models.IntegerField(default=0, help_text='Time spent in conference (minutes)')),
                ('camera_on', models.BooleanField(default=True)),
                ('microphone_on', models.BooleanField(default=True)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='livestream.videoconference')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conference_participations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Conference Participant',
                'verbose_name_plural': 'Conference Participants',
                'ordering': ['-joined_at'],
            },
        ),
        migrations.AddIndex(
            model_name='livestream',
            index=models.Index(fields=['course', 'status'], name='livestream__course__6c2b47_idx'),
        ),
        migrations.AddIndex(
            model_name='livestream',
            index=models.Index(fields=['instructor', '-scheduled_start'], name='livestream__instruc_8d4e2f_idx'),
        ),
        migrations.AddIndex(
            model_name='streamviewer',
            index=models.Index(fields=['stream', 'is_currently_watching'], name='livestream__stream__7a3c94_idx'),
        ),
        migrations.AddIndex(
            model_name='streamchat',
            index=models.Index(fields=['stream', '-created_at'], name='livestream__stream__9b2e5a_idx'),
        ),
        migrations.AddIndex(
            model_name='qaquestion',
            index=models.Index(fields=['stream', '-upvotes'], name='livestream__stream__4c8d1f_idx'),
        ),
        migrations.AddIndex(
            model_name='videoconference',
            index=models.Index(fields=['course', '-scheduled_start'], name='livestream__course__3f5a2e_idx'),
        ),
        migrations.AddIndex(
            model_name='videoconference',
            index=models.Index(fields=['host', '-scheduled_start'], name='livestream__host_id_7e9b1c_idx'),
        ),
        migrations.AddIndex(
            model_name='videoconference',
            index=models.Index(fields=['status', '-scheduled_start'], name='livestream__status_6d4c8f_idx'),
        ),
        migrations.AddIndex(
            model_name='videoconferenceparticipant',
            index=models.Index(fields=['conference', '-joined_at'], name='livestream__confere_2a5e9b_idx'),
        ),
        migrations.AddIndex(
            model_name='videoconferenceparticipant',
            index=models.Index(fields=['user', '-joined_at'], name='livestream__user_id_1c4f7d_idx'),
        ),
    ]
