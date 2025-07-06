-- Show Cross vs Inner vs Outer Join


-- DROP TABLE foods;

CREATE TABLE foods
(
  food TEXT,
  color TEXT
)
;

INSERT INTO foods VALUES
    (NULL, 'Black'),
    ('Apple', 'Green'),
    ('Popsicle', 'Blue'),
    ('Potato', 'Red'),
    ('Potato', 'White')
;


-- DROP TABLE things;

CREATE TABLE things
(
  thing TEXT,
  color TEXT
);

INSERT INTO things VALUES
    (NULL, 'Orange'),
    ('Hat', 'Purple'),
    ('Scarf', 'Green'),
    ('Shirt', 'Black'),
    ('Table', 'White'),
    ('Truck', 'Red')
;


SELECT * FROM foods
ORDER BY 1, 2
;

SELECT * FROM things
ORDER BY 1, 2
;

SELECT
    f.food AS f_food,
    f.color AS f_color,
    t.thing AS t_thing,
    t.color AS t_color
FROM foods f
	CROSS JOIN things t
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
