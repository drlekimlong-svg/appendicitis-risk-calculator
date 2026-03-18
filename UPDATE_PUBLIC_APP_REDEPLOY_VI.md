# Cập nhật app public đang chạy trên Streamlit Community Cloud

Anh không cần tạo app mới từ đầu.
Chỉ cần cập nhật lại repository GitHub đang dùng để deploy.

## Cách nhanh nhất
1. Mở repository GitHub đang chứa app public hiện tại.
2. Thay toàn bộ file cũ bằng bộ file mới trong gói này.
3. Kiểm tra lại bắt buộc phải có đủ:
   - `app.py`
   - `models_config.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `assets/logo_gia_dinh.png`
   - `assets/logo_pnt.png`
4. Commit changes lên branch đang dùng để deploy, thường là `main`.
5. Quay lại Streamlit Community Cloud.
6. App sẽ tự rebuild lại. Nếu chưa thấy, bấm **Reboot app** hoặc **Redeploy**.

## Nếu anh upload bằng giao diện web GitHub
1. Mở repo.
2. Bấm **Add file** → **Upload files**.
3. Kéo thả toàn bộ file mới vào đúng cấu trúc thư mục.
4. Bấm **Commit changes**.

## Sau khi cập nhật xong
Khi mở link public, bản mới sẽ có:
- mặc định giao diện Tiếng Việt
- nút đổi ngôn ngữ ở góc phải phía trên
- 2 logo ở đầu trang
- version hiển thị trên giao diện
- email liên hệ `Longlk@pnt.edu.vn`
- phần gợi ý cách dùng mô hình

## Nếu logo vẫn không hiện
Nguyên nhân gần như luôn là thiếu thư mục `assets/` hoặc upload sai vị trí file logo.
Hãy kiểm tra lại:
- `assets/logo_gia_dinh.png`
- `assets/logo_pnt.png`
