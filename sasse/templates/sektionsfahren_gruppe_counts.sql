select grp.name
     , count(schiff.teilnehmer_ptr_id) as anz_schiffe
     , sum(
            case when s1.geschlecht = 'm' and w.year - s1.year <= 20 then 1 else 0 end
         +  case when s2.geschlecht = 'm' and w.year - s2.year <= 20 then 1 else 0 end
         +  case when v1.geschlecht = 'm' and w.year - v1.year <= 20 then 1 else 0 end
         +  case when v2.geschlecht = 'm' and w.year - v2.year <= 20 then 1 else 0 end
       ) as anz_jps
     , sum(
            case when w.year - s1.year <= 20 then 1 else 0 end
         +  case when w.year - s2.year <= 20 then 1 else 0 end
         +  case when w.year - v1.year <= 20 then 1 else 0 end
         +  case when w.year - v2.year <= 20 then 1 else 0 end
       ) as anz_u21
     , sum(
            case when w.year - s1.year >= 18 and w.year - s1.year <= 42 then 1 else 0 end
         +  case when w.year - s2.year >= 18 and w.year - s2.year <= 42 then 1 else 0 end
         +  case when w.year - v1.year >= 18 and w.year - v1.year <= 42 then 1 else 0 end
         +  case when w.year - v2.year >= 18 and w.year - v2.year <= 42 then 1 else 0 end
       ) as anz_18_42
     , sum(
            case when s1.geschlecht = 'f' then 1 else 0 end
         +  case when s2.geschlecht = 'f' then 1 else 0 end
         +  case when v1.geschlecht = 'f' then 1 else 0 end
         +  case when v2.geschlecht = 'f' then 1 else 0 end
       ) as anz_frauen
     , sum(
            case when s1.geschlecht = 'm' and w.year - s1.year >= 60 then 1 else 0 end
         +  case when s2.geschlecht = 'm' and w.year - s2.year >= 60 then 1 else 0 end
         +  case when v1.geschlecht = 'm' and w.year - v1.year >= 60 then 1 else 0 end
         +  case when v2.geschlecht = 'm' and w.year - v2.year >= 60 then 1 else 0 end
       ) as anz_senioren
  from sasse_sektionsfahrengruppe grp
       join sasse_teilnehmer grp_tn on (grp_tn.id = grp.teilnehmer_ptr_id)
       join sasse_disziplin d on (d.id = grp_tn.disziplin_id)
       join (select id, extract(year from von) as year from sasse_wettkampf) w on (w.id = d.wettkampf_id)
       left outer join sasse_schiffsektion schiff on (schiff.gruppe_id = grp.teilnehmer_ptr_id)
       left outer join (select id, extract(year from geburtsdatum) as year, geschlecht from sasse_mitglied) s1 on (s1.id = schiff.ft1_steuermann_id)
       left outer join (select id, extract(year from geburtsdatum) as year, geschlecht from sasse_mitglied) s2 on (s2.id = schiff.ft2_steuermann_id)
       left outer join (select id, extract(year from geburtsdatum) as year, geschlecht from sasse_mitglied) v1 on (v1.id = schiff.ft1_vorderfahrer_id)
       left outer join (select id, extract(year from geburtsdatum) as year, geschlecht from sasse_mitglied) v2 on (v2.id = schiff.ft2_vorderfahrer_id)
 where 1=1
   and grp_tn.disziplin_id = %s
   {% if gruppe %}and grp.teilnehmer_ptr_id = %s{% endif %}
 group by grp.name
 order by grp.name
