from django.contrib import admin
from .models import Approval, EvaluatorFeedback, Goal, MemberFeedback, SubTask


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 0


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'status', 'owner', 'evaluator', 'completion_percentage', 'due_date')
    list_filter = ('level', 'status', 'category')
    search_fields = ('title', 'description')
    inlines = [SubTaskInline]


admin.site.register(Approval)
admin.site.register(MemberFeedback)
admin.site.register(EvaluatorFeedback)
