#register the natlink.pyd build by visual studio locally

$natlink_binary=Get-ChildItem NatlinkSource/Debug/*.pyd
echo "unregistring natlink"
natlinkconfig_cli -R
echo registering natlink binary "$natlink_binary"
natlinkconfig_cli --dev_natlink=$natlnk_binary -r