from django.contrib import admin
from django.utils import timezone
from .models import Achievement, ScoreHistory
from .engine import update_student_score


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('student', 'category', 'title', 'raw_score', 'verified', 'achieved_on', 'created_at')
    list_filter = ('category', 'verified')
    search_fields = ('student__user__username', 'title')
    list_editable = ('verified', 'raw_score')
    actions = ['verify_and_recalculate']

    def verify_and_recalculate(self, request, queryset):
        """Admin action: Verify selected achievements and recalculate scores."""
        for achievement in queryset:
            achievement.verified = True
            achievement.verified_by = request.user.username
            achievement.save()
            update_student_score(achievement.student, reason=f"Admin verified: {achievement.title}")
        self.message_user(request, f"Verified {queryset.count()} achievements and updated InCoScores.")
    verify_and_recalculate.short_description = "Verify & recalculate InCoScore"


@admin.register(ScoreHistory)
class ScoreHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'score', 'reason', 'recorded_at')
    list_filter = ('recorded_at',)
    readonly_fields = ('recorded_at',)
