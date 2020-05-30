title UDP Market Data Source3
cd ..
set PATH=%PATH%;F:\ProgramData\Anaconda3;
set PYTHONPATH=%PYTHONPATH%;.

echo "PATH=%PATH%"
echo "PYTHONPATH=%PYTHONPATH%"

python ocgmock/udp_md3.py

pause