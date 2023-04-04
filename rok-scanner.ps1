echo "Checking powershell host: "
if(($host.Name -match 'consolehost')) {echo "OK ($($host.Name))"} else { echo "Expected ConsoleHost but got $($host.Name). Script might fail to execute. For correct execution use the normal powershell not the ISE."}

python -m venv ./venv
invoke-expression -Command .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\rok-scanner.py