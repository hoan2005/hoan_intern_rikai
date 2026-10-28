create table film_3
(
id serial primary key,

replace_cost numeric(12,2),
rating smallint,

create_at TIMESTAMP default CURRENT_TIMESTAMP
)




INSERT INTO film_3 (title, replace_cost, rating) VALUES
('The Shawshank Redemption', 19.99, 'PG'),
('The Godfather', 14.99, 'G'),
('The Dark Knight', 24.99, 'PG-13'),
('Pulp Fiction', 12.99, 'R'),
('Forrest Gump', 9.99, 'G'),
('Inception', 21.99, 'PG-13'),
('Fight Club', 15.49, 'PG'),
('The Matrix', 18.99, 'R'),
('Goodfellas', 22.50, 'PG-13'),
('Interstellar', 29.99, 'NC-17'),
('Parasite', 19.99, 'PG'),
('Gladiator', 16.99, 'G'),
('The Lion King', 11.99, 'G'),
('Avengers: Endgame', 25.00, 'R'),
('Spirited Away', 20.49, 'PG-13'),
('Whiplash', 14.99, 'PG'),
('The Prestige', 17.50, 'R'),
('The Departed', 21.00, 'PG-13'),
('Coco', 19.99, 'G'),
('Joker', 23.49, 'R');

-- where dùng để đưa ra điều kiện 
-- ilike dùng để kiểm tra chuỗi có chứa các ký tự đưa ra
-- between để đưa ra 1 khoảng kiểm tra
-- in là dùng để kiểm tra gia strij trong cột có tồn tại trong 1 list hay không
select title,replace_cost,rating from film_3  where 
title ilike '%love%' and replace_cost between 10.00 and 20.00 and rating in ('G','PG','PG-13')