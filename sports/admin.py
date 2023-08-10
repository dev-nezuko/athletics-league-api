from django.contrib import admin

from .models import Player, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("city", "mascot")
    search_fields = ("city", "mascot")


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name")
    search_fields = ("first_name", "last_name")
    filter_horizontal = ("teams",)
