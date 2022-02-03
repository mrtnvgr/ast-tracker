#!/bin/bash

read -p "First launch?(y/n): " ch
if [[ $ch == y ]] 
then
	winecfg -v win10
	wget https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks
	winetricks dotnet40
	wget https://www.python.org/ftp/python/3.10.1/python-3.10.1.exe
	wine python-3.10.1.exe
	wine cmd /c pip install pyinstaller
	wine cmd /c pip install -r requirements.txt
	wineserver -k
	rm python-3.10.1.exe && rm winetricks
fi
echo "Building for GNU/Linux..."
pip3 install -r requirements.txt
pip3 install pyinstaller
pyinstaller --onefile ast-tracker.py
rm -rf build
rm -rf __pycache__
rm -f ast-tracker.spec
echo "Building for windows under wine..."
wine pyinstaller --onefile ast-tracker.py
wineserver -k
rm -rf build
rm -rf __pycache__
rm -f ast-tracker.spec
