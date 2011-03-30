select kat.name as Kategorie
     , limite as LimiteInPunkte
     , count(startnr) as Raenge
     , sum(kranzrang) as RaengeUeberLimit
     , sum(doppelstarter) as Doppelstarter
     , sum(case when doppelstarter and kranzrang then 1 else 0 end) as DoppelstarterUeberLimit
from (
      select tn.startnummer as Startnr
           , schiff.kategorie_id
           , kl.wert as Limite
           , case when (
                select min(t.startnummer) normale_startnummer
                  from sasse_mitglied m
                       join sasse_schiffeinzel schiff on (
                          schiff.vorderfahrer_id = m.id
                          or schiff.steuermann_id = m.id)
                       join sasse_teilnehmer t on (
                          t.id = schiff.teilnehmer_ptr_id)
                 where t.disziplin_id = tn.disziplin_id
                   and m.id in (vorne.id, hinten.id)
             ) = tn.startnummer then 0 else 1 end as doppelstarter
           , case when (sum(b.note) + 0.01) >= kl.wert then 1 else 0 end kranzrang
           , sum(b.note) as Total
        from bewertung_calc b
        join sasse_teilnehmer tn on (tn.id = b.teilnehmer_id)
        join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
        join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
        join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
        left join sasse_kranzlimite kl on (
               kl.disziplin_id = tn.disziplin_id
               and kl.kategorie_id = schiff.kategorie_id
             )
       where 1=1
         and tn.disziplin_id = %s
       group by tn.startnummer
     ) rangliste
  join sasse_kategorie kat on (kat.id = rangliste.kategorie_id)
 group by Kategorie
 order by Kategorie
