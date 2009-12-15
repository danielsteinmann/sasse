-- Alle Zeitbewertungen, konvertiert in Punkte
create view bewertung_in_punkte as
    select b.posten_id
         , b.teilnehmer_id
         , b.bewertungsart_id
         , b.wert zeitwert
         , r.zeit richtzeit
         , round(
              case
                when b.wert > (2 * r.zeit) then 0
                else 20.0 - (b.wert / (r.zeit / 10.0))
              end
            , 2) punktwert
      from sasse_bewertung b
           join sasse_richtzeit r on (r.posten_id = b.posten_id)
           join sasse_bewertungsart ba on (ba.id = b.bewertungsart_id)
     where ba.einheit = 'ZEIT'
