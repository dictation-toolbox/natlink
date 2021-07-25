#copy the the local natlink.pyd built by visual studio to the install directory for natlinkcore.

$natlink_binary=Get-ChildItem NatlinkSource/Debug/natlink.pyd
$natlink_symbols=Get-ChildItem NatlinkSource/Debug/natlink.pdb
$target_dir="src/natlinkcore/PYD"
echo "Natlink binary $natlink_binary copying to $target_dir"



Copy-Item    $natlink_binary -Destination $target_dir/natlink_3.8_Ver15.pyd


echo "copied natlink.pyd to $target_dir"