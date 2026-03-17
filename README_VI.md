# Streamlit web app cho 3 mô hình dự đoán viêm ruột thừa có biến chứng — phiên bản song ngữ

Gói này đã được cập nhật theo yêu cầu mới:
- chọn giao diện **English / Tiếng Việt**
- bỏ phần ghi chú dành cho developer, thay bằng khu vực **Prediction**
- có **nút Print / In** để in bản tổng hợp thông số và kết quả dự đoán
- cập nhật tác giả song ngữ theo danh sách mới của nhóm nghiên cứu
- chèn logo **Bệnh viện Nhân dân Gia Định** và **Trường Đại học Y khoa Phạm Ngọc Thạch** ở phần đầu trang

---

## PHẦN 1 — Chạy localhost trên Windows, từng bước

### Bước 1. Cài Python
- Cài Python 3.11 hoặc 3.12.
- Khi cài, nhớ tick **Add Python to PATH**.
- Cài xong, đóng cửa sổ PowerShell cũ và mở lại cửa sổ mới.

### Bước 2. Giải nén project
Ví dụ giải nén vào thư mục:

`C:\Users\Long\Downloads\appendicitis_streamlit_app`

### Bước 3. Mở PowerShell đúng thư mục app
Ví dụ:

```powershell
cd C:\Users\Long\Downloads\appendicitis_streamlit_app
```

### Bước 4. Kiểm tra Python
```powershell
py --version
```

Nếu hiện ra `Python 3.x.x` là đạt.

### Bước 5. Chạy file tự động
```powershell
.\run_app_windows.cmd
```

### Bước 6. Chờ app khởi động
Khi thấy dòng kiểu như:

```text
Local URL: http://localhost:8501
```

thì mở trình duyệt tại:

`http://localhost:8501`

### Bước 7. Giữ nguyên cửa sổ PowerShell
Đây là điểm rất quan trọng.

**Không được đóng cửa sổ PowerShell đang chạy Streamlit.**
Nếu đóng, `localhost:8501` sẽ ngừng ngay.

### Bước 8. Dừng app
Quay lại PowerShell và nhấn:

```text
Ctrl + C
```

---

## PHẦN 2 — Nếu muốn gõ tay từng lệnh

```powershell
cd C:\Users\Long\Downloads\appendicitis_streamlit_app
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

---

## PHẦN 3 — Nếu bị lỗi `ERR_CONNECTION_REFUSED`

Lỗi này gần như luôn có nghĩa là:
- app chưa chạy
- hoặc cửa sổ PowerShell đã bị đóng

Cách xử lý:
1. quay lại PowerShell
2. chạy lại:

```powershell
.\run_app_windows.cmd
```

3. chờ khi thấy `Local URL: http://localhost:8501`
4. mở lại trình duyệt

---

## PHẦN 4 — Cách dùng app

1. Chọn ngôn ngữ **English** hoặc **Tiếng Việt**
2. Chọn 1 trong 3 mô hình
3. Nhập các biến cần thiết
4. Bấm **Calculate risk / Tính nguy cơ**
5. Xem khu vực **Prediction**
6. Bấm **Print / In** để tạo bản in tổng hợp các thông số và kết quả dự đoán

---

## PHẦN 5 — Cấu trúc project

- `app.py`: file chính của Streamlit app
- `models_config.py`: chứa 3 mô hình, công thức, hệ số và vcov
- `requirements.txt`: thư viện cần cài
- `run_app_windows.cmd`: file chạy tự động trên Windows
- `HUONG_DAN_WINDOWS_STREAMLIT.txt`: hướng dẫn nhanh bằng text
- `assets/`: logo bệnh viện và trường
- `tests/smoke_test.py`: kiểm tra nhanh logic tính toán

---

## PHẦN 6 — Chạy smoke test

```powershell
.\.venv\Scripts\python.exe tests\smoke_test.py
```

Nếu hiện:

```text
Smoke test passed.
```

thì phần tính toán lõi vẫn chạy đúng.

---

## PHẦN 7 — Phát triển tiếp

Khi cần thêm mô hình mới, anh chỉ cần cập nhật `models_config.py`. Cấu trúc app hiện tại vẫn phù hợp để mở rộng Model 4, Model 5 về sau.


---

## PHẦN 8 — Đưa app lên Streamlit Community Cloud để có link online

Mục tiêu của phần này là tạo một link public dạng `https://ten-app.streamlit.app`.

### Cách làm ngắn gọn
1. Tạo một repository mới trên GitHub.
2. Upload **toàn bộ nội dung** của thư mục app vào repository đó.
3. Đăng nhập Streamlit Community Cloud bằng GitHub.
4. Chọn repository, branch và file chính `app.py`.
5. Deploy.

### Gợi ý tên repository
`appendicitis-risk-calculator`

### Gợi ý tên app URL
`appendicitis-risk-pnt-gdg`

### Python version nên chọn
Chọn **Python 3.12** trong **Advanced settings** khi deploy.

### Sau khi deploy
Mỗi lần anh sửa code rồi cập nhật lại GitHub, Streamlit Community Cloud sẽ build lại app từ repository đó.
