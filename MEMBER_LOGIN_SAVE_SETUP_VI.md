# Thiết lập đăng nhập thành viên và lưu dữ liệu

Bản app này hỗ trợ 2 chế độ:
- **Guest**: ai cũng dùng được, tính nguy cơ và in kết quả như trước, **không lưu dữ liệu**.
- **Member**: người dùng **đăng nhập** thì có thể lưu bộ biến đầu vào và kết quả dự đoán.

## 1. Logic hiện tại của app

- Nếu **chưa cấu hình OIDC** trong `secrets.toml` → app chạy ở **guest mode**.
- Nếu **đã cấu hình OIDC** → người dùng có thể bấm **Đăng nhập thành viên**.
- Nếu có khai báo danh sách `allowed_emails` → chỉ các email đó mới lưu được.
- Nếu không khai báo `allowed_emails` → mọi người dùng đã đăng nhập đều lưu được.

## 2. Cấu hình local để test nhanh

Tạo file:

`.streamlit/secrets.toml`

Ví dụ local test với **Google login + SQLite**:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "REPLACE_WITH_A_LONG_RANDOM_SECRET"
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[members]
allowed_emails = ["Longlk@pnt.edu.vn"]

[connections.app_db]
url = "sqlite:///appendicitis_app_local.db"
```

Sau đó chạy app như bình thường:

```powershell
.\run_app_windows.cmd
```

## 3. Khuyến nghị cho bản public

**Không nên dùng SQLite local cho bản public nếu anh cần lưu dữ liệu bền vững.**

Lý do: Community Cloud **không đảm bảo** local file storage sẽ được giữ lâu dài. Vì vậy:
- Localhost / demo: dùng SQLite được.
- Public / production: nên dùng **remote PostgreSQL**.

Ví dụ secrets cho PostgreSQL:

```toml
[auth]
redirect_uri = "https://appendicitis-complicated-risk-calculator.streamlit.app/oauth2callback"
cookie_secret = "REPLACE_WITH_A_LONG_RANDOM_SECRET"
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[members]
allowed_emails = [
  "Longlk@pnt.edu.vn",
  "another.member@pnt.edu.vn"
]

[connections.app_db]
dialect = "postgresql"
host = "YOUR_REMOTE_HOST"
port = "5432"
database = "YOUR_DATABASE_NAME"
username = "YOUR_DATABASE_USER"
password = "YOUR_DATABASE_PASSWORD"
```

## 4. Các bước cấu hình Google login cho app public

### Bước 1. Tạo OAuth client trong Google Auth Platform
Anh cần lấy:
- `client_id`
- `client_secret`
- `server_metadata_url`
  - với Google là:
  - `https://accounts.google.com/.well-known/openid-configuration`

### Bước 2. Khai báo Authorized redirect URI
Nhập đúng URL sau trong Google:

```text
https://appendicitis-complicated-risk-calculator.streamlit.app/oauth2callback
```

Nếu test local thì thêm:

```text
http://localhost:8501/oauth2callback
```

### Bước 3. Copy secrets lên Streamlit Community Cloud
- vào app dashboard
- chọn **Edit Secrets**
- dán nội dung secrets tương ứng
- save
- reboot app

## 5. Dữ liệu nào sẽ được lưu?

App hiện lưu:
- thời điểm lưu
- email và tên người đăng nhập
- model đang dùng
- language
- version app
- probability, CI, LP
- JSON các biến đã nhập
- JSON kết quả dự đoán

App **không tự thu thêm định danh người bệnh**. Vì vậy, nếu muốn an toàn hơn về bảo mật, đừng nhập tên hoặc mã bệnh án vào app này.

## 6. Nếu muốn siết chặt hơn

Có thể nâng cấp tiếp theo các hướng sau:
- chỉ cho phép email thuộc domain `@pnt.edu.vn`
- tách vai trò `viewer` / `member` / `admin`
- thêm trang xem danh sách bản ghi đã lưu
- export CSV cho admin
