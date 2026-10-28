SELECT 
    CONCAT(a1.first_name, ' ', a1.last_name) AS actor_1,
    CONCAT(a2.first_name, ' ', a2.last_name) AS actor_2,
    COUNT(fa1.film_id) AS shared_films
FROM film_actor fa1
JOIN film_actor fa2 ON fa1.film_id = fa2.film_id 
                   AND fa1.actor_id < fa2.actor_id    
JOIN actor a1 ON fa1.actor_id = a1.actor_id
JOIN actor a2 ON fa2.actor_id = a2.actor_id
GROUP BY 
    a1.actor_id,   
    a2.actor_id    
HAVING COUNT(fa1.film_id) >= 1 -- thay đổi 3 thành 1  vì thực tê dữ liệu hiện chưa có các cặp đóng cùng nhau trên 3 phim                          
ORDER BY shared_films DESC;