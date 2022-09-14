
$dest_folder = "C:\Program Files (x86)\Natlink\site-packages\natlink\"
$dest_pyd = "_natlink_core.pyd"
$dest_pdb = "_natlink_core.pdb"
$dest_pyd_file = $dest_folder+$dest_pyd
$dest_pdb_file = $dest_folder+$dest_pdb

$msg = "updates __init__.py and _natlinkcore.pyd  from _natlinkcore15.pyd to " + $dest_folder  + `
"\nMust be run from a powershell with administrative privileges.   " ` +
"\nIf you installed natlink to a folder other than C:\Program Files (x86)\Natlink\ copy this to another name and tweak $dest_folder, just don't check it in" + `
"\nto git."

echo $msg
Copy-Item  -Destination $dest_folder build\NatlinkSource\Debug\_natlink_core15.pyd
Copy-Item  -Destination $dest_folder build\NatlinkSource\Debug\_natlink_core15.pdb
Copy-Item  -Destination $dest_folder build\NatlinkSource\Debug\_natlink_core13.pyd
Copy-Item  -Destination $dest_folder build\NatlinkSource\Debug\_natlink_core13.pdb


Copy-Item  -Destination $dest_folder src\natlink\__init__.py 
Copy-Item  -Destination $dest_folder src\natlink\_natlink_core.pyi