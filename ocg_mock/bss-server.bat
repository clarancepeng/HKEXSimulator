title Bss Server
cd .
set PATH=%PATH%;C:\ProgramData\Anaconda3
set PYTHONPATH=%PYTHONPATH%;.

echo "PATH=%PATH%"
echo "PYTHONPATH=%PYTHONPATH%"

python ocgmock/bss_server.py 192.168.60.64 8000

pause