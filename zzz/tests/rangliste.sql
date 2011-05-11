drop table bewertung;
create table bewertung (
   posten_id number
 , teilnehmer_id number
 , wert number
 , wertart varchar2(10)
);

drop table richtzeit;
create table richtzeit (
   posten_id number
 , zeit number
);

insert into bewertung values (1, 1, 10.0, 'PUNKTE');
insert into bewertung values (1, 1, 9.5, 'PUNKTE');
insert into bewertung values (1, 2, 10.0, 'PUNKTE');
insert into bewertung values (1, 2, 10.0, 'PUNKTE');
insert into bewertung values (1, 3, 5.0, 'PUNKTE');
insert into bewertung values (1, 3, 5.0, 'PUNKTE');
insert into bewertung values (2, 1, 123.35, 'ZEIT');
insert into bewertung values (2, 2, 118.35, 'ZEIT');
insert into bewertung values (2, 3, 130.12, 'ZEIT');
insert into bewertung values (3, 1, 44.10, 'ZEIT');
insert into bewertung values (3, 2, 40.00, 'ZEIT');
insert into bewertung values (3, 3, 80.95, 'ZEIT');

insert into richtzeit values (2, 120.0);
insert into richtzeit values (3, 40.0);

-- Alle Zeitbewertungen, konvertiert in Punkte
drop view bewertung_in_punkte;
create view bewertung_in_punkte as
    select b.posten_id
         , b.teilnehmer_id
         , b.wert zeitwert
         , round(
              case
                when b.wert > (2 * r.zeit) then 0
                else 20 - (b.wert / (r.zeit / 10))
              end
            , 2) punktwert
         , r.zeit richtzeit
      from bewertung b
           join richtzeit r on (r.posten_id = b.posten_id)
     where b.wertart = 'ZEIT'
/

select * from bewertung;
select * from bewertung_in_punkte;

select teilnehmer_id
     , wertart
     , sum(wert)
  from bewertung
 group by teilnehmer_id, wertart
 order by 1, 2, 3
/

-- Rangliste
select teilnehmer_id as Teilnehmer
     , sum(case when wertart = 'PUNKTE' then wert end) as Punkte
     , sum(case when wertart = 'ZEIT' then wert end) as Gesamtzeit
  from (
         select teilnehmer_id
              , wert
              , wertart
           from bewertung
         -- 'all' ist nötig, damit nicht ein distinct passiert, bsp:
         -- 
         --   TEILNEHMER  WERTART  WERT
         --            1   PUNKTE    10  (Posten B)
         --            1   PUNKTE    10  (Posten C)
         --
         union all
         select teilnehmer_id
              , punktwert
              , 'PUNKTE'
           from bewertung_in_punkte
       )
 group by teilnehmer_id
 order by punkte desc, gesamtzeit desc
/

-- Notenliste
select teilnehmer_id as Teilnehmer
     , sum(case when posten_id = 1 and wertart = 'PUNKTE' then wert end) as "B"
     , sum(case when posten_id = 2 and wertart = 'PUNKTE' then wert end) as "C-F"
     , sum(case when posten_id = 3 and wertart = 'PUNKTE' then wert end) as "D-G"
     , sum(case when posten_id = 3 and wertart = 'ZEIT' then wert end) as "D-G (Zeit)"
     , sum(case when wertart = 'PUNKTE' then wert end) as Punkte
     , sum(case when wertart = 'ZEIT' then wert end) as Gesamtzeit
  from (
         select posten_id
              , teilnehmer_id
              , wert
              , wertart
           from bewertung
         union all
         select posten_id
              , teilnehmer_id
              , punktwert
              , 'PUNKTE'
           from bewertung_in_punkte
       )
 group by teilnehmer_id
 order by punkte desc, gesamtzeit desc
/
