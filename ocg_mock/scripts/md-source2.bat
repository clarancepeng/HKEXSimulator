title UDP Market Data Source2
cd ..
set PATH=%PATH%;F:\ProgramData\Anaconda3;
set PYTHONPATH=%PYTHONPATH%;.

echo "PATH=%PATH%"
echo "PYTHONPATH=%PYTHONPATH%"

python ocgmock/udp_md2.py

pause