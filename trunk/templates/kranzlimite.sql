select kategorie
     , (
        select wert
          from sasse_kranzlimite kl
          join sasse_kategorie k on (kl.kategorie_id = k.id)
         where kl.disziplin_id = %s
           and k.name = kategorie
       ) limite
     , sum(case
            when vorderfahreristds and steuermannistds then 0
            when vorderfahreristds or  steuermannistds then 1
            else 2
           end) wettkaempfer_tot
     , sum(case
            when mitkranz and vorderfahreristds and steuermannistds then 0
            when mitkranz and (vorderfahreristds or steuermannistds) then 1
            when mitkranz and not (vorderfahreristds or steuermannistds) then 2
            else 0
           end) wettkaempfer_mit_kranz
     , count(startnr) schiffe_tot
     , sum(case when mitkranz then 1 else 0 end) schiffe_mit_kranz
  from (
{% include "rangliste.sql" %}
       )
 group by kategorie
