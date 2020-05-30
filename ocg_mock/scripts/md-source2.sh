cd ..
export PATH=$PATH:.
export PYTHONPATH=$PYTHONPATH:.

echo "PATH=$PATH"
echo "PYTHONPATH=$PYTHONPATH"

python3 ocgmock/udp_md2.py
