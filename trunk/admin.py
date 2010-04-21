from django.contrib import admin

from models import Mitglied
from models import Sektion
from models import Postenart
from models import Bewertungsart

class MitgliedAdmin(admin.ModelAdmin):
    list_display = ('name', 'vorname', 'sektion', 'geburtsdatum', 'nummer',)
    search_fields = ('name', 'vorname', 'sektion__name',)
    actions_on_top = False
    actions_on_bottom = True

admin.site.register(Mitglied, MitgliedAdmin)
admin.site.register(Sektion)
admin.site.register(Postenart)
admin.site.register(Bewertungsart)
