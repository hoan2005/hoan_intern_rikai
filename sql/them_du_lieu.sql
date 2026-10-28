
INSERT INTO category (category_id, name) VALUES 
(1, 'Action'), 
(2, 'Comedy'), 
(3, 'Sci-Fi'), 
(4, 'Drama'), 
(5, 'Animation');

INSERT INTO film (film_id, title, release_year, length, rental_rate, rating) VALUES
(1, 'The Matrix', 1999, 136, 4.99, 'R'),
(2, 'Inception', 2010, 148, 4.99, 'PG-13'),
(3, 'The Hangover', 2009, 100, 2.99, 'R'),
(4, 'Interstellar', 2014, 169, 4.99, 'PG-13'),
(5, 'Toy Story', 1995, 81, 2.99, 'G'),
(6, 'The Dark Knight', 2008, 152, 4.99, 'PG-13'),
(7, 'Superbad', 2007, 113, 3.99, 'R'),
(8, 'Avatar', 2009, 162, 4.99, 'PG-13'),
(9, 'Gladiator', 2000, 155, 3.99, 'R'),
(10, 'Finding Nemo', 2003, 100, 2.99, 'G');


INSERT INTO actor (actor_id, first_name, last_name) VALUES
(1, 'Keanu', 'Reeves'),
(2, 'Leonardo', 'DiCaprio'),
(3, 'Bradley', 'Cooper'),
(4, 'Tom', 'Hanks'),
(5, 'Christian', 'Bale'),
(6, 'Scarlett', 'Johansson');

INSERT INTO film_actor (actor_id, film_id) VALUES
(1, 1), 
(2, 2), 
(3, 3), 
(2, 4), 
(4, 5), 
(5, 6),
(6, 4), 
(6, 8); 

INSERT INTO film_category (film_id, category_id) VALUES
(1, 1), (1, 3), 
(2, 1), (2, 3), 
(3, 2),         
(4, 3), (4, 4), 
(5, 5),       
(6, 1), (6, 4), 
(7, 2),         
(8, 1), (8, 3), 
(9, 1), (9, 4), 
(10, 5);        


INSERT INTO customer (customer_id, first_name, last_name, email) VALUES
(1, 'John', 'Doe', 'john.doe@email.com'),
(2, 'Alice', 'Smith', 'alice.smith@email.com'),
(3, 'Bob', 'Johnson', 'bob.johnson@email.com'),
(4, 'Emma', 'Watson', 'emma.watson@email.com'),
(5, 'Michael', 'Jordan', 'michael.jordan@email.com');


INSERT INTO inventory (inventory_id, film_id, store_id) VALUES
(101, 1, 1), (102, 1, 2),
(103, 2, 1), (104, 2, 2),
(105, 3, 1), 
(106, 4, 1), (107, 4, 2),
(108, 5, 1),
(109, 6, 1), (110, 6, 2),
(111, 7, 1),
(112, 8, 1),
(113, 9, 1),
(114, 10, 2);


INSERT INTO rental (rental_id, rental_date, inventory_id, customer_id, return_date) VALUES
(1001, '2022-05-01 09:30:00', 101, 1, '2022-05-05 10:00:00'),
(1002, '2022-05-01 14:15:00', 103, 2, '2022-05-06 12:00:00'),
(1003, '2022-05-02 10:00:00', 106, 3, '2022-05-07 15:00:00'),
(1004, '2022-05-02 16:45:00', 109, 1, '2022-05-08 09:00:00'),
(1005, '2022-05-03 11:20:00', 105, 4, '2022-05-05 14:00:00'),
(1006, '2022-05-03 18:00:00', 112, 5, '2022-05-10 16:00:00'),
(1007, '2022-05-04 13:10:00', 102, 2, '2022-05-09 11:00:00'),
(1008, '2022-05-05 15:00:00', 104, 3, '2022-05-12 10:00:00'),
(1009, '2022-05-05 19:30:00', 110, 4, '2022-05-11 13:00:00'),
(1010, '2022-05-06 08:45:00', 107, 5, '2022-05-13 15:00:00'),

(1011, '2022-04-28 10:00:00', 101, 1, '2022-05-02 10:00:00'),
(1012, '2022-06-02 14:00:00', 103, 2, '2022-06-08 16:00:00');

INSERT INTO payment (payment_id, customer_id, rental_id, amount, payment_date) VALUES
(1, 1, 1001, 10.99, '2022-05-01 09:35:00'),
(2, 2, 1002, 15.50, '2022-05-01 14:20:00'),
(3, 3, 1003, 12.99, '2022-05-02 10:05:00'),
(4, 1, 1004, 14.99, '2022-05-02 16:50:00'),
(5, 4, 1005, 8.99, '2022-05-03 11:25:00'),
(6, 5, 1006, 19.99, '2022-05-03 18:05:00'),
(7, 2, 1007, 10.99, '2022-05-04 13:15:00'),
(8, 3, 1008, 15.50, '2022-05-05 15:05:00'),
(9, 4, 1009, 14.99, '2022-05-05 19:35:00'),
(10, 5, 1010, 12.99, '2022-05-06 08:50:00'),
(11, 1, 1011, 9.99, '2022-04-28 10:05:00'),
(12, 2, 1012, 11.99, '2022-06-02 14:05:00');