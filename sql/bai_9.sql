SELECT 
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    f.title AS film_title,
    r.rental_date
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.id
WHERE r.return_date IS NULL                                 
  AND ('2022-06-01'::date - r.rental_date::date) > 7;        