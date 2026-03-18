# Thiết lập Google login + PostgreSQL cho app public hiện tại

App public hiện tại:
`https://appendicitis-complicated-risk-calculator.streamlit.app/`

Redirect URI phải dùng:
`https://appendicitis-complicated-risk-calculator.streamlit.app/oauth2callback`

## 1) Cập nhật code vào GitHub repo đang deploy
Thay các file/thư mục sau trong repo GitHub hiện tại:
- `app.py`
- `models_config.py`
- `requirements.txt`
- `assets/`
- `tests/`
- `.streamlit/config.toml`

Bản này đã thêm:
- đăng nhập Google bằng `st.login()`
- phân quyền lưu theo whitelist email
- trường `Research ID` / `ID nghiên cứu` gồm đúng 8 chữ số khi lưu
- tự tạo bảng `saved_predictions` nếu tài khoản database có quyền

## 2) Tạo Google login
### 2.1 Google Auth Platform
- Tạo hoặc chọn project.
- Vào **Google Auth Platform**.

### 2.2 Branding
Điền tối thiểu:
- **App name**: `Complicated Appendicitis Risk Calculator`
- **Support email**: chọn email Google quản trị mà giao diện cho phép chọn
- **Developer contact information**: email quản trị của anh

Nếu giao diện hiện ô **Authorized domain** và bắt buộc phải điền, Streamlit tutorial hiện dùng `example.com` cho trường hợp phát triển local và/hoặc deploy trên Streamlit Community Cloud.

### 2.3 Audience
Để dễ kiểm soát giai đoạn đầu, giữ app ở trạng thái **Testing** và thêm đúng 9 email test user:
- `longlk@pnt.edu.vn`
- `dr.lekimlong@gmail.com`
- `dr.thaikhanhphat@gmail.com`
- `trinhan.pham99@gmail.com`
- `quangtran12c1@gmail.com`
- `phucuong98.dn@gmail.com`
- `stellarduong@gmail.com`
- `mytrantrinh42@gmail.com`
- `tg_lenguyenkhoi@pnt.edu.vn`

### 2.4 Client
- Vào **Clients** → **Create client**
- **Application type**: `Web application`
- **Name**: `appendicitis-risk-calculator-web`
- **Authorized JavaScript origins**: để trống
- **Authorized redirect URIs**: thêm 2 dòng sau

```text
https://appendicitis-complicated-risk-calculator.streamlit.app/oauth2callback
http://localhost:8501/oauth2callback
```

Sau khi tạo, copy lại:
- **Client ID**
- **Client secret**

## 3) Tạo cookie secret
Trên máy anh, chạy một trong hai lệnh sau:

### Windows PowerShell
```powershell
py -c "import secrets; print(secrets.token_urlsafe(32))"
```

### macOS / Linux / terminal Python
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy chuỗi vừa tạo.

## 4) Dán secrets vào Streamlit Community Cloud
Vào app settings của app đang deploy → **Secrets**.

Copy toàn bộ nội dung file `SECRETS_EXAMPLE.toml`, rồi thay 6 chỗ sau:
- `PASTE_RANDOM_COOKIE_SECRET_HERE`
- `PASTE_GOOGLE_CLIENT_ID_HERE`
- `PASTE_GOOGLE_CLIENT_SECRET_HERE`
- `PASTE_POSTGRES_HOST_HERE`
- `PASTE_POSTGRES_DATABASE_HERE`
- `PASTE_POSTGRES_USERNAME_HERE`
- `PASTE_POSTGRES_PASSWORD_HERE`

Nếu port PostgreSQL không phải `5432`, sửa lại `port`.

## 5) Nếu muốn tạo bảng thủ công trong PostgreSQL
Chạy file `postgres_create_table_saved_predictions.sql` trong PostgreSQL.

Nếu user database có quyền tạo bảng, app cũng sẽ tự tạo bảng khi khởi động.

## 6) Redeploy / Reboot
Sau khi cập nhật code trên GitHub và lưu secrets:
- quay lại Streamlit Community Cloud
- bấm **Reboot app** hoặc **Redeploy**

## 7) Cách test nhanh
1. Mở app public.
2. Không đăng nhập: app vẫn chạy ở chế độ guest, không lưu được.
3. Bấm **Đăng nhập thành viên / Member login**.
4. Đăng nhập bằng 1 trong 9 email đã khai báo.
5. Nhập dữ liệu mô hình và bấm tính nguy cơ.
6. Ở phần lưu dữ liệu, nhập **ID nghiên cứu 8 chữ số**. Ví dụ: `24000001`.
7. Bấm lưu.

## 8) Nếu gặp lỗi thường gặp
### `redirect_uri_mismatch`
Nghĩa là redirect URI trong Google client không khớp tuyệt đối với URI app đang gửi. Kiểm tra lại đúng chuỗi sau trong Google client:

```text
https://appendicitis-complicated-risk-calculator.streamlit.app/oauth2callback
```

### Đăng nhập được nhưng không lưu được
Kiểm tra lần lượt:
- email có nằm trong `[members].allowed_emails` không
- đã cấu hình `[connections.app_db]` chưa
- database user có quyền kết nối và tạo bảng / ghi dữ liệu chưa
- đã tính nguy cơ trước khi bấm lưu chưa
- `Research ID` có đúng 8 chữ số không

### Chỉ muốn 9 email trên đăng nhập được trong giai đoạn đầu
Cứ để Google app ở trạng thái **Testing** và thêm đúng 9 email đó ở phần **Audience → Test users**.
