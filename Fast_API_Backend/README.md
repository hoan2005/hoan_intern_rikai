# Mini CRUD API - Backend

## Mô tả

Backend REST API quản lý người dùng và bài viết. Ứng dụng cung cấp các thao
tác tạo, xem, cập nhật và xóa dữ liệu; bài viết còn hỗ trợ tìm kiếm, lọc và
phân trang. Dữ liệu được lưu trong PostgreSQL.

Các router chỉ tiếp nhận request, lấy dependency và chuyển tiếp đến service.
Service chịu trách nhiệm kiểm tra nghiệp vụ, phân quyền, xử lý cache và gọi
repository để truy vấn/cập nhật dữ liệu.

## Định dạng phản hồi API

Tất cả API trả phản hồi thành công theo cấu trúc:

```json
{"success": true, "message": "Success", "data": {}}
```

`data` chứa payload của endpoint. Phản hồi lỗi dùng cấu trúc:

```json
{"success": false, "message": "Mô tả lỗi"}
```

Mã HTTP vẫn thể hiện kết quả (ví dụ `401`, `404`, `422`, `500`); endpoint
xóa thành công trả `200` với envelope chuẩn. Các trang tài liệu `/docs`,
`/redoc` và `/openapi.json` không bị bọc trong envelope.

## Công nghệ sử dụng

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Redis
- Psycopg

## Ghi nhật ký

Ứng dụng ghi các request đến, mã trạng thái phản hồi, thời gian xử lý và
ngoại lệ vào `app.log` tại thư mục gốc của dự án. Các lỗi validation được
ghi lại cùng đường dẫn và tên trường lỗi, không ghi giá trị dữ liệu gửi lên.
Tệp log được tạo tự động khi ứng dụng nhận request và được Git bỏ qua.

## Yêu cầu môi trường

- Python 3.10 trở lên
- PostgreSQL đang chạy và có database để ứng dụng kết nối
- Redis đang chạy
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

Thêm khóa bí mật JWT vào file môi trường (dùng khóa ngẫu nhiên dài khi chạy
thực tế):

```env
JWT_SECRET_KEY=<your-random-secret>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
SCRYPT_ALGORITHM=scrypt
SCRYPT_N=16384
SCRYPT_R=8
SCRYPT_P=1
```

Thêm cấu hình Redis và giới hạn request vào `app/.env`:

```env
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
```

Giới hạn mặc định của ứng dụng là 100 request mỗi client trong 60 giây.
`app/.env.example` đặt `RATE_LIMIT_REQUESTS=10` để kiểm thử; đổi thành `100`
khi không còn cần kiểm thử giới hạn thấp. `REDIS_MAX_CONNECTIONS` cấu hình
số kết nối tối đa trong pool Redis của mỗi tiến trình ứng dụng. Không commit
`app/.env`; có thể sao chép các biến Redis từ `app/.env.example`.

Các request `GET /posts` công khai, không kèm bộ lọc được cache trong Redis
60 giây theo khóa `posts:page={page}:limit={limit}`. Request có xác thực hoặc
có bộ lọc luôn đọc dữ liệu mới từ database. Tạo, cập nhật hoặc xóa bài viết
sẽ xóa toàn bộ các cache trang bài viết. Response `GET /posts` có header
`X-Data-Source: redis` khi lấy từ cache, hoặc `X-Data-Source: database` khi
truy vấn cơ sở dữ liệu.

Giữ nguyên cấu hình SCRYPT sau khi đã tạo tài khoản để các mật khẩu hiện có
tiếp tục được xác thực.

Nếu có `DATABASE_URL`, ứng dụng sẽ ưu tiên giá trị này thay cho các biến
`DB_*`. Không commit thông tin xác thực thật lên Git. File `app/.env` đã
được Git bỏ qua.

## Giới hạn tốc độ

Mỗi địa chỉ IP được giới hạn theo `RATE_LIMIT_REQUESTS` trong khoảng thời
gian `RATE_LIMIT_WINDOW_SECONDS`. Request vượt ngưỡng nhận phản hồi `429 Too
Many Requests` kèm header `Retry-After`. Redis dùng chung bộ đếm giữa các
worker; nếu Redis không khả dụng, API trả về `503` thay vì bỏ qua giới hạn.

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
| Xác thực | `/profile` | Hồ sơ người dùng đang đăng nhập |
| Người dùng | `/users` | Danh sách và tạo người dùng |
| Người dùng | `/users/{user_id}` | Xem, cập nhật hoặc xóa người dùng |
| Người dùng | `/users/{user_id}/posts` | Lấy bài viết của một hoặc nhiều người dùng |
| Bài viết | `/posts` | Danh sách, tạo và tìm kiếm bài viết |
| Bài viết | `/posts/{post_id}` | Xem, cập nhật hoặc xóa bài viết |
| Bài viết | `/users/{user_id}/posts` | Lấy bài viết của một người dùng |

Để gọi API cần đăng nhập trong Swagger, gọi `POST /login` trước, sao chép
JWT trong `data.access_token` của response, sau đó bấm **Authorize** và dán
chỉ token vào trường Bearer. Swagger sẽ tự thêm tiền tố `Bearer` vào header.

Danh sách bài viết hỗ trợ các tham số lọc `author_id`, `category`,
`published`, tìm kiếm `search`, và phân trang `page`, `limit`. Kết quả được
sắp xếp theo thời gian tạo tăng dần; nếu thời gian tạo trùng nhau thì sắp
xếp tiếp theo ID để giữ thứ tự ổn định. Ví dụ:

```text
GET /posts?search=fastapi&page=1&limit=10
```


### Quyền truy cập và vai trò

`GET /profile` yêu cầu JWT hợp lệ. Khách chưa đăng nhập chỉ thấy bài viết
đã xuất bản; người dùng đăng nhập thấy thêm bản nháp do chính mình tạo.
Người dùng chỉ được xem, sửa và xóa bản nháp của mình. Truy cập bài viết
không thuộc quyền được phép trả về `404` để không tiết lộ bài viết riêng tư.

`GET /users` yêu cầu đăng nhập; `POST /users` chỉ admin được dùng. User
không thể tự gán hoặc đổi role thành `admin`; tài khoản admin ban đầu được
cấp quyền trực tiếp trong database. Admin có thể quản lý mọi người dùng và
bài viết; user chỉ quản lý hồ sơ của mình và bản nháp của mình. Tạo user
qua `POST /users` đồng thời tạo một bài viết chào mừng; cả hai được commit
trong cùng một transaction hoặc cùng rollback nếu có lỗi.

Có thể lấy bài viết của nhiều người dùng bằng cách phân tách ID bằng dấu
phẩy, ví dụ `GET /users/7,8/posts`. Kết quả được nhóm theo `user_id` và tải
bằng một truy vấn `joinedload`; mỗi người dùng chỉ thấy bài public của người
khác, còn bài nháp chỉ hiển thị cho chính chủ. Admin có thể xem bài public
và chưa public của tất cả người dùng.

TAI_KHOAN_USER:
username : lam
password: lamxinhyeu

TAI_KHOAN_ADMIN:
username: hoan
passwword : hoan12345

## Cấu trúc thư mục

```text
Fast_API_Backend/
├── app/
│   ├── __init__.py
│   ├── .env.example                 # Mẫu cấu hình Redis và rate limit
│   ├── main.py                     # Khởi tạo ứng dụng, Redis và đăng ký router/middleware
│   ├── database.py                 # Cấu hình kết nối SQLAlchemy
│   ├── dependencies.py             # Database session và xác thực người dùng
│   ├── exceptions.py               # Handler cho validation, HTTP và lỗi server
│   ├── middleware.py               # Ghi log request/response
│   ├── post_cache.py               # Cache danh sách bài viết và invalidation Redis
│   ├── rate_limit.py               # Giới hạn request theo client bằng Redis
│   ├── response_format.py          # Chuẩn hóa envelope response toàn cục
│   ├── core/
│   │   ├── config.py               # Đọc cấu hình ứng dụng và database
│   │   └── logging_config.py       # Cấu hình ghi log vào app.log
│   ├── migrations/
│   │   ├── 0001_add_post_filter_fields.sql  # Các trường lọc bài viết
│   │   └── 0002_add_user_role.sql           # Vai trò người dùng
│   ├── models/
│   │   ├── post_models.py          # Model bài viết và quan hệ với người dùng
│   │   └── user_models.py          # Model người dùng
│   ├── routers/
│   │   ├── auth_routers.py         # Endpoint đăng nhập và hồ sơ
│   │   ├── post_routers.py         # Endpoint API bài viết
│   │   └── user_routers.py         # Endpoint API người dùng
│   ├── schemas/
│   │   ├── post_schemas.py         # Schema request/response bài viết
│   │   └── user_schemas.py         # Schema request/response người dùng
│   ├── services/
│   │   ├── auth_service.py         # Xác thực và tạo access token
│   │   ├── post_service.py         # Nghiệp vụ bài viết và điều phối cache
│   │   └── user_service.py         # Nghiệp vụ người dùng và phân quyền
│   └── repositories/
│       ├── post_repo.py            # Truy vấn cơ sở dữ liệu bài viết
│       └── user_repo.py            # Truy vấn người dùng và eager loading bài viết
├── tests/
│   ├── test_auth.py                # Kiểm thử xác thực và quyền truy cập
│   ├── test_logging.py             # Kiểm thử logging và response envelope
│   ├── test_posts.py               # Kiểm thử API và chức năng bài viết
│   ├── test_rate_limit.py          # Kiểm thử giới hạn request
│   └── test_users.py               # Kiểm thử người dùng và eager loading
├── requirements.txt                # Dependencies của dự án
├── pyproject.toml                  # Cấu hình công cụ Python
├── .flake8                         # Cấu hình Flake8
├── .gitignore                      # Các file và thư mục Git bỏ qua
├── .github/
│   └── copilot-instructions.md     # Hướng dẫn cho Copilot trong repository
└── README.md                       # Tài liệu dự án
```

Các file `__init__.py` trong thư mục con được lược bỏ để sơ đồ gọn hơn.

## Kiểm thử

Cài `pytest` nếu môi trường chưa có, sau đó chạy:

```bash
pip install pytest
PYTHONPATH=. pytest
```
