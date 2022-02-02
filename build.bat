@echo off
pip3 install -r requirements.txt
pip3 install pyinstaller
pyinstaller --onefile ast-tracker.py
rmdir /s /q __pycache__
rmdir /s /q build
del /q ast-tracker.spec
