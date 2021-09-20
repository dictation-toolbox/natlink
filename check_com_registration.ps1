echo "checking the registration of the natlink COM objects"
Get-ChildItem -Path "Registry::HKEY_CLASSES_ROOT\WOW6432Node\CLSID\{dd990001-bb89-11d2-b031-0060088dc929}" -Recurse
echo "checking the Python Core, make sure you are using the same version of Python as natlink "
Get-ChildItem -path "Registry::HKEY_LOCAL_MACHINE\Software\Python\PythonCore" -Recurse

