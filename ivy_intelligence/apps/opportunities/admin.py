from django.contrib import admin
from .models import Opportunity, ScrapingLog


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'university', 'domain', 'opportunity_type', 'is_active', 'deadline', 'scraped_at')
    list_filter = ('university', 'domain', 'opportunity_type', 'is_active')
    search_fields = ('title', 'description', 'tags')
    list_editable = ('is_active',)
    date_hierarchy = 'scraped_at'
    readonly_fields = ('scraped_at', 'updated_at')


@admin.register(ScrapingLog)
class ScrapingLogAdmin(admin.ModelAdmin):
    list_display = ('university', 'status', 'opportunities_found', 'new_opportunities', 'started_at')
    list_filter = ('university', 'status')
    readonly_fields = ('started_at', 'finished_at')
