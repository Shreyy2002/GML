from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('level', models.CharField(choices=[('COMPANY', 'Company'), ('TEAM', 'Team'), ('INDIVIDUAL', 'Individual')], db_index=True, max_length=20)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('PENDING', 'Pending'), ('ACTIVE', 'Active'), ('COMPLETED', 'Completed'), ('SCORED', 'Scored'), ('REJECTED', 'Rejected')], db_index=True, default='DRAFT', max_length=20)),
                ('due_date', models.DateField(db_index=True)),
                ('weightage', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('category', models.CharField(db_index=True, max_length=120)),
                ('completion_percentage', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('final_score', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evaluator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goals_to_evaluate', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_goals', to=settings.AUTH_USER_MODEL)),
                ('parent_goal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_goals', to='goals.goal')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goals', to='teams.team')),
            ],
        ),
        migrations.CreateModel(
            name='SubTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('is_done', models.BooleanField(default=False)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_tasks', to='goals.goal')),
            ],
        ),
        migrations.CreateModel(
            name='Approval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approvals', to='goals.goal')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goal_approvals', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MemberFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('self_reflection', models.TextField()),
                ('delivered', models.TextField()),
                ('improvement', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('goal', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='member_feedback', to='goals.goal')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_feedbacks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EvaluatorFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quality', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('ownership', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('communication', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('timeliness', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('initiative', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField()),
                ('final_rating', models.CharField(choices=[('BELOW', 'Below Expectations'), ('MEETS', 'Meets Expectations'), ('ABOVE', 'Above Expectations')], max_length=10)),
                ('numeric_score', models.DecimalField(decimal_places=2, max_digits=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluator_feedbacks', to=settings.AUTH_USER_MODEL)),
                ('goal', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='evaluator_feedback', to='goals.goal')),
            ],
        ),
        migrations.AddIndex(model_name='goal', index=models.Index(fields=['status', 'level'], name='goals_goal_status_64f114_idx')),
        migrations.AddIndex(model_name='goal', index=models.Index(fields=['owner', 'status'], name='goals_goal_owner_i_819487_idx')),
        migrations.AddIndex(model_name='goal', index=models.Index(fields=['team', 'status'], name='goals_goal_team_id_5076cc_idx')),
        migrations.AddIndex(model_name='goal', index=models.Index(fields=['due_date', 'status'], name='goals_goal_due_dat_c2d37a_idx')),
        migrations.AddIndex(model_name='subtask', index=models.Index(fields=['goal', 'is_done'], name='goals_subta_goal_id_1b279a_idx')),
        migrations.AddIndex(model_name='approval', index=models.Index(fields=['goal', 'created_at'], name='goals_appro_goal_id_67fe11_idx')),
        migrations.AddIndex(model_name='approval', index=models.Index(fields=['reviewer'], name='goals_appro_reviewer_2be41a_idx')),
    ]
