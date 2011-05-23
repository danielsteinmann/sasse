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
     , schiff.steuermann_ist_ds as SteuermannIstDS
     , schiff.vorderfahrer_ist_ds as VorderfahrerIstDS
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
        , schiff.steuermann_ist_ds, schiff.vorderfahrer_ist_ds
 order by Punkte desc, Zeit asc
