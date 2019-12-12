@echo off
call "D:\Anaconda3\Scripts\activate.bat"
python -m PyQt5.uic.pyuic ui.ui -o ui.py
python -m PyQt5.uic.pyuic dialog.ui -o dialog.py
python -m PyQt5.uic.pyuic dialog2.ui -o dialog2.py
pause