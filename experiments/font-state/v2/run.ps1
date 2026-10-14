$ErrorActionPreference = 'Stop'
python -m pip install -r requirements.txt
python generate_fonts.py
python -m http.server 8000
