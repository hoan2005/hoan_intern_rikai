# Chuyến đi & Thanh toán (Giao dịch tài chính)
Loại CSDL: SQL

Công nghệ ví dụ: PostgreSQL

Vì sao: Đòi hỏi tính nhất quán tuyệt đối (ACID) và khả năng xử lý giao dịch phức tạp (Transactions) để đảm bảo tiền bạc và trạng thái chuyến đi không bao giờ bị sai lệch hay thất thoát.

# Điểm GPS của tài xế (Real-time tracking & Tải ghi lớn)
Loại CSDL: NoSQL

Công nghệ ví dụ: Cassandra (hoặc Redis cho real-time caching)

Vì sao: Phục vụ lượng ghi khổng lồ từ hàng vạn thiết bị liên tục mỗi 3 giây; kiến trúc NoSQL phân tán cho phép scale-out theo chiều ngang và tối ưu tốc độ ghi cực tốt mà không bị nghẽn cổ chai do khóa bảng (table lock).

# Hồ sơ người dùng + Lịch sử chuyến đi
Loại CSDL: NoSQL

Công nghệ ví dụ: MongoDB

Vì sao: Dữ liệu có cấu trúc dạng document (JSON) linh hoạt, cho phép tra cứu cực nhanh theo user_id chỉ trong một truy vấn duy nhất mà không cần thực hiện các thao tác JOIN nhiều bảng phức tạp.