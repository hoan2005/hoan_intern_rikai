-- tạo bảng film
create table film_2 (
id serial primary key,
rating smallint not null,
rental_rate numeric(12,2) not NULL,
created_at TIMESTAMP default CURRENT_TIMESTAMP

)

-- thêm dữ liệu vào bảng
INSERT INTO film_2 (rating, rental_rate) VALUES
(5, 2.99),
(4, 4.99),
(5, 3.99),
(4, 2.99),
(3, 1.99),
(5, 3.99),
(4, 2.49),
(5, 2.99),
(4, 3.49),
(5, 4.49),
(5, 3.99),
(4, 2.99),
(5, 1.99),
(4, 4.99),
(5, 3.49),
(5, 2.49),
(4, 2.99),
(4, 3.49),
(5, 2.99),
(4, 3.99)
-- group by nhóm các ratinh giống nhau lịa làm 1
-- count(*) đếm số lượng dòng trong từng nhóm
-- avg  tính trung bình trên 1 cột
-- order by xắp xếp dữ liệu
select rating,count(*) as so_luong_phim,
Round(AVG(rental_rate),2) as gia_trung_binh from film_2 group by rating order by so_luong_phim desc 