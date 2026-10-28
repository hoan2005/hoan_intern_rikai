



SELECT 
    c.name AS category_name,
    COUNT(fc.film_id) AS total_films
FROM 
    category c
INNER JOIN 
    film_category fc ON c.category_id = fc.category_id
GROUP BY 
    c.name
ORDER BY 
    total_films DESC;