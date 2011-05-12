drop table bewertung;
create table bewertung (
   teilnehmer_id number
 , posten_id number
 , punkt number
 , zeit decimal
);

drop table richtzeit;
create table richtzeit (
   posten_id number
 , zeit decimal
);

insert into bewertung values (1, 1, 10.0, 0);
insert into bewertung values (1, 1, 9.5, 0);
insert into bewertung values (1, 2, 0, 123.35);
insert into bewertung values (1, 3, 0, 44.10);
insert into bewertung values (2, 1, 10.0, 0);
insert into bewertung values (2, 1, 10.0, 0);
insert into bewertung values (2, 2, 0, 118.35);
insert into bewertung values (2, 3, 0, 40.00);
insert into bewertung values (3, 1, 5.0, 0);
insert into bewertung values (3, 1, 5.0, 0);
insert into bewertung values (3, 2, 0, 130.12);
insert into bewertung values (3, 3, 0, 80.95);

insert into richtzeit values (2, 120.0);
insert into richtzeit values (3, 40.0);

-- Bewertungen, wobei die Zeit in Punkte umgewandelt wurde
drop view bewertung_z2p;
create view bewertung_z2p as
    select b.teilnehmer_id
         , b.posten_id
         , b.zeit
         , r.zeit richtzeit
         , case
             when b.posten_id in (2, 3) then -- Es ist eine Zeitnote
               round(
                 case
                   when b.zeit > (2 * r.zeit) then 0
                   else 20.00 - (b.zeit / (r.zeit / 10.00))
                 end
               , 2)
             else
               b.punkt
           end as punkt
      from bewertung b
           left outer join richtzeit r on (r.posten_id = b.posten_id)
/

select * from bewertung;
select * from bewertung_z2p;

-- Rangliste
select teilnehmer_id as Teilnehmer
     , sum(zeit) as Gesamtzeit
     , sum(punkt) as Punkte
  from bewertung_z2p
 group by teilnehmer_id
 order by punkte desc, gesamtzeit desc
/

-- Notenliste
select teilnehmer_id as Teilnehmer
     , sum(case when posten_id = 1 then punkt end) as "B"
     , sum(case when posten_id = 2 then zeit end) as "C-F[s]"
     , sum(case when posten_id = 2 then punkt end) as "C-F"
     , sum(case when posten_id = 3 then zeit end) as "D-G[s]"
     , sum(case when posten_id = 3 then punkt end) as "D-G"
     , sum(zeit) as Gesamtzeit
     , sum(punkt) as Punkte
  from bewertung_z2p
 group by teilnehmer_id
 order by punkte desc, gesamtzeit desc
/
