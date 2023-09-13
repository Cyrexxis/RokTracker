echo "Checking powershell host: "
if(($host.Name -match 'consolehost')) {echo "OK ($($host.Name))"} else { echo "Expected ConsoleHost but got $($host.Name). Script might fail to execute. For correct execution use the normal powershell not the ISE."}

python .\check_python.py
if($LastExitCode -eq 1){
    Exit
}

python -m venv ./venv
invoke-expression -Command .\venv\Scripts\activate
pip install tqdm==4.66.1

python .\install_scanner.py
if($LastExitCode -eq 1){
    Exit
}

Write-Host -NoNewLine 'Press any key to continue after build tools are installed...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');

pip install -r requirements.txt
pip install .\deps\tesserocr-2.6.0-cp311-cp311-win_amd64.whl