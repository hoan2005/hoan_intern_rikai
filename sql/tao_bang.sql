
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);


CREATE TABLE film (
    film_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_year INT,
    length INT,
    rental_rate DECIMAL(5,2),
    rating VARCHAR(10),
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE actor (
    actor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100)
);


CREATE TABLE film_category (
    film_id INT REFERENCES film(film_id) ON DELETE CASCADE,
    category_id INT REFERENCES category(category_id) ON DELETE CASCADE,
    PRIMARY KEY (film_id, category_id)
);


CREATE TABLE film_actor (
    actor_id INT REFERENCES actor(actor_id) ON DELETE CASCADE,
    film_id INT REFERENCES film(film_id) ON DELETE CASCADE,
    PRIMARY KEY (actor_id, film_id),
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    film_id INT REFERENCES film(film_id) ON DELETE CASCADE,
    store_id INT
);


CREATE TABLE rental (
    rental_id SERIAL PRIMARY KEY,
    rental_date TIMESTAMP NOT NULL,
    inventory_id INT REFERENCES inventory(inventory_id) ON DELETE CASCADE,
    customer_id INT REFERENCES customer(customer_id) ON DELETE CASCADE,
    return_date TIMESTAMP
);

CREATE TABLE payment (
    payment_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customer(customer_id) ON DELETE CASCADE,
    rental_id INT REFERENCES rental(rental_id) ON DELETE CASCADE,
    amount DECIMAL(5,2) NOT NULL,
    payment_date TIMESTAMP NOT NULL
);