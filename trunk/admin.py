from django.contrib import admin

from models import Mitglied
from models import Sektion
from models import Postenart
from models import Bewertungsart

admin.site.register(Mitglied)
admin.site.register(Sektion)
admin.site.register(Postenart)
admin.site.register(Bewertungsart)
