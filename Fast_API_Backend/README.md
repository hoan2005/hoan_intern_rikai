# Mini CRUD API - Backend

## Mô tả

Backend REST API quản lý người dùng và bài viết. Ứng dụng cung cấp các thao
tác tạo, xem, cập nhật và xóa dữ liệu; bài viết còn hỗ trợ tìm kiếm, lọc và
phân trang. Dữ liệu được lưu trong PostgreSQL.

## Công nghệ sử dụng

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Psycopg

## Yêu cầu môi trường

- Python 3.10 trở lên
- PostgreSQL đang chạy và có database để ứng dụng kết nối
- Git

## Cài đặt

Clone repository rồi chuyển đến thư mục backend:

```bash
git clone https://github.com/hoan2005/hoan_intern_rikai.git
cd hoan_intern_rikai/Fast_API_Backend
```

Tạo và kích hoạt môi trường ảo:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Trên Windows PowerShell, kích hoạt môi trường bằng:

```powershell
.venv\Scripts\Activate.ps1
```

Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

## Cấu hình biến môi trường

Ứng dụng đọc cấu hình database từ file `app/.env` hoặc biến môi trường. Có
thể cấu hình bằng một trong hai cách sau.

Sử dụng chuỗi kết nối `DATABASE_URL`:

```env
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<database>
```

Hoặc khai báo từng thông tin kết nối:

```env
DB_USER=postgres
DB_PASSWORD=<your-password>
DB_HOST=localhost
DB_PORT=5432
DB_NAME=<your-database>
```

Nếu có `DATABASE_URL`, ứng dụng sẽ ưu tiên giá trị này thay cho các biến
`DB_*`. Không commit thông tin xác thực thật lên Git. File `app/.env` đã
được Git bỏ qua.

## Chạy dự án

Đảm bảo PostgreSQL đã chạy và thông tin kết nối đã được cấu hình, sau đó
khởi động API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Cách sử dụng

Có thể xem và gửi request trực tiếp từ Swagger UI tại `/docs`. Các nhóm API
chính:

| Nhóm | Endpoint | Chức năng |
|---|---|---|
| Người dùng | `/users` | Danh sách và tạo người dùng |
| Người dùng | `/users/{user_id}` | Xem, cập nhật hoặc xóa người dùng |
| Bài viết | `/posts` | Danh sách, tạo và tìm kiếm bài viết |
| Bài viết | `/posts/{post_id}` | Xem, cập nhật hoặc xóa bài viết |
| Bài viết | `/users/{user_id}/posts` | Lấy bài viết của một người dùng |

Danh sách bài viết hỗ trợ các tham số lọc `author_id`, `category`,
`published`, tìm kiếm `search`, và phân trang `page`, `limit`. Kết quả được
sắp xếp theo thời gian tạo tăng dần; nếu thời gian tạo trùng nhau thì sắp
xếp tiếp theo ID để giữ thứ tự ổn định. Ví dụ:

```text
GET /posts?search=fastapi&page=1&limit=10
```

Không có tài khoản demo được cấu hình sẵn. Có thể tạo người dùng mới thông
qua `POST /users` trong Swagger UI.

## Cấu trúc thư mục

```text
Fast_API_Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Khởi tạo FastAPI và đăng ký router
│   ├── database.py                 # Cấu hình kết nối SQLAlchemy
│   ├── dependencies.py             # Dependency dùng chung, ví dụ database session
│   ├── exceptions.py               # Đăng ký xử lý ngoại lệ
│   ├── core/
│   │   └── config.py               # Đọc cấu hình ứng dụng và database
│   ├── migrations/
│   │   └── 0001_add_post_filter_fields.sql  # Migration cho các trường lọc bài viết
│   ├── models/
│   │   └── post_models.py          # Model cơ sở dữ liệu bài viết
│   ├── routers/
│   │   └── post_routers.py         # Endpoint API cho bài viết
│   ├── schemas/
│   │   └── post_schemas.py         # Schema kiểm tra request/response bài viết
│   ├── services/
│   │   └── post_service.py         # Logic nghiệp vụ bài viết
│   └── repositories/
│       └── post_repo.py            # Truy vấn cơ sở dữ liệu bài viết
├── tests/
│   └── test_posts.py               # Kiểm thử API và chức năng bài viết
├── requirements.txt                # Dependencies của dự án
├── pyproject.toml                  # Cấu hình công cụ Python
├── .flake8                         # Cấu hình Flake8
├── .gitignore                      # Các file và thư mục Git bỏ qua
└── README.md                       # Tài liệu dự án
```

Với các thư mục có nhiều file, cấu trúc trên chỉ hiển thị một file làm ví dụ.

## Kiểm thử

Cài `pytest` nếu môi trường chưa có, sau đó chạy:

```bash
pip install pytest
PYTHONPATH=. pytest
```
