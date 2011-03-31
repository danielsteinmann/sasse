select tn.startnummer as Startnr
     , case when (
          select kl.wert
            from sasse_kranzlimite kl
           where 1=1
             and kl.disziplin_id = tn.disziplin_id
             and kl.kategorie_id = schiff.kategorie_id
       ) < (sum(b.note) + 0.01) then 1 else 0 end as MitKranz
       /* 0.01 umgeht Rundungsprobleme in sqlite, wo es nur floats gibt */
     , case when (
          select min(t.startnummer) normale_startnummer
            from sasse_mitglied m
                 join sasse_schiffeinzel schiff on (
                  schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id)
                 join sasse_teilnehmer t on (t.id = schiff.teilnehmer_ptr_id)
           where m.id = hinten.id and t.disziplin_id = p.disziplin_id
       ) = tn.startnummer then 0 else 1 end as SteuermannIstDS
     , case when (
          select min(t.startnummer) normale_startnummer
            from sasse_mitglied m
                 join sasse_schiffeinzel schiff on (
                  schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id)
                 join sasse_teilnehmer t on (t.id = schiff.teilnehmer_ptr_id)
           where m.id = vorne.id and t.disziplin_id = p.disziplin_id
       ) = tn.startnummer then 0 else 1 end as VorderfahrerIstDS
     , max(hinten.name) as Steuermann
     , max(hinten.vorname) as SteuermannVorname
     , hinten.geburtsdatum as SteuermannGeburi
     , max(vorne.name) as Vorderfahrer
     , max(vorne.vorname) as VorderfahrerVorname
     , vorne.geburtsdatum as VorderfahrerGeburi
     , max(sektion.name) as Sektion
     , max(kat.name) as Kategorie
     , sum(b.zeit) as Zeit
     , sum(b.note) as Total
  from bewertung_calc b
  join sasse_teilnehmer tn on (tn.id = b.teilnehmer_id)
  join sasse_posten p on (p.id = b.posten_id)
  join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
  join sasse_kategorie kat on (kat.id = schiff.kategorie_id)
  join sasse_sektion sektion on (sektion.id = schiff.sektion_id)
  join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
  join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
 where p.disziplin_id = %s and kat.id = %s
 group by tn.startnummer
 order by Total desc, Zeit asc
