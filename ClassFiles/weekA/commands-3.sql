-- Created automatically in org buffer with
--    (mapconcat #'identity
--               (org-element-map (org-element-parse-buffer) 'src-block
--                 (lambda (block)
--                   (org-element-property :value block)))
--               "\n")
-- Each group of commands is annotated with its section in the notes.


-- For Reference: PostgreSQL Primer and Command Summary

create table products (
       product_id SERIAL PRIMARY KEY,
       name text,
       price numeric CHECK (price > 0),
       sale_price numeric CHECK (sale_price > 0),
       CHECK (price > sale_price)
);

insert into products (name, price, sale_price) values ('furby', 100, 95);
insert into products (name, price, sale_price)
       values ('frozen lunchbox', 10, 8),
              ('uss enterprise', 12, 11),
              ('spock action figure', 8, 7),
              ('slime', 1, 0.50);

select * from products;
select name, price from products;
select name as product, price as howmuch from products;


-- Activity Debrief

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
select * from rdata where a ILIKE '%abc%';

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


-- Joins and Foreign Keys

create table countries (
       country_code char(2) PRIMARY KEY,
       country_name text UNIQUE
);
insert into countries
  values ('us', 'United States'), ('mx', 'Mexico'), ('au', 'Australia'),
         ('gb', 'Great Britain'), ('de', 'Germany'), ('ol', 'OompaLoompaland');
select * from countries;
delete from countries where country_code = 'ol';

create table cities (
       name text NOT NULL,
       postal_code varchar(9) CHECK (postal_code <> ''),
       country_code char(2) REFERENCES countries,
       PRIMARY KEY (country_code, postal_code)
);

insert into cities values ('Toronto', 'M4C185', 'ca'), ('Portland', '87200', 'us');

insert into countries values ('ca', 'Canada');
insert into cities values ('Toronto', 'M4C185', 'ca'), ('Portland', '87200', 'us');
update cities set postal_code = '97205' where name = 'Portland';

select personae.lastname, personae.firstname, score, moment
       from events
       join personae on persona = personae.id
       where moment > timestamp '2015-03-26 08:00:00'
       order by moment;

create table A (id SERIAL PRIMARY KEY, name text);
insert into A (name)
       values ('Pirate'),
              ('Monkey'),
              ('Ninja'),
              ('Flying Spaghetti Monster');

create table B (id SERIAL PRIMARY KEY, name text);
insert into B (name)
       values ('Rutabaga'),
              ('Pirate'),
              ('Darth Vader'),
              ('Ninja');
select * from A;
select * from B;

select * from A INNER JOIN B on A.name = B.name;

select * from A FULL OUTER JOIN B on A.name = B.name;

select * from A LEFT OUTER JOIN B on A.name = B.name;

select * from A LEFT OUTER JOIN B on A.name = B.name where B.id IS null;

select * from A FULL OUTER JOIN B on A.name = B.name
    where B.id IS null OR A.id IS null;

select name, postal_code, country_name
    from cities inner join countries
    on cities.country_code = countries.country_code;

select cities.name as city, country_name as country,
       concat(name, ', ', country_name, ' ', postal_code) as address
    from cities inner join countries
    on cities.country_code = countries.country_code;

create table venues (
       id SERIAL PRIMARY KEY,
       name varchar(255),
       street_address text,
       type char(7) CHECK (type in ('public', 'private')) DEFAULT 'public',
       postal_code varchar(9),
       country_code char(2),
       FOREIGN KEY (country_code, postal_code)
         REFERENCES cities (country_code, postal_code) MATCH FULL
);
insert into venues (name, postal_code, country_code)
  values ('Crystal Ballroom', '97205', 'us'),
         ('Voodoo Donuts', '97205', 'us'),
         ('CN Tower', 'M4C185', 'ca');
update venues set type = 'private' where name = 'CN Tower';
select * from venues;       

create table social_events (
       id SERIAL PRIMARY KEY,
       title text,
       starts timestamp DEFAULT timestamp 'now' + interval '1 month',
       ends timestamp DEFAULT timestamp 'now' + interval '1 month' + interval '3 hours',
       venue_id integer REFERENCES venues (id)
);
insert into social_events (title, venue_id) values ('LARP Club', 3);
insert into social_events (title, starts, ends) 
  values ('Fight Club', timestamp 'now' + interval '12 hours', timestamp 'now' + interval '16 hours');
insert into social_events (title, venue_id) 
  values ('Arbor Day Party', 1), ('Doughnut Dash', 2);
select * from social_events;

select e.title as event, v.name as venue FROM social_events e JOIN venues v
  on e.venue_id = v.id;
select e.title as event, v.name as venue FROM social_events e LEFT JOIN venues v
  on e.venue_id = v.id;

create index social_events_title  on social_events using hash(title);
create index social_events_starts on social_events using btree(starts);

select * from social_events where title = 'Fight Club';
select * from social_events where starts >= '2015-11-28';

alter table events ADD FOREIGN KEY (persona) REFERENCES personae;
alter table events ADD FOREIGN KEY (element) REFERENCES elements;

select p.lastname, p.firstname, 
         c.department || '-' || c.catalog_number as course,
         score,
         hints,
         to_char(moment, 'Dy DD Mon YYYY')
       from events
       join personae as p on persona = p.id
       join courses as c on p.course = c.id
       where moment > timestamp '2015-03-26 08:00:00';


-- Advanced Example: Text Processing 

create extension fuzzystrmatch;
create extension cube;
create extension pg_trgm;

select title from movies where title ilike 'stardust%';

select title from movies where title ilike 'stardust_%';

select count(*) from movies
       where title !~* '^the.*';

select count(*) from movies
       where title ~* 'the';

select count(*) from movies
       where title ~ 'the';

create index movie_title_pattern on movies (lower(title) text_pattern_ops);

select levenshtein('guava', 'guano');
select levenshtein('bat','fads') as fads,
       levenshtein('bat','fad')  as fad,
       levenshtein('bat','fat')  as fat,
       levenshtein('bat','bad')  as bad;

select movie_id, title from movies
  where levenshtein(lower(title), lower('a hard day nght')) <= 3;
select movie_id, title from movies
  where levenshtein(lower(title), lower('a hard day nght')) <= 8;

select show_trgm('Avatar');

create index movies_title_trigram on movies
  using gist(title gist_trgm_ops);
select title from movies where title % 'Avatre';

select title from movies where title @@ 'night & day';

select to_tsvector('A Hard Day''s Night'), to_tsquery('english', 'night & day');

explain select * from movies where title @@ 'night & day';
create index movies_title_searchable on movies
       using gin(to_tsvector('english', title));
explain select * from movies where title @@ 'night & day';
explain select * from movies
        where to_tsvector('english', title) @@ 'night & day';

select * from genres;
select * from movies where title @@ 'star & wars';
select name, cube_ur_coord('(0, 7, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 10, 0, 0, 0)', position) as score
  from genres g
  where cube_ur_coord('(0, 7, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 10, 0, 0, 0)', position) > 0;

select title, 
       cube_distance(genre, '(0, 7, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 10, 0, 0, 0)') as dist
       from movies
       ORDER BY dist
       LIMIT 16;

select m.movie_id, m.title
       from movies as m,
            (select genre, title from movies
                    where title = 'Mad Max') as s
       where cube_enlarge(s.genre, 5, 18) @> m.genre AND
             s.title != m.title
       order by cube_distance(m.genre, s.genre)
       limit 10;


-- Appendix: A Few Advanced Maneuvers, Part I

select title, starts from social_events where 
     venue_id in (select id from venues where name ~ 'room');

select title, starts from social_events where 
     exists (select 1 from venues where id = social_events.venue_id);

select count(*) from social_events where venue_id = 4;

select count(*) from events where venue_id = 1;
select count(*) from events where venue_id = 2;
select count(*) from events where venue_id = 3;
select count(*) from events where venue_id = 4;

select venue_id, count(*) from events group by venue_id;

select venue_id, count(*) from events group by venue_id
    having venue_id is not NULL;
select venue_id, count(*) from events group by venue_id
    having count(*) > 1 AND venue_id is not NULL;

insert into social_events (title, venue_id)
  values ('Valentine''s Day Party', 1), ('April Fool''s Day Party', 1);

select venue_id, count(*) from social_events group by venue_id
    order by venue_id;
select venue_id, count(*) OVER (PARTITION BY venue_id)
    from social_events order by venue_id;
