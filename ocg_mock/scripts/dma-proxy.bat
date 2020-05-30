title DMA Proxy
cd ..
set PATH=%PATH%;F:\ProgramData\Anaconda3;F:\ProgramData\Anaconda3\Library\mingw-w64\bin;F:\ProgramData\Anaconda3\Library\usr\bin;F:\ProgramData\Anaconda3\Library\bin;F:\ProgramData\Anaconda3\Scripts;C:\ProgramData\Anaconda3\bin;F:\ProgramData\Anaconda3\condabin;
set PYTHONPATH=%PYTHONPATH%;.

echo "PATH=%PATH%"
echo "PYTHONPATH=%PYTHONPATH%"

python ocgmock/dma_proxy.py

pause