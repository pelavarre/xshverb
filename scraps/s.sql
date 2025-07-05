-- Show Outer vs Inner Join


DROP TABLE foods;

CREATE TABLE foods
(
  food TEXT,
  color TEXT
)
;

INSERT INTO foods VALUES
    ('Apple', 'Green'),
    ('Potato', 'White'),
    ('Potato', 'Red'),
    ('Popsicle', 'Blue'),
    (NULL, 'Black')
;


DROP TABLE things;

CREATE TABLE things
(
  thing TEXT,
  color TEXT
);

INSERT INTO things VALUES
    ('Truck', 'Red'),
    ('Scarf', 'Green'),
    ('Table', 'White'),
    ('Hat', 'Purple'),
    ('Shirt', 'Black'),
    (NULL, 'Orange')
;


SELECT * FROM foods
;

SELECT * FROM things
;


SELECT
    foods.food AS foods_food,
    foods.color AS foods_color,
    things.thing AS things_thing,
    things.color AS things_color
FROM foods
	INNER JOIN things
		ON foods.color = things.color
;


SELECT
    f.food AS f_food,
    f.color AS f_color,
    t.thing AS t_thing,
    t.color AS t_color
FROM foods f
	INNER JOIN things t
		ON f.color = t.color
;


SELECT
    f.food AS f_food,
    f.color AS f_color,
    t.thing AS t_thing,
    t.color AS t_color
FROM foods f
	LEFT OUTER JOIN things t
		ON f.color = t.color
;


SELECT
    f.food AS f_food,
    f.color AS f_color,
    t.thing AS t_thing,
    t.color AS t_color
FROM foods f
	RIGHT OUTER JOIN things t
		ON f.color = t.color
;




SELECT
    f.food AS f_food,
    f.color AS f_color,
    t.thing AS t_thing,
    t.color AS t_color
FROM foods f
	LEFT OUTER JOIN things t
		ON f.color = t.color

UNION DISTINCT

SELECT
    f.food AS f_food,
    f.color AS f_color,
    t.thing AS t_thing,
    t.color AS t_color
FROM foods f
	RIGHT OUTER JOIN things t
		ON f.color = t.color
;
