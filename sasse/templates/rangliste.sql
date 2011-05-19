select tn.startnummer as Startnr
     , tn.ausgeschieden as Ausgeschieden
     , tn.disqualifiziert as Disqualifiziert
     , case when not tn.ausgeschieden and not tn.disqualifiziert and (
          select kl.wert
            from sasse_kranzlimite kl
           where 1=1
             and kl.disziplin_id = max(tn.disziplin_id)
             and kl.kategorie_id = max(schiff.kategorie_id)
       ) <= sum(b.note) then 1 else 0 end as MitKranz
     , case when (
          select min(t.startnummer) normale_startnummer
            from sasse_mitglied m
                 join sasse_schiffeinzel schiff on (
                  schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id)
                 join sasse_teilnehmer t on (t.id = schiff.teilnehmer_ptr_id)
           where m.id = max(hinten.id) and t.disziplin_id = max(tn.disziplin_id)
       ) = tn.startnummer then 0 else 1 end as SteuermannIstDS
     , case when (
          select min(t.startnummer) normale_startnummer
            from sasse_mitglied m
                 join sasse_schiffeinzel schiff on (
                  schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id)
                 join sasse_teilnehmer t on (t.id = schiff.teilnehmer_ptr_id)
           where m.id = max(vorne.id) and t.disziplin_id = max(tn.disziplin_id)
       ) = tn.startnummer then 0 else 1 end as VorderfahrerIstDS
     , max(hinten.name) as Steuermann
     , max(hinten.vorname) as SteuermannVorname
     , max(hinten.geburtsdatum) as SteuermannGeburi
     , max(vorne.name) as Vorderfahrer
     , max(vorne.vorname) as VorderfahrerVorname
     , max(vorne.geburtsdatum) as VorderfahrerGeburi
     , max(sektion.name) as Sektion
     , max(kat.name) as Kategorie
     , sum(b.zeit) as Zeit
     , sum(case when tn.ausgeschieden or tn.disqualifiziert then 0 else b.note end) as Punkte
  from sasse_teilnehmer tn
  join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
  join bewertung_calc b on (b.teilnehmer_id = tn.id)
  join sasse_kategorie kat on (kat.id = schiff.kategorie_id)
  join sasse_sektion sektion on (sektion.id = schiff.sektion_id)
  join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
  join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
 where tn.disziplin_id = %s
       {% if kategorie %}and kat.id = %s{% endif %}
 group by tn.startnummer, tn.ausgeschieden, tn.disqualifiziert
 order by Punkte desc, Zeit asc
