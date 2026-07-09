-- Alle Zeitbewertungen, konvertiert in Punkte
create view bewertung_calc as
    select t.id as teilnehmer_id
         , p.id as posten_id
         , ba.id as bewertungsart_id
         , b.zeit
         , case
             -- Umrechnung von Zeit zu Note
             when ba.einheit = 'ZEIT' then
               round(
                 case
                   when b.zeit > (3 * r_zeit_auto.zeit) then 0
                   else 15.00 - (b.zeit / (r_zeit_auto.zeit / 5.00))
                 end
               , 1)
             -- Falls keine Noten eingegeben wurden
             when b.note is null then
                ba.defaultwert
             else
                b.note
           -- signum machts moeglich, sum() in einem SQL Select zu verwenden, 
           end * ba.signum as note
         , r_zeit_auto.zeit as richtzeit
      from sasse_teilnehmer t
      join sasse_posten p on (p.disziplin_id = t.disziplin_id)
      join sasse_bewertungsart ba on (ba.postenart_id = p.postenart_id)
      -- Es sollen auch Bewertungen einfliessen, für welche nur
      -- Defaults existieren, respektive kein User Input geschieht
      left outer join sasse_bewertung b on (
          b.teilnehmer_id = t.id
          and b.posten_id = p.id
          and b.bewertungsart_id = ba.id)
      -- left join weil nur Zeitposten eine Richtzeit haben
      left outer join sasse_richtzeit r on (r.posten_id = p.id)
      -- Wenn eine Richtzeit vorhanden ist, dann wird diese verwendet.
      -- Ansonsten die schnellste Zeit des Postens
      , lateral (select case
                   -- Wenn es kein ZEIT Posten ist muss das teure select min nie ausgeführt werden
                   when ba.einheit <> 'ZEIT' or r.zeit > 0 then r.zeit
                   else (select min(zeit) from sasse_bewertung where posten_id = b.posten_id)
                end as zeit) r_zeit_auto
