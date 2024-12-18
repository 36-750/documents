-- Created automatically in org buffer with
--    (mapconcat #'identity
--               (org-element-map (org-element-parse-buffer) 'src-block
--                 (lambda (block)
--                   (org-element-property :value block)))
--               "\n")

-- To populate the events table (after creating it), do the following
--
--    \COPY events FROM '<path>/events.csv' WITH DELIMITER ',';
--    SELECT setval('events_id_seq', 1001, false);
--
-- with '<path>/events.csv' containing the (relative) path location
-- of the events.csv file you pulled from the github repository.


-- A Simple Example

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


-- Making Tables

create table products (
       product_id integer,
       name text,
       price real,
       sale_price real
);

create table products (
       product_id SERIAL PRIMARY KEY,
       name text,
       price numeric CHECK (price > 0),
       sale_price numeric CHECK (sale_price > 0),
       CHECK (price > sale_price)
);

insert into products (name, price, sale_price)
       values ('kirk action figure', 50, 52);

create table products (
       product_id SERIAL PRIMARY KEY,
       label text UNIQUE NOT NULL CHECK (char_length(label) > 0),
       price numeric CHECK (price >= 0),
       discount numeric DEFAULT 0.0 CHECK (discount >= 0),
       CHECK (price > discount)
);

insert into products (label, price)
       values ('kirk action figure', 50);
insert into products (price, discount)
       values (50, 42);
insert into products (label, price, discount)
       values ('', 50, 42);

alter table products
      rename product_id to id;

alter table products add brand_name text NOT NULL;

alter table products drop discount;

alter table products
      alter brand_name SET DEFAULT 'generic';

drop table products;
drop table products cascade;


-- Working with CRUD

create table events (
       id SERIAL PRIMARY KEY,
       moment timestamp DEFAULT 'now',
       persona integer NOT NULL,
       element integer NOT NULL,
       score integer NOT NULL DEFAULT 0 CHECK (score >= 0 and score <= 1000),
       hints integer NOT NULL DEFAULT 0 CHECK (hints >= 0),
       latency real,
       answer text,
       feedback text
);

-- modify the path 'events.csv' to be correct for your computer (relative to postgres repl)
\COPY events FROM 'events.csv' WITH DELIMITER ',';
SELECT setval('events_id_seq', 1001, false);

insert into events (persona, element, score, answer, feedback)
       values (1211, 29353, 824, 'C', 'How do the mean and median differ?');
insert into events (persona, element, score, answer, feedback)
       values (1207, 29426, 1000, 'A', 'You got it!')
       RETURNING id;
insert into events (persona, element, score, answer, feedback)
       values (1117, 29433,  842, 'C', 'Try simplifying earlier.'),
              (1199, 29435,    0, 'B', 'Your answer was blank'),
              (1207, 29413, 1000, 'C', 'You got it!'),
              (1207, 29359,  200, 'A', 'A square cannot be negative')
       RETURNING *;

select * from events;

select 1 as one;
select ceiling(10*random()) as r;
select 1 from generate_series(1,10) as ones;
select min(r), avg(r) as mean, max(r) from
       (select random() as r from generate_series(1,10000)) as _;
select timestamp '2015-01-22 08:00:00' + random() * interval '64 days'
       as w from generate_series(1,10);

select * from events where id > 20 and id < 40;

select score, element from events
    where persona = 1202 order by element, score;
select count(answer) from events where answer = 'A';
select element, count(answer) as numAs
       from events where answer = 'A'
       group by element
       order by numAs;
select persona, avg(score) as mean_score
       from events 
       group by persona
       order by mean_score;

select id from events where moment > timestamp '2015-03-20 08:00:00';
select id, persona, score from events where score > 900;
select distinct persona from events where score > 900 order by persona;
select persona from events group by persona having avg(score) > 600;
select element, count(element) from events group by element order by element;


create table gems (label text DEFAULT '',
                   facets integer DEFAULT 0,
                   price money);

insert into gems (select '', ceiling(20*random()+1), money '1.00' from generate_series(1,20) as k);

update gems set label = ('{thin,quality,wow}'::text[])[ceil(random()*3)];

update gems set label = 'thin'
       where facets < 10;
update gems set label = 'quality', price = 25.00
       where facets >= 10 and facets < 20;
update gems set label = 'wow', price = money '100.00'
             where facets >= 20;

select * from gems;

delete from gems where facets < 5;
delete from events where id > 1000 and answer = 'B';


--- Foreign Keys

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


--- Joins

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
