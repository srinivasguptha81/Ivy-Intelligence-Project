from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'year_of_study', 'cgpa', 'incoscore', 'profile_complete')
    list_filter = ('year_of_study', 'profile_complete')
    search_fields = ('user__username', 'user__email', 'university')
    readonly_fields = ('incoscore', 'created_at', 'updated_at')
