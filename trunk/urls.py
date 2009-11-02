from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
import views

urlpatterns = patterns('',
    url(r'^$',
        views.wettkaempfe_get, name="wettkaempfe_get"),
    (r'^add/$',
        views.wettkaempfe_add, {}, "wettkaempfe_add"),
    (r'^(?P<jahr>\d+)/$',
        views.wettkaempfe_by_year, {}, "wettkaempfe_by_year"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/$',
        views.wettkampf_get, {}, "wettkampf_get"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/update/$',
        views.wettkampf_update, {}, "wettkampf_update"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/delete/$',
        views.wettkampf_delete_confirm, {}, "wettkampf_delete_confirm"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/add/$',
        views.disziplinen_add, {}, "disziplinen_add"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/$',
        views.disziplin_get, {}, "disziplin_get"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/update/$',
        views.disziplin_update, {}, "disziplin_update"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/delete/$',
        views.disziplin_delete_confirm, {}, "disziplin_delete_confirm"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/posten/$',
        views.posten_list, {}, "posten_list"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/posten/(?P<posten>[-\w]+)$',
        views.posten_get, {}, "posten_get"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/posten/(?P<posten>[-\w]+)/update/$',
        views.posten_update, {}, "posten_update"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/posten/(?P<posten>[-\w]+)/delete/$',
        views.posten_delete_confirm, {}, "posten_delete_confirm"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/startliste/$',
        views.startliste, {}, "startliste"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/teilnehmer/(?P<startnummer>\d+)/$',
        views.teilnehmer_get, {}, "teilnehmer_get"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/teilnehmer/(?P<startnummer>\d+)/update/$',
        views.teilnehmer_update, {}, "teilnehmer_update"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/teilnehmer/(?P<startnummer>\d+)/delete/$',
        views.teilnehmer_delete_confirm, {}, "teilnehmer_delete_confirm"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/bewertungen/$',
        views.bewertungen, {}, "bewertungen"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/postenblatt/$',
        views.postenblatt, {}, "postenblatt"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/postenblatt/update/$',
        views.postenblatt_update, {}, "postenblatt_update"),
)

#---- Wettkaempfe
#
# wettkaempfe/ 
#     GET: wettkaempfe_get: List of wettkaempfe
#
# wettkaempfe/create/
#     GET: wettkaempfe_create: Form with 'create' button
#     POST: wettkaempfe_post: Add new wettkampf
#
# wettkaempfe/2008/
#     GET: wettkaempfe_by_year: Liste filtered by year
#
# wettkaempfe/2008/faellbaumcup/
#     GET: wettkampf_get: Show attributes and list of disziplines
#     PUT: wettkampf_put
#     DELETE: wettkampf_delete
#
# wettkaempfe/2008/faellbaumcup/update/
#     GET: wettkampf_update: Form with 'update' button
#     POST: wettkampf_put: Execupte update
#
# wettkaempfe/2008/faellbaumcup/delete/
#     GET: wettkampf_confirm_delete: Confirm message, return delete form
#     POST: wettkampf_delete: Execute delete
#
