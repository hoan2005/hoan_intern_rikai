# Hướng dẫn Sử dụng & Tài liệu API - Mini CRUD API

Tài liệu này cung cấp hướng dẫn chi tiết về cách cài đặt, chạy ứng dụng, danh sách các endpoint và cơ chế lưu trữ dữ liệu của hệ thống **Mini CRUD API** xây dựng bằng FastAPI.

---

## 1. Nơi lưu trữ dữ liệu (Data Storage)

Ứng dụng sử dụng **mô hình cơ sở dữ liệu giả lập trong bộ nhớ (In-memory Database)** bằng cấu trúc dữ liệu `dict` của Python nhằm phục vụ mục đích học tập và thử nghiệm nhanh:
* **Cơ chế:** Dữ liệu người dùng được lưu trữ tạm thời trong một biến kiểu dictionary (`fake_users_db`) nằm trong file `controllers/user.py`.
* **Đặc điểm:** 
  * Tốc độ truy xuất nhanh do nằm trên RAM.
  * Dữ liệu sẽ **bị mất** và reset về trạng thái ban đầu mỗi khi ứng dụng (server Uvicorn) bị tắt hoặc khởi động lại.
  * Tự động tăng ID (`id_counter`) cho mỗi người dùng mới được tạo thành công.

---

## 2. Hướng dẫn Cài đặt & Chạy ứng dụng

### Yêu cầu hệ thống
* Python từ `3.8` trở lên.

### Các bước thực hiện:

1. **Chuẩn bị cấu trúc thư mục dự án:**
   Đảm bảo các file mã nguồn được sắp xếp đúng theo cấu trúc sau:
   ```text
   my_user_api/
   ├── Schemas/
   │   └── user.py
   ├── controller/
   │   └── user.py
   ├── router/
   │   └── user.py
   └── main.py
   ```

2. **Cài đặt các thư viện phụ thuộc:**
   Mở terminal tại thư mục gốc của dự án và chạy lệnh sau:
   ```bash
   pip install fastapi uvicorn pydantic email-validator
   ```

3. **Khởi chạy ứng dụng:**
   Chạy lệnh Uvicorn để khởi động server (bật chế độ `--reload` để tự động cập nhật khi sửa code):
   ```bash
   uvicorn main:app --reload
   ```

4. **Truy cập giao diện tài liệu Swagger UI:**
   Mở trình duyệt web và truy cập vào đường dẫn:
   * **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 3. Danh sách các Endpoint

Dưới đây là chi tiết các endpoint được tổ chức trong router người dùng (`/users`):

### 3.1. Lấy danh sách toàn bộ người dùng
* **URL:** `GET /users`
* **Mô tả:** Trả về danh sách tất cả người dùng hiện có trong cơ sở dữ liệu giả lập.
* **Mã trạng thái thành công:** `200 OK`
* **Response Model:** `list[UserResponse]` *(Đã ẩn trường mật khẩu)*.

### 3.2. Xem chi tiết người dùng theo ID
* **URL:** `GET /users/{user_id}`
* **Tham số đường dẫn (Path Parameter):**
  * `user_id` (kiểu `int`): ID định danh của người dùng cần xem.
* **Mô tả:** Lấy thông tin chi tiết của một người dùng cụ thể.
* **Mã trạng thái thành công:** `200 OK`
* **Mã lỗi thường gặp:** `404 Not Found` (nếu không tìm thấy ID).
* **Response Model:** `UserResponse` *(Đã ẩn trường mật khẩu)*.

### 3.3. Tạo người dùng mới
* **URL:** `POST /users/them`
* **Request Body (JSON):**
  ```json
  {
    "username": "nguyenvana",
    "email": "vana@example.com",
    "password": "securepassword123"
  }
  ```
* **Mô tả:** Thêm mới một người dùng vào hệ thống. Mật khẩu được nhận vào để kiểm tra validation nhưng sẽ **không** hiển thị trong phần trả về.
* **Mã trạng thái thành công:** `201 Created`
* **Mã lỗi thường gặp:** 
  * `422 Unprocessable Entity` (nếu vi phạm quy tắc validation tiếng Việt như sai định dạng email, mật khẩu quá ngắn...).
  * `400 Bad Request` (nếu email đã tồn tại trong hệ thống).
* **Response Model:** `UserResponse` *(Đã ẩn trường mật khẩu)*.

### 3.4. Cập nhật thông tin người dùng
* **URL:** `PUT /users/{user_id}`
* **Tham số đường dẫn:** `user_id` (kiểu `int`)
* **Request Body (JSON - Có thể cập nhật một phần):**
  ```json
  {
    "username": "nguyenvanupdate",
    "email": "update@example.com",
    "password": "string"
  }
  ```
* **Mô tả:** Cập nhật thông tin của người dùng dựa theo ID.
* **Mã trạng thái thành công:** `200 OK`
* **Mã lỗi thường gặp:**
  * `404 Not Found` (nếu không tìm thấy ID).
  * `400 Bad Request` (nếu email cập nhật trùng với người dùng khác).
* **Response Model:** `UserResponse` *(Đã ẩn trường mật khẩu)*.

### 3.5. Xóa người dùng
* **URL:** `DELETE /users/{user_id}`
* **Tham số đường dẫn:** `user_id` (kiểu `int`)
* **Mô tả:** Xóa vĩnh viễn người dùng khỏi danh sách giả lập theo ID.
* **Mã trạng thái thành công:** `200 OK`
* **Response:** Thông báo xóa thành công.
  ```json
  {
    "message": "Đã xóa thành công người dùng có ID: 1"
  }
  ```
* **Mã lỗi thường gặp:** `404 Not Found` (nếu ID không tồn tại).