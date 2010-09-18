# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Mitglied
from models import Sektion
from models import Disziplinart
from models import Postenart
from models import Bewertungsart

class MitgliedAdmin(admin.ModelAdmin):
    list_display = ('name', 'vorname', 'sektion', 'geburtsdatum', 'nummer',)
    search_fields = ('name', 'vorname', 'sektion__name',)
    actions_on_top = False
    actions_on_bottom = True

class MembershipInline(admin.TabularInline):
    model = Postenart.disziplinarten.through
    extra = 0  #Man kann mit einem JavaScript-Link neue dazufügen


class BewertungsartInline(admin.TabularInline):
    model = Bewertungsart
    extra = 0  #Man kann mit einem JavaScript-Link neue dazufügen

class DisziplinartAdmin(admin.ModelAdmin):
    inlines = [
            MembershipInline,
            ]

class PostenartAdmin(admin.ModelAdmin):
    inlines = [
            BewertungsartInline,
            ]

admin.site.register(Mitglied, MitgliedAdmin)
admin.site.register(Sektion)
admin.site.register(Disziplinart, DisziplinartAdmin)
admin.site.register(Postenart, PostenartAdmin)
