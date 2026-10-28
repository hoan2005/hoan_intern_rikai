WITH ranked_films AS (
    SELECT 
        c.name AS category_name,
        f.title,
        SUM(p.amount) AS revenue,
        DENSE_RANK() OVER (
            PARTITION BY c.category_id 
            ORDER BY SUM(p.amount) DESC
        ) AS rank_in_category
    FROM category c
    JOIN film_category fc ON c.category_id = fc.category_id
    JOIN film f ON fc.film_id = f.id                   
    JOIN inventory i ON f.id = i.film_id              
    JOIN rental r ON i.inventory_id = r.inventory_id
    JOIN payment p ON r.rental_id = p.rental_id
    GROUP BY c.category_id, c.name, f.id, f.title     
)

SELECT 
    category_name,
    title,
    revenue,
    rank_in_category AS rank
FROM ranked_films
WHERE rank_in_category <= 2
ORDER BY category_name, rank_in_category;