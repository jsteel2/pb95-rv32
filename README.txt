main.py generates the PBASIC code for the RV32 emulator
pbasic.py is a PBASIC->lua compiler for testing, because progressbar95's interpreter is slow
run the emulator in lua like this: python3 main.py | python3 pbasic.py | lua
to run the emulator in progressbar95, copy it to %APPDATA%\Roaming\Spooky House Studios UG (haftungsbeschraenkt)\Progressbar95\Documents\pbasic1.txt
and load it with PBLOAD 1
