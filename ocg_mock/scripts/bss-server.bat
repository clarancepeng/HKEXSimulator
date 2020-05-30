title Bss Server
cd ..
set PATH=%PATH%;F:\ProgramData\Anaconda3
set PYTHONPATH=%PYTHONPATH%;.

echo "PATH=%PATH%"
echo "PYTHONPATH=%PYTHONPATH%"

python ocgmock/bss_server.py 192.168.101.11 8000

pause