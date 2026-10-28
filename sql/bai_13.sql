WITH daily_summary AS (
   
    SELECT 
        payment_date::date AS pay_date,
        SUM(amount) AS daily_amount
    FROM payment
    WHERE payment_date >= '2022-05-01' 
      AND payment_date < '2022-06-01'
    GROUP BY payment_date::date
)

SELECT 
    pay_date,
    daily_amount,
    SUM(daily_amount) OVER (ORDER BY pay_date) AS running_total
FROM daily_summary
ORDER BY pay_date;