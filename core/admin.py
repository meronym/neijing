from django.contrib import admin

from core.models import Condition, Disharmony, Manifestation


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ['name', 'updated_at']


@admin.register(Disharmony)
class DisharmonyAdmin(admin.ModelAdmin):
    list_display = ['name', 'updated_at']


@admin.register(Manifestation)
class ManifestationAdmin(admin.ModelAdmin):
    list_display = ['name']
