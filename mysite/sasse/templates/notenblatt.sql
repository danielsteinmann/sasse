select p.name as Posten
     , max(pa.name) as Postenart
     , sum(case when ba.gruppe = 'STIL' and b.note < 0 then abs(b.note) end) as Abzug
     , sum(case when ba.gruppe = 'ZIEL' then b.note end) as Note
     , sum(b.richtzeit) as Richtzeit
     , sum(b.zeit) as Zeit
     , sum(b.note) as Punkte
  from bewertung_calc b
  join sasse_bewertungsart ba on (ba.id = b.bewertungsart_id)
  join sasse_posten p on (p.id = b.posten_id)
  join sasse_postenart pa on (pa.id = p.postenart_id)
  join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = b.teilnehmer_id)
 where p.disziplin_id = %s
{% if teilnehmer %}and b.teilnehmer_id = %s{% endif %}
{% if sektion %}and schiff.sektion_id = %s{% endif %}
 group by b.teilnehmer_id, p.name
 order by min(p.reihenfolge)
