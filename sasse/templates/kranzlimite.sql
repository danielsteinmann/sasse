select kat.name
     , (
        select wert
          from sasse_kranzlimite kl
          join sasse_kategorie k on (kl.kategorie_id = k.id)
         where kl.disziplin_id = %s
           and k.name = kat.name
       ) limite
     , sum(case
            when r.vorderfahreristds and r.steuermannistds then 0
            when r.vorderfahreristds or  r.steuermannistds then 1
            else 2
           end) wettkaempfer_tot
     , sum(case
            when r.mitkranz::bool and r.vorderfahreristds and r.steuermannistds then 0
            when r.mitkranz::bool and (r.vorderfahreristds or r.steuermannistds) then 1
            when r.mitkranz::bool and not (r.vorderfahreristds or r.steuermannistds) then 2
            else 0
           end) wettkaempfer_mit_kranz
     , count(r.startnr) schiffe_tot
     , sum(case when r.mitkranz::bool then 1 else 0 end) schiffe_mit_kranz
  from sasse_kategorie kat
  join (
{% include "rangliste.sql" %}
       ) as r on (r.kategorie = kat.name)
 where kat.disziplinart_id = %s
 group by kat.name, kat.reihenfolge
 order by kat.reihenfolge
