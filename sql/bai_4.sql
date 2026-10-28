


SELECT 
    COUNT(payment_id) AS total_transactions,
    SUM(amount) AS total_revenue
FROM payment
WHERE payment_date >= '2022-05-01 00:00:00' 
  AND payment_date < '2022-06-01 00:00:00'