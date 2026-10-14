@echo off
python -m pip install -r requirements.txt || exit /b 1
python generate_fonts.py || exit /b 1
python -m http.server 8000
