cd ..
export PATH=$PATH:.
export PYTHONPATH=$PYTHONPATH:.
echo "PATH=$PATH"
echo "PYTHONPATH=$PYTHONPATH"

python3 ocgmock/bss_server.py 192.168.92.199 8000
