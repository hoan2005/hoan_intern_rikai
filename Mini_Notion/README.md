# Mini Notion

Khung backend Python/FastAPI được tổ chức theo các lớp trách nhiệm:

- `app/controllers/`: tiếp nhận request và trả response.
- `app/services/`: xử lý logic nghiệp vụ.
- `app/repositories/`: tương tác với cơ sở dữ liệu.
- `app/models/`: định nghĩa model và mapping bảng cơ sở dữ liệu.
- `app/schemas/`: định nghĩa schema Pydantic cho Create, Update và Read.
- `app/core/`: cấu hình, bảo mật và thông báo lỗi tiếng Việt.
- `app/db/`: cấu hình kết nối và quản lý session cơ sở dữ liệu.
- `alembic/versions/`: lưu các migration cơ sở dữ liệu.
- `tests/`: lưu các bài kiểm thử.

## Cấu hình PostgreSQL

Sao chép `app/.env.example` thành `app/.env`, sau đó cập nhật thông tin
PostgreSQL và `JWT_SECRET_KEY`:

```bash
cp -n app/.env.example app/.env
```

Ứng dụng đọc cấu hình từ các biến `APP_*`, `DB_*`, `JWT_SECRET_KEY` và
`BCRYPT_*`. Kết nối cơ sở dữ liệu sử dụng SQLAlchemy với driver psycopg 3.
Không đưa `app/.env` hoặc secret thật lên Git.

## Đăng ký, đăng nhập và xác thực

- `POST /auth/register`: tạo user mới (email, mật khẩu tối thiểu 8 ký tự,
  xác nhận mật khẩu, họ tên); hai trường mật khẩu phải khớp. Mật khẩu được
  băm bằng bcrypt. Trả `409` nếu email đã được đăng ký.
- `POST /auth/login`: nhận email và mật khẩu, trả về `access_token` dạng JWT
  khi thông tin đăng nhập hợp lệ.
- `GET /auth/me`: trả thông tin user hiện tại, không bao gồm mật khẩu.
- Gửi token trong header
  `Authorization: Bearer <access_token>`.

JWT được ký bằng `JWT_SECRET_KEY`, có thời hạn mặc định 30 phút. Có thể đặt
`JWT_ACCESS_TOKEN_EXPIRE_MINUTES` từ 30 đến 60 trong `app/.env`. Token sai,
hết hạn hoặc không có user tương ứng sẽ bị từ chối với HTTP `401`.

Dependency `get_db` trong `app/db/session.py` tạo một session cho mỗi request
được inject vào endpoint bằng `Depends(get_db)`, sau đó đóng session trong
`finally`. Kết nối vật lý được SQLAlchemy lấy từ pool khi session thực hiện
truy vấn và được trả lại pool khi session đóng.

## Bộ sưu tập

- `GET /collections`: liệt kê bộ sưu tập của user đang đăng nhập; hỗ trợ
  `limit` (mặc định 10, tối đa 100) và `offset` (mặc định 0).
- `POST /collections`: tạo bộ sưu tập với `name` từ 1 đến 150 ký tự; tên
  được loại bỏ khoảng trắng ở hai đầu.
- `GET /collections/{id}`, `PATCH /collections/{id}` và
  `DELETE /collections/{id}` chỉ truy cập dữ liệu của user
  hiện tại. ID không tồn tại hoặc thuộc user khác đều trả `404`.
- Khi xóa một bộ sưu tập vẫn còn ghi chú, các ghi chú đó cũng bị xóa theo
  (`ON DELETE CASCADE` và quan hệ `delete-orphan`).

Có thể kiểm tra thủ công tại `/docs`: đăng ký và đăng nhập bằng hai tài khoản,
sao chép token của từng tài khoản rồi dùng nút **Authorize** để thiết lập
token. Tạo bộ sưu tập bằng tài khoản thứ nhất, chuyển sang token của tài khoản
thứ hai và gọi `GET`, `PATCH`, `DELETE` với ID đó; cả ba thao tác cần trả `404`.

## Ghi chú, ghim, tìm kiếm và phân trang

- `POST /collections/{id}/notes`: tạo ghi chú trong bộ sưu tập của user hiện
  tại. Request nhận `title` (bắt buộc, 1–255 ký tự) và `body` (tùy chọn,
  tối đa 10.000 ký tự); khoảng trắng thừa ở đầu/cuối tiêu đề được loại bỏ.
  Thành công trả `201` cùng ghi chú vừa tạo.
- `GET /collections/{id}/notes`: liệt kê ghi chú của bộ sưu tập đó, hỗ trợ
  `q`, `limit` (mặc định 10, tối đa 100) và `offset` (mặc định 0).
- `GET /notes`: liệt kê tất cả ghi chú của user hiện tại; hỗ trợ `collection_id`,
  `q` (tìm tiêu đề không phân biệt hoa thường) và `tag`.
- `GET /notes/{id}`: lấy chi tiết ghi chú.
- `PATCH /notes/{id}`: cập nhật một phần các trường `title`, `body`,
  `is_pinned`. Tiêu đề không được để trống; có thể gửi `body: null` để xóa
  nội dung. Ví dụ:

  ```json
  {
    "title": "Ghi chú đã cập nhật",
    "body": "Nội dung mới",
    "is_pinned": true
  }
  ```

- `DELETE /notes/{id}`: xóa cứng ghi chú, thành công trả `204`.
- Tất cả danh sách trả về `{ "items": [...], "total": 42, "limit": 10,
  "offset": 0 }`; `total` được đếm sau khi áp dụng bộ lọc và trước phân trang.
  Thứ tự là `is_pinned DESC, updated_at DESC`; `q` dùng `ILIKE` với tham số
  bind. `limit` phải từ 1 đến 100, `offset` phải lớn hơn hoặc bằng 0.
- Quyền sở hữu được kiểm tra qua bộ sưu tập của ghi chú. ID không tồn tại hoặc
  thuộc user khác đều trả `404`, bao gồm thao tác trên ghi chú đơn lẻ và các
  endpoint ghi chú lồng trong bộ sưu tập. Request sai dữ liệu trả `422` với
  thông báo lỗi tiếng Việt.

## Chạy ứng dụng và kiểm tra kết nối

Áp dụng migration trên database hiện có bằng lệnh:

```bash
alembic upgrade head
```

Migration đảm bảo `users.email` là duy nhất, tag không trùng tên trong cùng
user, index danh sách note theo collection/thời gian cập nhật và khóa chính
ghép của `note_tags`. Các ràng buộc tương đương đã có sẽ được giữ nguyên.

Chạy API bằng lệnh:

```bash
python -m uvicorn app.main:app --reload
```

Sau đó mở `http://127.0.0.1:8000/health/db`. Endpoint trả về trạng thái
`connected` nếu truy vấn kiểm tra PostgreSQL thành công; nếu không, trả mã
HTTP `503`.

## Cài đặt dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Trên Windows PowerShell, kích hoạt môi trường bằng:

```powershell
.venv\Scripts\Activate.ps1
```
