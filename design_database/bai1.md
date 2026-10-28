# xác định các lỗi 1NF/2NF/3NF
+ Khi một đơn hàng chứa nhiều tựa sách, cột book_titles nhận giá trị "Dune; Foundation" và cột quantities nhận giá trị "1; 2" gộp chung trong một ô thay vì tách thành các dòng riêng biệt.
+ Nếu chọn khóa chính là tổ hợp (order_id, book_titles): Các thông tin về đơn hàng và khách hàng như order_date, customer_name, customer_email chỉ phụ thuộc vào order_id (một phần của khóa chính).
+ Tồn tại chuỗi phụ thuộc giữa các thông tin khách hàng (ví dụ: customer_email xác định customer_name). Khách hàng không nên gắn chết vào bảng đơn hàng mà cần được quản lý độc lập.
# Thiết kế chuận 3NF
1. Bảng customers (Quản lý thông tin khách hàng)
customer_id (PK - Khóa chính): Định danh khách hàng.

customer_name: Tên khách hàng.

customer_email: Email khách hàng.

2. Bảng books (Quản lý danh mục sách)
book_id (PK - Khóa chính): Định danh đầu sách.

book_title: Tên sách.

book_price: Giá bán của sách.

3. Bảng orders (Quản lý thông tin chung của đơn hàng)
order_id (PK - Khóa chính): Mã đơn hàng.

order_date: Ngày đặt hàng.

customer_id (FK - Khóa ngoại): Tham chiếu đến customers(customer_id).

total_amount: Tổng giá trị đơn hàng.

4. Bảng order_items (Bảng chi tiết đơn hàng - giải quyết quan hệ Nhiều-Nhiều giữa orders và books)
order_item_id (PK - Khóa chính) hoặc dùng khóa chính tổ hợp (order_id, book_id).

order_id (FK - Khóa ngoại): Tham chiếu đến orders(order_id).

book_id (FK - Khóa ngoại): Tham chiếu đến books(book_id).

quantity: Số lượng mua của từng đầu sách trong đơn hàng.

unit_price: Đơn giá tại thời điểm mua (giúp lưu vết lịch sử giá).

# code DBML

Table customers {
  customer_id int [primary key]
  customer_name varchar
  customer_email varchar
}

Table books {
  book_id int [primary key]
  book_title varchar
  book_price decimal
}

Table orders {
  order_id int [primary key]
  order_date datetime
  customer_id int
  total_amount decimal
}

Table order_items {
  order_item_id int [primary key]
  order_id int
  book_id int
  quantity int
  unit_price decimal
}

// Thiết lập mối quan hệ (Foreign Keys)
Ref: orders.customer_id > customers.customer_id // Một khách hàng có nhiều đơn hàng

Ref: order_items.order_id > orders.order_id // Một đơn hàng có nhiều chi tiết

Ref: order_items.book_id > books.book_id // Một đầu sách xuất hiện trong nhiều chi tiết đơn hàng