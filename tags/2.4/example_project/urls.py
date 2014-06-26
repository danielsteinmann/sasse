from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Authentication
    (r'^accounts/login/$', login, {}, 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', logout, {}, 'django.contrib.auth.views.logout'),

    # Admin site:
    (r'^admin/', include(admin.site.urls)),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT }),

    (r'^', include('sasse.urls')),
)
