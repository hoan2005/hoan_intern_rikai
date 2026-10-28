# 1 Thực thể + Quan hệ
Khách hàng (Customer): Đặt nhiều đơn hàng.

Nhà hàng (Restaurant): Sở hữu một thực đơn gồm nhiều món ăn, và nhận nhiều đơn hàng.

Món ăn (MenuItem): Thuộc thực đơn của một nhà hàng, có thể nằm trong nhiều đơn hàng (thông qua bảng trung gian).

Tài xế (Driver): Được phân công vận chuyển cho nhiều đơn hàng (mỗi đơn hàng tại một thời điểm gắn với 1 tài xế).

Đơn hàng (Order): Lưu thông tin tổng quan về một giao dịch đặt món của khách tại nhà hàng.

Chi tiết đơn hàng (OrderItem): Lưu danh sách món ăn, số lượng và giá tiền tại thời điểm đặt (snapshot price) cho từng đơn hàng.

Lịch sử trạng thái đơn hàng (OrderStatusHistory): Ghi nhận quá trình thay đổi trạng thái của đơn hàng 

# Các bảng dữ liệu đạt chuẩn 3NF (với PK và FK)

-- 1. Bảng Khách hàng
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    address TEXT NOT NULL
);

-- 2. Bảng Nhà hàng
CREATE TABLE restaurants (
    restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL
);

-- 3. Bảng Món ăn (Thuộc thực đơn nhà hàng)
CREATE TABLE menu_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_menu_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

-- 4. Bảng Tài xế
CREATE TABLE drivers (
    driver_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    vehicle_plate VARCHAR(50) NOT NULL
);

-- 5. Bảng Đơn hàng
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    driver_id INT NULL, -- Có thể NULL khi mới đặt, chưa phân công tài xế
    current_status VARCHAR(50) NOT NULL DEFAULT 'placed',
    placed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_order_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    CONSTRAINT fk_order_driver FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- 6. Bảng Chi tiết đơn hàng (N-N giữa Order và MenuItem + Snapshot giá)
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL, -- Lưu giá cứng tại thời điểm đặt món
    
    CONSTRAINT fk_item_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_item_menu FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

-- 7. Bảng Lịch sử trạng thái đơn hàng (Audit Trail)
CREATE TABLE order_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_history_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
# Sơ đồ ERD
Table customers {
  customer_id int [pk, increment]
  full_name varchar(255)
  phone varchar(20) [unique]
  address text
}

Table restaurants {
  restaurant_id int [pk, increment]
  restaurant_name varchar(255)
  address text
}

Table menu_items {
  item_id int [pk, increment]
  restaurant_id int
  item_name varchar(255)
  price decimal(10,2)
}

Table drivers {
  driver_id int [pk, increment]
  full_name varchar(255)
  phone varchar(20) [unique]
  vehicle_plate varchar(50)
}

Table orders {
  order_id int [pk, increment]
  customer_id int
  restaurant_id int
  driver_id int [null]
  current_status varchar(50)
  placed_at datetime
}

Table order_items {
  order_item_id int [pk, increment]
  order_id int
  item_id int
  quantity int
  unit_price decimal(10,2)
}

Table order_status_history {
  history_id int [pk, increment]
  order_id int
  status varchar(50)
  changed_at datetime
}


Ref: menu_items.restaurant_id > restaurants.restaurant_id
Ref: orders.customer_id > customers.customer_id
Ref: orders.restaurant_id > restaurants.restaurant_id
Ref: orders.driver_id > drivers.driver_id
Ref: order_items.order_id > orders.order_id
Ref: order_items.item_id > menu_items.item_id
Ref: order_status_history.order_id > orders.order_id

# Chỉ mục cho truy vấn: "Đơn hàng gần đây của tôi"
CREATE INDEX idx_customer_placed_desc 
ON orders (customer_id, placed_at DESC);