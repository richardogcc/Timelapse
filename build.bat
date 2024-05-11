@echo off
pyinstaller --onefile --windowed --icon=main.ico -n Timelapse timelapse.py
xcopy /y main.ico dist\

