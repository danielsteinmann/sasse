from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
import views

sektionsfahren_patterns = patterns('',
    (r'^$',
        views.sektionsfahren_get, {}, "sektionsfahren_get"),
    (r'^startliste/$',
        views.sektionsfahren_startliste, {}, "sektionsfahren_startliste"),
    (r'^gruppe/add/$',
        views.sektionsfahren_gruppe_add, {}, "sektionsfahren_gruppe_add"),
    (r'^gruppe/(?P<gruppe>[-\w]+)/$',
        views.sektionsfahren_gruppe_get, {}, "sektionsfahren_gruppe_get"),
    (r'^gruppe/(?P<gruppe>[-\w]+)/update/$',
        views.sektionsfahren_gruppe_update, {}, "sektionsfahren_gruppe_update"),
    (r'^gruppe/(?P<gruppe>[-\w]+)/delete/$',
        views.sektionsfahren_gruppe_delete, {}, "sektionsfahren_gruppe_delete"),
    (r'^gruppe/(?P<gruppe>[-\w]+)/abzug/$',
        views.sektionsfahren_gruppe_abzug, {}, "sektionsfahren_gruppe_abzug"),
    (r'^gruppe/(?P<gruppe>[-\w]+)/schiff/$',
        views.sektionsfahren_schiff_post, {}, "sektionsfahren_schiff_post"),
    (r'^gruppe/(?P<gruppe>[-\w]+)/schiff/(?P<position>\d+)/update/$',
        views.sektionsfahren_schiff_update, {}, "sektionsfahren_schiff_update"),
    (r'^postenblatt/$',
        views.sektionsfahren_postenblatt, {}, "sektionsfahren_postenblatt"),
    (r'^postenblatt/(?P<posten>[-\w]+)/$',
        views.sektionsfahren_postenblatt, {}, "sektionsfahren_postenblatt"),
    (r'^rangliste/$',
        views.sektionsfahren_rangliste, {}, "sektionsfahren_rangliste"),
    (r'^rangliste/pdf/$',
        views.sektionsfahren_rangliste_pdf, {}, "sektionsfahren_rangliste_pdf"),
    (r'^rangliste-gruppe/$',
        views.sektionsfahren_rangliste_gruppe, {}, "sektionsfahren_rangliste_gruppe"),
    (r'^rangliste-schiffe/$',
        views.sektionsfahren_rangliste_schiff, {}, "sektionsfahren_rangliste_schiff"),
    (r'^kranzlimiten/$',
        views.sektionsfahren_kranzlimiten, {}, "sektionsfahren_kranzlimiten"),
    (r'^kranzlimiten/update/$',
        views.sektionsfahren_kranzlimiten_update, {}, "sektionsfahren_kranzlimiten_update"),
    (r'^notenblatt/(?P<sektion_name>[-\w\s]+)/$',
        views.sektionsfahren_notenblatt, {}, "sektionsfahren_notenblatt"),
    (r'^notenblatt-gruppe/(?P<gruppe>[-\w]+)/$',
        views.sektionsfahren_notenblatt_gruppe, {}, "sektionsfahren_notenblatt_gruppe"),
)

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
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/sektionsfahren/',
        include(sektionsfahren_patterns)),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/doppelstarter-einzelfahren/$',
        views.doppelstarter_einzelfahren, {}, "doppelstarter_einzelfahren"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/startlisten-einzelfahren-export/$',
        views.startlisten_einzelfahren_export, {}, "startlisten_einzelfahren_export"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/startlisten-einzelfahren-import/$',
        views.startlisten_einzelfahren_import, {}, "startlisten_einzelfahren_import"),
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
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/startliste/pdf/$',
        views.startliste_einzelfahren_pdf, {}, "startliste_einzelfahren_pdf"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/teilnehmer/(?P<startnummer>\d+)/$',
        views.teilnehmer_get, {}, "teilnehmer_get"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/teilnehmer/(?P<startnummer>\d+)/update/$',
        views.teilnehmer_update, {}, "teilnehmer_update"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/teilnehmer/(?P<startnummer>\d+)/delete/$',
        views.teilnehmer_delete_confirm, {}, "teilnehmer_delete_confirm"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/bewertungen/$',
        views.bewertungen, {}, "bewertungen"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/postenblatt/(?P<posten>[-\w]+)/$',
        views.postenblatt, {}, "postenblatt"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/postenblatt/(?P<posten>[-\w]+)/update/$',
        views.postenblatt_update, {}, "postenblatt_update"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/richtzeiten/$',
        views.richtzeiten, {}, "richtzeiten"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/richtzeiten/pdf/$',
        views.richtzeiten_pdf, {}, "richtzeiten_pdf"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/richtzeit/(?P<posten>[-\w]+)/$',
        views.richtzeit, {}, "richtzeit"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/richtzeit/(?P<posten>[-\w]+)/update/$',
        views.richtzeit_update, {}, "richtzeit_update"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/notenliste/$',
        views.notenliste, {}, "notenliste"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/notenliste/pdf/$',
        views.notenliste_pdf, {}, "notenliste_pdf"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/notenliste/pdf/alle-sektionen$',
        views.notenliste_pdf_all, {}, "notenliste_pdf_all"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/notenblaetter/$',
        views.notenblaetter_pdf, {}, "notenblaetter_pdf"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/rangliste/$',
        views.rangliste, {}, "rangliste"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/rangliste/pdf/$',
        views.rangliste_pdf_all, {}, "rangliste_pdf_all"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/rangliste/(?P<kategorie>[-\w]+)/$',
        views.rangliste, {}, "rangliste"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/rangliste/(?P<kategorie>[-\w]+)/pdf/$',
        views.rangliste_pdf, {}, "rangliste_pdf"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/kranzlimiten/$',
        views.kranzlimiten, {}, "kranzlimiten"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/kranzlimiten/update$',
        views.kranzlimiten_update, {}, "kranzlimiten_update"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/notenblatt/$',
        views.notenblatt, {}, "notenblatt"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/notenblatt/(?P<startnummer>\d+)/$',
        views.notenblatt, {}, "notenblatt"),
    (r'^(?P<jahr>\d+)/(?P<wettkampf>[-\w]+)/(?P<disziplin>[-\w]+)/notenblatt/(?P<startnummer>\d+)/pdf/$',
        views.notenblatt_pdf, {}, "notenblatt_pdf"),
)
