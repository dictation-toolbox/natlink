
rem "This file will hopefully fix a failing install of the pywin32, the"
rem "Windows extensions for python2.7, on Windows 10."
rem 
rem "Please ensure your python installation is in the directory below"
rem "If not, edit this file."
rem "Then Run as administrator, by right-clicking on the filename"

pause
C:\python27\python.exe C:\python27\scripts\pywin32_postinstall.py -install
pause