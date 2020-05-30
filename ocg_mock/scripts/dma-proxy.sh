cd ..
export PATH=$PATH:.
export PYTHONPATH=$PYTHONPATH:.

echo "PATH=$PATH"
echo "PYTHONPATH=$PYTHONPATH"

python3 ocgmock/dma_proxy.py
