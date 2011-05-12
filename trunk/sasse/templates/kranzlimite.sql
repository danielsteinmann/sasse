select kategorie
     , (
        select wert
          from sasse_kranzlimite kl
          join sasse_kategorie k on (kl.kategorie_id = k.id)
         where kl.disziplin_id = %s
           and k.name = r.kategorie
       ) limite
     , sum(case
            when r.vorderfahreristds and r.steuermannistds then 0
            when r.vorderfahreristds or  r.steuermannistds then 1
            else 2
           end) wettkaempfer_tot
     , sum(case
            when r.mitkranz and r.vorderfahreristds and r.steuermannistds then 0
            when r.mitkranz and (r.vorderfahreristds or r.steuermannistds) then 1
            when r.mitkranz and not (r.vorderfahreristds or r.steuermannistds) then 2
            else 0
           end) wettkaempfer_mit_kranz
     , count(r.startnr) schiffe_tot
     , sum(case when r.mitkranz then 1 else 0 end) schiffe_mit_kranz
  from (
{% include "rangliste.sql" %}
       ) as r
 group by r.kategorie
