select tn.startnummer as Startnr
     , max(hinten.name) as Steuermann
     , max(vorne.name) as Vorderfahrer
     , max(sektion.name) as Sektion
     , max(kat.name) as Kategorie
     , sum(case when b.einheit = 'ZEIT' then b.wert end) as Zeit
     , sum(case when b.einheit = 'PUNKT' then b.wert end) as Total
{% for p in posten %}
{% ifequal p.postenart.name "Zeitnote" %}
     , sum(case when b.posten_id = {{ p.id }} and b.einheit = 'ZEIT' then b.wert end) as '{{ p.name }}'
     , sum(case when b.posten_id = {{ p.id }} and b.einheit = 'PUNKT' then b.wert end) as 'p'
{% else %}
     , sum(case when b.posten_id = {{ p.id }} and b.einheit = ba.einheit then b.wert end) as '{{ p.name }}'
{% endifequal %}
{% endfor %}
  from (
          select posten_id
               , teilnehmer_id
               , wert
               , ba.einheit
               , b.bewertungsart_id
            from sasse_bewertung b
            join sasse_bewertungsart ba on (ba.id = b.bewertungsart_id)
         union all
          select posten_id
               , teilnehmer_id
               , punktwert
               , 'PUNKT'
               , bewertungsart_id
            from bewertung_in_punkte
       ) as b
       join sasse_teilnehmer tn on (tn.id = b.teilnehmer_id)
       join sasse_bewertungsart ba on (ba.id = b.bewertungsart_id)
       join sasse_posten p on (p.id = b.posten_id)
       join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
       join sasse_kategorie kat on (kat.id = schiff.kategorie_id)
       join sasse_sektion sektion on (sektion.id = schiff.sektion_id)
       join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
       join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
 where p.disziplin_id = %s
       {% if sektion %}and schiff.sektion_id = %s{% endif %}
 group by tn.startnummer
 order by Total desc, Zeit asc
