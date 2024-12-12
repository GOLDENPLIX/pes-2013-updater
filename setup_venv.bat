@echo off
REM Create virtual environment
python -m venv pes_update_venv

REM Activate virtual environment
call pes_update_venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

REM Run tests
python -m unittest tests/test_modules.py

REM Deactivate virtual environment
deactivate

echo Virtual environment setup complete!
