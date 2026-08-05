from django.contrib import admin

from .models import Estimate, EstimateLine, WorkCategory, WorkItem


@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_system']
    search_fields = ['name']


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'avg_price', 'user', 'is_system']
    list_filter = ['category']
    search_fields = ['name']


class EstimateLineInline(admin.TabularInline):
    model = EstimateLine
    extra = 0


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'updated_at']
    inlines = [EstimateLineInline]
