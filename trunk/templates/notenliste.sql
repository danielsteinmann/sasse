select tn.startnummer as Startnr
     , max(hinten.name) as Steuermann
     , max(vorne.name) as Vorderfahrer
     , max(sektion.name) as Sektion
     , max(kat.name) as Kategorie
     , sum(b.zeit) as Zeit
     , sum(b.note) as Punkte
{% for p in posten %}
     , sum(case when b.posten_id = {{ p.id }} then b.note end) as '{{ p.name }}'
{% ifequal p.postenart.name "Zeitnote" %}
     , sum(case when b.posten_id = {{ p.id }} then b.zeit end) as '{{ p.name }} [s]'
{% endifequal %}
{% endfor %}
  from bewertung_calc b
       join sasse_teilnehmer tn on (tn.id = b.teilnehmer_id)
       join sasse_posten p on (p.id = b.posten_id)
       join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
       join sasse_kategorie kat on (kat.id = schiff.kategorie_id)
       join sasse_sektion sektion on (sektion.id = schiff.sektion_id)
       join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
       join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
 where p.disziplin_id = %s
       {% if sektion %}and schiff.sektion_id = %s{% endif %}
       {% if startnummern %}and tn.startnummer in ({startnummern}){% endif %}
 group by tn.startnummer
 order by Punkte desc, Zeit asc
