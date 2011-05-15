select kategorie
     , (
        select wert
          from sasse_kranzlimite kl
          join sasse_kategorie k on (kl.kategorie_id = k.id)
         where kl.disziplin_id = %s
           and k.name = r.kategorie
       ) limite
     , sum(case
            when r.vorderfahreristds::bool and r.steuermannistds::bool then 0
            when r.vorderfahreristds::bool or  r.steuermannistds::bool then 1
            else 2
           end) wettkaempfer_tot
     , sum(case
            when r.mitkranz::bool and r.vorderfahreristds::bool and r.steuermannistds::bool then 0
            when r.mitkranz::bool and (r.vorderfahreristds::bool or r.steuermannistds::bool) then 1
            when r.mitkranz::bool and not (r.vorderfahreristds::bool or r.steuermannistds::bool) then 2
            else 0
           end) wettkaempfer_mit_kranz
     , count(r.startnr) schiffe_tot
     , sum(case when r.mitkranz::bool then 1 else 0 end) schiffe_mit_kranz
  from (
{% include "rangliste.sql" %}
       ) as r
 group by r.kategorie
