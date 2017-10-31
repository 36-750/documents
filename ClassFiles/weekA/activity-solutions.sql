-- Solutions to Activity in Week 9 Tuesday

-- #1
create table rdata (id integer, a text, b text, moment date, x real);

-- #2
select generate_series(1,101) as id;

-- #3
select md5(random()::text);

-- #4
select ('{X,Y,Z}'::text[])[ceil(random()*3)];

-- #5
select date '2017-01-01' + ceil(random()*365)::integer;

-- #6
insert into rdata (select generate_series(1,101) as id,
                          md5(random()::text) as a,
                          ('{X,Y,Z}'::text[])[ceil(random()*3)] as b,
                          date '2017-01-01' + ceil(random()*365)::integer as moment,
                          random()*1000.0 as x);

-- #7
select * from rdata where b = 'Z';

-- #8
select * from rdata where a ~* '[0-9][0-9][a-c]a';

-- #9
select * from rdata where (moment, moment) overlaps (date '2017-11-01', date '2017-11-30');

-- #10
update rdata set b = 'X' where id % 3 = 0 and id % 5 = 0;

-- #11 and #12
delete from foo where k > 2 and k % 2 = 0;
delete from foo where k > 3 and k % 3 = 0;
delete from foo where k > 5 and k % 5 = 0;
delete from foo where k > 7 and k % 7 = 0;
delete from foo where k = 1;
