# Copilot Instructions — Mini Notion API

## Quy tắc giao tiếp và làm việc (ưu tiên cao nhất)
1. Chỉ dùng **tiếng Việt** khi hội thoại với người dùng (trả lời, giải thích, hỏi lại, báo cáo). Tên kỹ thuật, tên hàm và đoạn code giữ nguyên.
2. Chỉ làm **đúng yêu cầu** của người dùng. Không tự ý làm thêm, không "tiện tay" sửa chỗ không được nhờ.
3. Sau mỗi lần làm, **liệt kê những gì đã giúp sửa/thêm** (file nào, thay đổi gì, vì sao).
4. Khi muốn **thêm bất cứ thứ gì mới** (tính năng, file, thư viện, endpoint, cấu hình…): dừng lại và **hỏi người dùng trước**, nêu rõ **lý do cần thêm** để người dùng review. Chỉ thêm khi người dùng chấp nhận.
5. Nếu không chắc, hỏi lại bằng tiếng Việt. Không bịa tên hàm, endpoint hay thư viện không có thật.

## Dự án
Backend sổ tay cá nhân kiểu Notion thu nhỏ.
Stack: FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic, Pydantic v2, pydantic-settings, JWT + bcrypt.
Quan hệ: `users` 1–N `collections` 1–N `notes`; `users` 1–N `tags`; `notes` N–N `tags` qua `note_tags`.

## Phạm vi
Chỉ làm: auth (register/login/me), CRUD collections, CRUD notes (ghim, tìm theo tiêu đề `q`), tags N–N + lọc theo tag, phân trang limit/offset.
Không tự thêm: share link, upload file, OAuth, websocket, phân quyền theo vai trò, cursor pagination. Chỉ làm khi người dùng yêu cầu rõ.

## Cấu trúc thư mục
```
app/
  controllers/    # tiếp nhận API (request/response)
  services/       # xử lý logic nghiệp vụ
  repositories/   # tương tác với database
  models/         # định nghĩa mapping bảng cơ sở dữ liệu
  schemas/        # Pydantic: Create / Update / Read
  core/           # config, security, thông báo lỗi tiếng Việt
  db/             # kết nối, session
alembic/
tests/
README.md
requirements.txt
pyproject.toml    # cấu hình Black
.flake8           # cấu hình flake8
```
Luồng một chiều: **controller → service → repository → model**.
- **Controller:** chỉ nhận request, gọi service, trả response. Không viết logic, không truy vấn database.
- **Service:** chứa toàn bộ logic nghiệp vụ; không viết truy vấn, gọi repository.
- **Repository:** nơi duy nhất tương tác với database; không chứa logic nghiệp vụ.
- **Model:** chỉ định nghĩa mapping bảng (cột, quan hệ, ràng buộc).
- Tầng dưới không import tầng trên; không import vòng.

## Quy ước đặt tên file (theo thư mục)
Tên file phải có hậu tố đúng với thư mục chứa nó:

| Thư mục | Mẫu tên file | Ví dụ |
|---|---|---|
| `controllers/` | `*_controller.py` | `note_controller.py` |
| `services/` | `*_service.py` | `note_service.py` |
| `repositories/` | `*_repository.py` | `note_repository.py` |
| `models/` | `*_model.py` | `note_model.py` |
| `schemas/` | `*_schema.py` | `note_schema.py` |

## Code
- Python 3.11+, type hint cho hàm công khai.
- Tuân thủ **PEP 8**. Format bằng **Black**, kiểm tra lint bằng **flake8**.
  - `pyproject.toml`: `[tool.black]`, `line-length = 79`.
  - `.flake8`: `max-line-length = 79`, `extend-ignore = E203, W503`, loại trừ `alembic/versions`.
- SQLAlchemy 2.x (`select()`, `Mapped`, `mapped_column`), không dùng `session.query()`.
- Pydantic v2; tách schema `Create` / `Update` / `Read`; đặt `max_length` cho `title` và `body`.
- `snake_case` cho hàm/biến/cột, tên bảng số nhiều. Thời gian lưu UTC.
- Dùng `logging`, không `print`.

## Thông báo lỗi bằng tiếng Việt
- **Mọi lỗi trả về cho người dùng đều phải bằng tiếng Việt:** lỗi kiểm tra dữ liệu của Pydantic (422), lỗi nghiệp vụ, xác thực, 404, 500 và mọi lỗi khác trong hệ thống.
- Tuỳ biến handler `RequestValidationError` để trả thông điệp tiếng Việt (ví dụ: "Mật khẩu phải có ít nhất 8 ký tự").
- Gom thông báo lỗi vào một nơi chung trong `app/core/`; không rải chuỗi lỗi khắp code.
- Dùng định dạng lỗi thống nhất, ví dụ `{ "detail": "Không tìm thấy ghi chú" }`.
- Không để lộ thông báo lỗi tiếng Anh mặc định của FastAPI/Pydantic ra ngoài.

## API
- Danh sách `GET /notes` nhận `collection_id`, `q`, `tag`, `limit` (mặc định 10, tối đa 100), `offset` (mặc định 0).
- Response phân trang: `{ items, total, limit, offset }`; sắp xếp `is_pinned DESC, updated_at DESC`.
- Thứ tự xử lý: quyền sở hữu → lọc → đếm `total` → sắp xếp → phân trang.
- `q` dùng `ILIKE` với tham số bind.
- Mã trạng thái: 201 tạo, 204 xoá, 401 chưa xác thực, 404 không tồn tại hoặc không thuộc user, 422 dữ liệu sai.

## Bảo mật
- Mật khẩu băm bằng bcrypt, tối thiểu 8 ký tự; không log mật khẩu.
- JWT có `sub` và `exp` (30–60 phút); secret lấy từ biến môi trường, không hardcode.
- Mọi truy vấn dữ liệu người dùng phải lọc theo `current_user.id`; không tin `user_id` từ request body.
- Truy cập dữ liệu của người khác trả 404 (chống IDOR).
- Lỗi đăng nhập luôn là `Email hoặc mật khẩu không đúng`.
- Không trả `password_hash`; luôn dùng schema `Read`, không trả thẳng ORM model.
- Không nối chuỗi vào SQL.
- `.env` nằm trong `.gitignore`; chỉ commit `.env.example` với giá trị giả.
- CORS lấy từ `CORS_ORIGINS`; không trả stack trace ở production.

## Database
- Mọi thay đổi schema đi qua migration Alembic (có `upgrade` và `downgrade`); không dùng `create_all()`.
- Bắt buộc: `UNIQUE users.email`, `UNIQUE (user_id, name)` trên `tags`, index `notes (collection_id, updated_at DESC)`, PK `note_tags (note_id, tag_id)`.
- Xoá collection thì xoá cascade các note của nó.

## Tài liệu và thư viện
- `README.md`: cài đặt, migrate, chạy, demo, mặc định phân trang, bảo mật, giới hạn đã biết.
- `requirements.txt`: liệt kê đủ thư viện kèm phiên bản, gồm cả Black và flake8.

## Test
- `pytest` + `TestClient`. Mỗi endpoint có test đường chính, dữ liệu sai và quyền.
- Bắt buộc có test user A truy cập dữ liệu user B → 404.
- Test kiểm tra thông báo lỗi trả về là tiếng Việt.
- Chạy `black --check .`, `flake8`, `pytest` và `alembic upgrade head` trước khi coi là xong.

## Nguyên tắc chung
- Đọc code hiện có và theo đúng phong cách trước khi sửa.
- Thay đổi nhỏ, tập trung; không refactor ngoài yêu cầu.
- Thư viện hoặc thứ gì mới: theo quy tắc hỏi người dùng ở đầu file.

# Phân trang (Pagination)

## Tham số truy vấn

| Tham số | Quy tắc | Ví dụ |
|---------|---------|-------|
| `limit` | Mặc định 10 (hoặc 20); tối thiểu 1; tối đa 100 | `limit=10` |
| `offset` | Mặc định 0; tối thiểu 0 | `offset=10` → trang 2 |

## Phản hồi

| Trường | Mô tả | Ví dụ |
|--------|-------|-------|
| `items` | Mảng các resource | Các note của trang này |
| `total` | Số lượng sau khi lọc (nên dùng) | `total=42` |

## Sắp xếp

| Quy tắc | Ý nghĩa |
|---------|---------|
| `is_pinned DESC, updated_at DESC` | Note ghim nổi lên đầu |

## Thứ tự xử lý

```
quyền sở hữu → bộ lọc → đếm → sắp xếp → phân trang
```

> **Lưu ý:** Không bao giờ phân trang rồi mới lọc.