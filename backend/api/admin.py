from django.contrib import admin
from .models import WorkCategory, WorkItem, Estimate, EstimateLine


@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    search_fields = ['name']
    list_filter = ['user']


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'avg_price', 'user']
    search_fields = ['name']
    list_filter = ['category', 'user']
    list_editable = ['avg_price']


class EstimateLineInline(admin.TabularInline):
    model = EstimateLine
    extra = 0
    fields = ['work_item', 'custom_name', 'unit', 'price', 'quantity', 'total']


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'updated_at']
    search_fields = ['name', 'user__username']
    list_filter = ['user']
    inlines = [EstimateLineInline]


@admin.register(EstimateLine)
class EstimateLineAdmin(admin.ModelAdmin):
    list_display = ['estimate', 'work_item', 'price', 'quantity', 'total']
    list_filter = ['estimate__user']
