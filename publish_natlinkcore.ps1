#powershell to run the tests, then build the python package.
$ErrorActionPreference = "Stop"
pytest 
flit publish --format sdist