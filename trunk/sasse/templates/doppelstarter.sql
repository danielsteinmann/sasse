-- Doppelstarter ist derjeninge mit der groesseren Startnummer
create view doppelstarter as
    select tn.disziplin_id
         , m.id mitglied_id
         , min(tn.startnummer) normale_startnummer
         , count(tn.id) anzahl_starts
      from sasse_mitglied m
           join sasse_schiffeinzel schiff on (
               schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id)
           join sasse_teilnehmer tn on (tn.id = schiff.teilnehmer_ptr_id)
     group by tn.disziplin_id, m.id
    having count(tn.id) > 1
