@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Khong tim thay Python trong venv. Xem HUONG_DAN_CHAY.md de cai dat.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" -c "import socket, sys; probe = socket.socket(); probe.settimeout(1); result = probe.connect_ex(('127.0.0.1', 7860)); probe.close(); sys.exit(0 if result == 0 else 1)"
if "%errorlevel%"=="0" (
    echo Cong 7860 dang duoc su dung.
    echo Neu Kokoro da chay, mo http://127.0.0.1:7860 de su dung.
    echo Muon khoi dong lai, dung phien cu truoc roi mo file nay.
    pause
    exit /b 0
)

set "GRADIO_ANALYTICS_ENABLED=False"
set "HF_HUB_DISABLE_TELEMETRY=1"
set "PYTHONIOENCODING=utf-8"
set "KOKORO_OUTPUT_DIR=%~dp0audio"
set "KOKORO_VI_MODEL_DIR=%~dp0models\vietnamese"

echo Kokoro TTS - http://127.0.0.1:7860
echo Audio: %KOKORO_OUTPUT_DIR%
echo Tieng Viet: chon giong vi_diem_trinh hoac vi_... trong giao dien.
echo Giu cua so nay mo khi su dung. Nhan Ctrl+C de dung.
echo Neu cong 7860 dang duoc su dung, dung phien cu truoc khi chay lai.
echo.
"venv\Scripts\python.exe" -u -m kokoro_tts_local.gradio_interface --host 127.0.0.1 --port 7860
set "tts_exit_code=%errorlevel%"
if not "%tts_exit_code%"=="0" (
    echo.
    echo Ung dung da dung voi loi. Giu lai thong bao ben tren de chan doan.
    pause
)
exit /b %tts_exit_code%
