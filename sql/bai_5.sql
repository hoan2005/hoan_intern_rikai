-- lấy dữ liệu từ bnagr film
-- case when  then cấu trúc điều kiên
-- nếu when đúng thì sẽ chạy trong then

SELECT 
    CASE 
        WHEN rental_rate < 1.00 THEN 'Cheap'
        WHEN rental_rate BETWEEN 1.00 AND 3.00 THEN 'Moderate'
        ELSE 'Expensive'
    END AS price_category,
    COUNT(*) AS total_films
FROM film
GROUP BY price_category
ORDER BY total_films DESC