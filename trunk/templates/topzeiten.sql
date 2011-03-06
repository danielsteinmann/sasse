select tn.startnummer as Startnr
     , hinten.name as Steuermann
     , vorne.name as Vorderfahrer
     , sektion.name as Sektion
     , kat.name as Kategorie
     , b.zeit as Zeit
     , b.note as Punkte
     , b.richtzeit as Richtzeit
  from bewertung_calc b
       join sasse_teilnehmer tn on (tn.id = b.teilnehmer_id)
       join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
       join sasse_kategorie kat on (kat.id = schiff.kategorie_id)
       join sasse_sektion sektion on (sektion.id = schiff.sektion_id)
       join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
       join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
 where b.posten_id = %s
   and b.zeit > 0
 order by Zeit asc
