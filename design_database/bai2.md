# danh sách các quan hệ 
Giữa sach (tác phẩm) và tac_gia: Quan hệ Nhiều - Nhiều (N:N) 
Giữa sach (tác phẩm) và ban_sao_vat_ly: Quan hệ Một - Nhiều (1:N) 
Giữa doc_gia và phieu_muon: Quan hệ Một - Nhiều (1:N) 
Giữa phieu_muon và ban_sao_vat_ly: Quan hệ Nhiều - Nhiều (N:N) 
# các bảng trung gian 
Do tồn tại các quan hệ Nhiều - Nhiều (N:N), hệ thống cần 2 bảng trung gian:

sach_tac_gia: Giải quyết quan hệ N:N giữa sach và tac_gia.

chi_tiet_phieu_muon: Giải quyết quan hệ N:N giữa phieu_muon và ban_sao_vat_ly 
# lược đồ erd 
1. Bảng doc_gia (Độc giả)
doc_gia_id: INT (PK, NOT NULL)

ho_ten: VARCHAR (NOT NULL)

email: VARCHAR (UNIQUE, NOT NULL)

so_dien_thoai: VARCHAR

2. Bảng sach (Đầu sách / Tác phẩm)
sach_id: INT (PK, NOT NULL)

tieu_de: VARCHAR (NOT NULL)

nam_xuat_ban: INT

3. Bảng tac_gia (Tác giả)
tac_gia_id: INT (PK, NOT NULL)

ten_tac_gia: VARCHAR (NOT NULL)

4. Bảng trung gian sach_tac_gia (Liên kết Sách - Tác giả)
sach_id: INT (PK / FK tham chiếu tới sach(sach_id), NOT NULL)

tac_gia_id: INT (PK / FK tham chiếu tới tac_gia(tac_gia_id), NOT NULL)

5. Bảng ban_sao_vat_ly (Bản sao sách thực tế)
ban_sao_id: INT (PK, NOT NULL)

sach_id: INT (FK tham chiếu tới sach(sach_id), NOT NULL)

trang_thai: VARCHAR (NOT NULL - ví dụ: sẵn sàng, đang mượn, bảo trì)

6. Bảng phieu_muon (Phiếu mượn)
phieu_muon_id: INT (PK, NOT NULL)

ngay_muon: DATE (NOT NULL)

ngay_hen_tra: DATE (NOT NULL)

doc_gia_id: INT (FK tham chiếu tới doc_gia(doc_gia_id), NOT NULL)

7. Bảng trung gian chi_tiet_phieu_muon (Chi tiết phiếu mượn)
phieu_muon_id: INT (PK / FK tham chiếu tới phieu_muon(phieu_muon_id), NOT NULL)

ban_sao_id: INT (PK / FK tham chiếu tới ban_sao_vat_ly(ban_sao_id), NOT NULL)

tinh_trang_khi_muon: VARCHAR

tinh_trang_khi_tra: VARCHAR