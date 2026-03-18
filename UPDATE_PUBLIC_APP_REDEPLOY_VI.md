# Cập nhật app public đang chạy

Để cập nhật bản public trên Streamlit Community Cloud, anh chỉ cần thay bộ file trong GitHub repo đang deploy rồi commit/push lại.

## Những file/thư mục cần có trong repo

- `app.py`
- `models_config.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `assets/logo_gia_dinh.png`
- `assets/logo_pnt.png`
- `SECRETS_EXAMPLE.toml`
- `MEMBER_LOGIN_SAVE_SETUP_VI.md`

## Nếu muốn bật login + save trên app public

Ngoài việc update code, anh còn phải vào **Edit Secrets** của app trên Streamlit Community Cloud và khai báo:

- `[auth]` để bật OIDC login
- `[members]` nếu muốn giới hạn email nào được lưu
- `[connections.app_db]` để cấu hình nơi lưu dữ liệu

## Lưu ý rất quan trọng

SQLite local chỉ phù hợp để test local hoặc demo ngắn. Nếu bản public cần giữ dữ liệu ổn định thì dùng **remote PostgreSQL**.

## Thao tác ngắn gọn

1. Giải nén bộ code mới.
2. Ghi đè file cũ trong repo GitHub.
3. Commit và push lên branch đang deploy.
4. Vào Streamlit Community Cloud, nếu app chưa tự build lại thì bấm **Reboot app** hoặc **Redeploy**.
