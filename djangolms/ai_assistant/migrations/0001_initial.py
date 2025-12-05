# Generated migration for ai_assistant app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assignments', '0001_initial'),
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AIInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('QUIZ_HINT', 'Quiz Hint'), ('QUIZ_EXPLANATION', 'Quiz Explanation'), ('ANSWER_REVIEW', 'Answer Review'), ('CONCEPT_HELP', 'Concept Help'), ('GRADING_ASSIST', 'Grading Assistance'), ('FEEDBACK_GEN', 'Feedback Generation'), ('STUDENT_ANALYTICS', 'Student Analytics'), ('PERFORMANCE_PREDICT', 'Performance Prediction')], max_length=20)),
                ('user_input', models.TextField()),
                ('ai_response', models.TextField()),
                ('model_used', models.CharField(default='claude-3-5-sonnet-20241022', max_length=50)),
                ('tokens_used', models.IntegerField(default=0)),
                ('response_time_ms', models.IntegerField(default=0)),
                ('helpful', models.BooleanField(blank=True, null=True)),
                ('feedback_comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assignment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assignments.assignment')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('submission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assignments.submission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_interactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='QuizAssistanceSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hints_requested', models.IntegerField(default=0)),
                ('explanations_requested', models.IntegerField(default=0)),
                ('session_start', models.DateTimeField(auto_now_add=True)),
                ('session_end', models.DateTimeField(blank=True, null=True)),
                ('helpful_interactions', models.JSONField(default=list)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assignments.assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-session_start'],
            },
        ),
        migrations.CreateModel(
            name='StudentAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_grade', models.CharField(blank=True, max_length=5)),
                ('risk_level', models.CharField(choices=[('LOW', 'Low Risk'), ('MEDIUM', 'Medium Risk'), ('HIGH', 'High Risk'), ('CRITICAL', 'Critical Risk')], default='LOW', max_length=20)),
                ('learning_gaps', models.JSONField(default=list, help_text='Identified knowledge gaps')),
                ('strengths', models.JSONField(default=list, help_text="Student's strong areas")),
                ('recommendations', models.JSONField(default=list, help_text='Recommended interventions')),
                ('engagement_score', models.DecimalField(decimal_places=2, default=0, help_text='0-100 score', max_digits=5)),
                ('participation_trend', models.CharField(choices=[('IMPROVING', 'Improving'), ('STABLE', 'Stable'), ('DECLINING', 'Declining')], default='STABLE', max_length=20)),
                ('summary', models.TextField(help_text='AI-generated summary of student performance')),
                ('analyzed_assignments_count', models.IntegerField(default=0)),
                ('last_analyzed', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_analytics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Student Analytics',
                'ordering': ['-last_analyzed'],
                'unique_together': {('student', 'course')},
            },
        ),
        migrations.CreateModel(
            name='AIGradingSuggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggested_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('confidence_score', models.DecimalField(decimal_places=2, help_text='AI confidence (0-100)', max_digits=3)),
                ('feedback', models.TextField()),
                ('strengths', models.JSONField(default=list, help_text='List of identified strengths')),
                ('areas_for_improvement', models.JSONField(default=list, help_text='List of areas to improve')),
                ('rubric_scores', models.JSONField(blank=True, default=dict, help_text='Breakdown by rubric criteria')),
                ('requires_human_review', models.BooleanField(default=False)),
                ('flagged_reason', models.TextField(blank=True, help_text='Why flagged for human review')),
                ('accepted', models.BooleanField(blank=True, null=True)),
                ('instructor_notes', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ai_suggestion', to='assignments.submission')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='aiinteraction',
            index=models.Index(fields=['user', '-created_at'], name='ai_assistan_user_id_8b3f44_idx'),
        ),
        migrations.AddIndex(
            model_name='aiinteraction',
            index=models.Index(fields=['interaction_type', '-created_at'], name='ai_assistan_interac_7e5c91_idx'),
        ),
    ]
