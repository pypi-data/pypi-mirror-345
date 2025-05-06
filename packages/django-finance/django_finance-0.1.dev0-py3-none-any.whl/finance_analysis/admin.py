from django.contrib import admin
from .models import Filter
from .models import Group
from .models import Tag


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = ['field', 'operator', 'pattern']
    list_filter = ['field', 'operator']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'parent',
        'level',
        ]
    list_filter = [
        'parent',
        'level',
        ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']


