# Quy chuẩn dự án FastAPI

## Ngôn ngữ và cách làm việc
- Luôn trả lời, giải thích và viết tài liệu bằng tiếng Việt.
- Trả lời ngắn gọn, đi thẳng vào vấn đề.
- Với thay đổi ảnh hưởng nhiều hơn 2 file, thay đổi database schema, hoặc thêm thư viện: trình bày kế hoạch ngắn và chờ tôi xác nhận.
- Với sửa nhỏ, fix bug rõ ràng hoặc thay đổi 1 file: làm trực tiếp, sau đó tóm tắt file đã sửa và lý do.
- Nếu thiếu thông tin quan trọng, hỏi lại. Nếu phải giả định, nêu rõ giả định.
- có thể sửa ngoài phạm vi yêu cầu nhưng bắt buộc phải hỏi lại ý kiến người dùng
- có thể thêm thư viện mới đẻ phù hợp với code sinh ra nhưng phải hỏi lại ý kiến của người dùng
- Không xoá hoặc viết lại code hiện có nếu không cần thiết.

## Kiến trúc
- `app/routers/`: chỉ nhận request, gọi service và trả response. Không chứa business logic hoặc SQL.
- `app/services/`: chứa business logic.
- `app/repositories/`: chỉ chứa truy vấn và thao tác dữ liệu SQLAlchemy.
- `app/models/`: chứa SQLAlchemy ORM models.
- `app/schemas/`: chứa Pydantic schema cho request và response.
- `app/core/`: chứa cấu hình, dependency và exception handler.

## FastAPI
- Dùng Pydantic schema cho mọi request và response.
- Dùng `response_model`, `tags`, `summary` và `description` cho endpoint.
- Dùng dependency injection cho DB session: `db: Session = Depends(get_db)`.
- Dùng async endpoint cho các thao tác I/O.
- Dùng đúng HTTP status: 200, 201, 204, 400, 401, 403, 404, 409, 422, 500.
- Xử lý lỗi nghiệp vụ bằng global exception handler; không lộ stack trace.

## Database
- Model SQLAlchemy đặt trong `app/models/`.
- Truy vấn database đặt trong `app/repositories/`.
- Không viết SQL hoặc gọi database trực tiếp trong router.
- Khi thay đổi model, tạo Alembic migration.
- Không commit secret hoặc connection string thật.

## Chất lượng code
- Dùng type hints cho hàm, method và endpoint.
- Tuân thủ PEP 8 và cấu hình `.flake8`.
- Ưu tiên thay đổi tối thiểu, giữ đúng style code hiện có.

## Kiểm thử
- Mọi tính năng mới phải có pytest test trong `tests/`.
- Dùng FastAPI `TestClient`.
- Test ít nhất: happy path, lỗi validation và lỗi nghiệp vụ chính.
- Sau khi sửa code, chạy `pytest` và báo kết quả.

## Quy tắc cuối cùng
- Phải tuấn thủ các nguyên tắc đã nêu trước đó
- nếu vấn đề không nằm trong các nguyên tắc trước đó bạn có thể sáng tạo thoải mái nhưng bắt buộc phải hỏi ý kiến người dùng
