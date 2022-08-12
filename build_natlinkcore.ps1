#powershell to run the tests, then build the python package.
$ErrorActionPreference = "Stop"
pytest --capture=tee-sys 
flit build --format sdist