from django.contrib import admin
from .models import Application, AutoFillLog


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'status', 'auto_submitted', 'applied_at')
    list_filter = ('status', 'auto_submitted')
    search_fields = ('student__username', 'opportunity__title')
    list_editable = ('status',)


@admin.register(AutoFillLog)
class AutoFillLogAdmin(admin.ModelAdmin):
    list_display = ('application', 'success', 'attempted_at')
    list_filter = ('success',)
