# CREATE TABLE sau khi tái cấu trúc (3NF)

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    author_name VARCHAR(255) NOT NULL,
    author_email VARCHAR(255) UNIQUE NOT NULL
);


CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);


CREATE TABLE posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    post_title VARCHAR(255) NOT NULL,
    post_content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Sửa thành kiểu DATETIME chuẩn
    views_count INT DEFAULT 0,
    
    -- Khóa ngoại liên kết
    CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_posts_category FOREIGN KEY (category_id) REFERENCES categories(category_id)

);

# CREATE INDEX cho truy vấn nóng

CREATE INDEX idx_category_created_desc 
ON posts (category_id, created_at DESC);

#  ghi chú về vấn đề created_at kiểu chuỗi cũ
Lỗi sắp xếp (Sorting bug)
Tốn dung lượng lưu trữ & Chậm Index
Mất các hàm toán học/thời gian