SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
 
    ('2022-09-01'::date - MAX(p.payment_date)::date) AS recency,

    SUM(p.amount) AS monetary
FROM customer c
JOIN payment p ON c.customer_id = p.customer_id
WHERE p.payment_date < '2022-09-01'      
GROUP BY 
    c.customer_id, 
    c.first_name, 
    c.last_name
ORDER BY 
    monetary DESC;                        