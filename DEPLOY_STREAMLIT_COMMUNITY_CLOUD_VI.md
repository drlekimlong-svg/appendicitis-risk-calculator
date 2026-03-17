# Hướng dẫn đưa webapp lên Streamlit Community Cloud

## Mục tiêu
Tạo một link online public để mở trực tiếp trên Internet, ví dụ:

`https://appendicitis-risk-pnt-gdg.streamlit.app`

## Phần A — Chuẩn bị
Anh cần có:
- 1 tài khoản GitHub
- 1 tài khoản Streamlit Community Cloud
- thư mục project đã chạy được ở localhost

## Phần B — Tạo GitHub repository
### Cách 1: dễ nhất, dùng giao diện web GitHub
1. Đăng nhập GitHub.
2. Bấm **New repository**.
3. Đặt tên repository, ví dụ: `appendicitis-risk-calculator`.
4. Chọn **Public** nếu anh muốn có link public dễ chia sẻ.
5. Không cần thêm README, .gitignore hay license ở bước tạo repo nếu anh định upload nguyên bộ file ngay.
6. Bấm **Create repository**.

## Phần C — Upload code lên GitHub
1. Mở repository vừa tạo.
2. Bấm **Add file** → **Upload files**.
3. Kéo thả **toàn bộ file và thư mục bên trong** project vào.
4. Quan trọng: phải thấy các file như sau ở đúng cấu trúc:
   - `app.py`
   - `models_config.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `assets/...`
5. Bấm **Commit changes**.

## Phần D — Deploy trên Streamlit Community Cloud
1. Đăng nhập Streamlit Community Cloud bằng GitHub.
2. Chọn **Create app**.
3. Chọn đúng workspace trùng với owner của repository.
4. Chọn:
   - **Repository**: repo anh vừa tạo
   - **Branch**: thường là `main`
   - **Main file path**: `app.py`
5. Ở ô **App URL**, chọn tên link mong muốn.
6. Bấm **Advanced settings**.
7. Chọn **Python 3.12**.
8. Nếu anh upload nguyên thư mục `appendicitis_streamlit_app`, đặt **Main file path** là `appendicitis_streamlit_app/app.py`. Nếu anh upload các file nằm ngay ở root repo, đặt **Main file path** là `app.py`.
9. Bấm **Deploy**.

## Phần E — Sau khi deploy
- Nếu build thành công, Streamlit sẽ tạo link `*.streamlit.app`.
- Anh chỉ cần copy link đó để chia sẻ.
- Mỗi lần anh sửa code và commit lại GitHub, app có thể được cập nhật lại từ repo.

## Phần F — Nếu deploy lỗi
Hai nhóm lỗi hay gặp nhất:
1. thiếu `requirements.txt`
2. đặt sai `Main file path`

Kiểm tra lại:
- `app.py` có nằm đúng trong repository không
- `requirements.txt` có cùng thư mục với `app.py` không
- `assets/` đã được upload đủ chưa

## Phần G — Muốn đổi link app
Trong lúc tạo app, anh có thể nhập một subdomain mới trong ô **App URL**.

## Phần H — Muốn app thật sự public
Cách đơn giản nhất là dùng **public GitHub repository**. Nếu dùng private repository thì app sẽ không tự public cho mọi người.
