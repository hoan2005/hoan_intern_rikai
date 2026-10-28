SELECT 
    title,
    release_year,
    length,
    rental_rate,
    rating
FROM film
WHERE rating = 'PG-13'                  
  AND length > 120                      
  AND rental_rate > 2.99                
ORDER BY length DESC                    
LIMIT 10;                               