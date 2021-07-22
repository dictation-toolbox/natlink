#copy the the local natlink.pyd built by visual studio to the install directory for natlinkcore.

$natlink_binary=Get-ChildItem NatlinkSource/Debug/natlink.pyd
$natlink_symbols=Get-ChildItem NatlinkSource/Debug/natlink.pdb
echo "Natlink binary $natlink_binary"

$site_packages=$(pye_purelib)

Copy-Item    $natlink_binary -Destination $site_packages\natlinkcore\
Copy-Item    $natlink_symbols -Destination $site_packages\natlinkcore\


echo "copied natlink.dll and natlink.pyd to $site_packages\natlinkcore"