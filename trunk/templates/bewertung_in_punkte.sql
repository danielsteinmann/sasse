-- Alle Zeitbewertungen, konvertiert in Punkte
create view bewertung_in_punkte as
    select b.teilnehmer_id
         , b.posten_id
         , b.bewertungsart_id
         , b.zeit
         , case
             -- Umrechnung von Zeit zu Note
             when ba.einheit = 'ZEIT' then
               round(
                 case
                   when b.zeit > (2 * r.zeit) then 0
                   else 20.00 - (b.zeit / (r.zeit / 10.00))
                 end
               , 2)
             -- Abzüge müssen negativ gemacht werden
             else
               -- TODO: Erst einschalten, wenn Daten migriert
               -- b.note * b.signum
               b.note
           end as note
         , r.zeit as richtzeit
      from sasse_bewertung b
           join sasse_bewertungsart ba on (ba.id = b.bewertungsart_id)
           left outer join sasse_richtzeit r on (r.posten_id = b.posten_id)
