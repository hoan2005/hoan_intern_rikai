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
- `GET /auth/me`: trả thông tin user hiện tại. Gửi token trong header
  `Authorization: Bearer <access_token>`.

JWT được ký bằng `JWT_SECRET_KEY`, có thời hạn mặc định 30 phút. Có thể đặt
`JWT_ACCESS_TOKEN_EXPIRE_MINUTES` từ 30 đến 60 trong `app/.env`. Token sai,
hết hạn hoặc không có user tương ứng sẽ bị từ chối với HTTP `401`.

Dependency `get_db` trong `app/db/session.py` tạo một session cho mỗi request
được inject vào endpoint bằng `Depends(get_db)`, sau đó đóng session trong
`finally`. Kết nối vật lý được SQLAlchemy lấy từ pool khi session thực hiện
truy vấn và được trả lại pool khi session đóng.

## Chạy ứng dụng và kiểm tra kết nối

Chạy API bằng lệnh:

```bash
python -m app.main
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
