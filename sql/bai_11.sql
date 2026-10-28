WITH customer_spending AS (
   
    SELECT 
        c.customer_id,
        CONCAT(c.first_name, ' ', c.last_name) AS name,
        SUM(p.amount) AS total_spent
    FROM customer c
    JOIN rental r ON c.customer_id = r.customer_id      
    JOIN payment p ON r.rental_id = p.rental_id         
    GROUP BY c.customer_id, c.first_name, c.last_name
),
overall_average AS (
    
    SELECT AVG(total_spent) AS avg_spent
    FROM customer_spending
)


SELECT 
    cs.customer_id,
    cs.name,
    cs.total_spent
FROM customer_spending cs
CROSS JOIN overall_average oa
WHERE cs.total_spent > oa.avg_spent
ORDER BY cs.total_spent DESC;     

