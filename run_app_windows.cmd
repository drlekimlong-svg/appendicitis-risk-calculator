@echo off
setlocal

echo ================================================
echo Complicated Appendicitis Risk Calculator - Start
echo ================================================
echo.
echo Luu y:
echo - Hay giai nen file ZIP truoc.
echo - Mo CMD/PowerShell trong dung thu muc chua file app.py.
echo - Khi app da chay, GIU nguyen cua so nay. Neu dong cua so nay, localhost se dung.
echo.

if not exist app.py (
  echo [ERROR] Khong tim thay app.py.
  echo Hay giai nen file ZIP va mo CMD/PowerShell ngay trong thu muc chua app.py.
  pause
  exit /b 1
)

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Khong tim thay Python Launcher ^(py^).
  echo Hay cai Python truoc, sau do mo lai CMD/PowerShell.
  pause
  exit /b 1
)

echo [1/4] Kiem tra Python...
py -3 --version
if errorlevel 1 (
  echo [ERROR] Python 3 chua san sang.
  pause
  exit /b 1
)

echo.
echo [2/4] Tao virtual environment .venv ...
if not exist .venv (
  py -3 -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Khong tao duoc .venv
    pause
    exit /b 1
  )
) else (
  echo .venv da ton tai, bo qua buoc tao moi.
)

echo.
echo [3/4] Cai dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] Loi khi nang cap pip.
  pause
  exit /b 1
)

if exist requirements.txt (
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 (
    echo [ERROR] Loi khi cai requirements.txt
    pause
    exit /b 1
  )
) else (
  echo [WARNING] Khong thay requirements.txt, se cai rieng streamlit.
  .venv\Scripts\python.exe -m pip install streamlit
  if errorlevel 1 (
    echo [ERROR] Loi khi cai Streamlit.
    pause
    exit /b 1
  )
)

echo.
echo [4/4] Chay Streamlit app...
echo Neu trinh duyet khong tu mo, vao dia chi: http://localhost:8501
echo Nhan Ctrl + C trong cua so nay de dung app.
.venv\Scripts\python.exe -m streamlit run app.py

endlocal
