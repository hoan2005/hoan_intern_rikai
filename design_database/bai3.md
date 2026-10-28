# ERD dạng DBML
Table users {
  user_id int [primary key]
  name varchar [not null]
  email varchar [unique, not null]
  created_at datetime
}

Table categories {
  category_id int [primary key]
  category_name varchar [not null]
}

Table products {
  product_id int [primary key]
  product_name varchar [not null]
  price decimal [not null] // Ràng buộc NOT NULL cho trường tiền tệ
  category_id int
}

Table orders {
  order_id int [primary key]
  user_id int
  order_date datetime
  total_amount decimal [not null] // Ràng buộc NOT NULL cho trường tiền tệ
}

Table order_items {
  order_item_id int [primary key]
  order_id int
  product_id int
  quantity int [not null]
  unit_price decimal [not null] // Ràng buộc NOT NULL cho trường tiền tệ
}

// Thiết lập mối quan hệ (Foreign Keys và các đường nối 1-N)
Ref: categories.category_id < products.category_id // Một danh mục chứa nhiều sản phẩm (1 - N)

Ref: users.user_id < orders.user_id // Một người dùng có thể đặt nhiều đơn hàng (1 - N)

Ref: orders.order_id < order_items.order_id // Một đơn hàng chứa nhiều chi tiết sản phẩm (1 - N)

Ref: products.product_id < order_items.product_id // Một sản phẩm có thể xuất hiện trong nhiều chi tiết đơn hàng (1 - N)

# Danh sách kiểm tra ràng buộc
users.email UNIQUE: Đảm bảo không có hai người dùng nào đăng ký trùng một địa chỉ email trong hệ thống, đồng thời thêm thuộc tính NOT NULL để bắt buộc phải có email khi tạo tài khoản.

price / unit_price NOT NULL: Tất cả các trường liên quan đến tiền tệ (giá sản phẩm products.price, đơn giá tại thời điểm mua order_items.unit_price, và tổng tiền orders.total_amount) đều được cấu hình bắt buộc nhập (NOT NULL) nhằm tránh sai sót tài chính.

Khóa chính (PK) và Khóa ngoại (FK):

Mỗi bảng đều có khóa chính định danh (user_id, category_id, product_id, order_id, order_item_id).

Các khóa ngoại (category_id, user_id, product_id) được liên kết chính xác để duy trì toàn vẹn dữ liệu giữa các bảng.

# Bảng cầu nối N–N
order_items (Chi tiết đơn hàng).