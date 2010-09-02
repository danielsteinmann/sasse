drop table posten;
create table posten (
   id number
 , name varchar
 , offset number
 , reihenfolge number
);

drop table bewertung;
create table bewertung (
   teilnehmer_id number
 , posten_id number
 , signum number
 , note number
 , zeit decimal
);

drop table richtzeit;
create table richtzeit (
   posten_id number
 , zeit decimal
);

insert into posten values(1, 'Anmeldung A', 0, 1);
insert into posten values(2, 'Zeit B-C', 0, 2);
insert into posten values(3, 'Zeit E-F', 0, 3);
insert into posten values(4, 'Abfahrt E', 10, 4);

insert into bewertung values (10, 1, -1, 0.5, null);
insert into bewertung values (10, 2, +1, null, 123.35);
insert into bewertung values (10, 3, +1, null, 44.10);
insert into bewertung values (10, 4, -1, 3.0, null);
insert into bewertung values (10, 4, +1, 8.5, null);
insert into bewertung values (20, 1, -1, 1.0, null);
insert into bewertung values (20, 2, +1, null, 118.35);
insert into bewertung values (20, 3, +1, null, 40.00);
insert into bewertung values (20, 4, -1, 0.5, null);
insert into bewertung values (20, 4, +1, 9.5, null);
insert into bewertung values (30, 1, -1, 5.0, null);
insert into bewertung values (30, 2, +1, null, 130.12);
insert into bewertung values (30, 3, +1, null, 80.95);
insert into bewertung values (30, 4, -1, 1.0, null);
insert into bewertung values (30, 4, +1, 7.5, null);

insert into richtzeit values (2, 120.0);
insert into richtzeit values (3, 40.0);

-- Bewertungen, wobei die Zeit in eine Note umgewandelt wurde
drop view bewertung_calc;
create view bewertung_calc as
    select b.teilnehmer_id
         , b.posten_id
         , b.zeit
         , r.zeit richtzeit
         , case
             -- Umrechnung von Zeit zu Note
             when b.posten_id in (2, 3) then
               round(
                 case
                   when b.zeit > (2 * r.zeit) then 0
                   else 20.00 - (b.zeit / (r.zeit / 10.00))
                 end
               , 2)
             -- Abzüge müssen negativ gemacht werden
             else
               b.note * b.signum
           end as note
         , case
             when b.posten_id in (2, 3) then 'zeit'
             when b.signum = -1 then 'abzug'
             else 'normal'
           end as 'typ'
      from bewertung b
           left outer join richtzeit r on (r.posten_id = b.posten_id)
     union
    -- Der Typ wird für das Notenblatt gebraucht. Im Notenblatt muss der Offset
    -- (typischerweise Stil-Maximum) des Posten gefiltert werden können
    select b.teilnehmer_id
         , b.posten_id
         , null
         , null
         , p.offset
         , 'offset'
      from bewertung b
           join posten p on (p.id = b.posten_id)
     where p.offset > 0
/

select * from bewertung;
select * from bewertung_calc;

-- Rangliste
select teilnehmer_id as Teilnehmer
     , sum(zeit) as Gesamtzeit
     , sum(note) as Gesamtnote
  from bewertung_calc
 group by Teilnehmer
 order by Gesamtnote desc, Gesamtzeit desc
/

-- Notenliste
select teilnehmer_id as Teilnehmer
     , sum(case when p.name = "Anmeldung A" then note end) as "A"
     , sum(case when p.name = "Zeit B-C" then zeit end) as "B-C[s]"
     , sum(case when p.name = "Zeit B-C" then note end) as "B-C"
     , sum(case when p.name = "Zeit E-F" then zeit end) as "E-F[s]"
     , sum(case when p.name = "Zeit E-F" then note end) as "E-F"
     , sum(case when p.name = "Abfahrt E" then note end) as "E"
     , sum(zeit) as Gesamtzeit
     , sum(note) as Gesamtnote
  from bewertung_calc b
  join posten p on (p.id = b.posten_id)
 group by Teilnehmer
 order by Gesamtnote desc, Gesamtzeit desc
/

-- Notenblatt
select b.teilnehmer_id as Teilnehmer
     , p.name as Posten
     , sum(case when b.typ = 'abzug' then abs(note) end) as "Abzug"
     , sum(case when b.typ = "normal" then note end) as "Note"
     , sum(zeit) as "Zeit"
     , sum(note) as "Total"
  from bewertung_calc b
  join posten p on (p.id = b.posten_id)
 group by Teilnehmer, Posten
 order by Teilnehmer, p.reihenfolge
/

