#register the natlink.pyd build by visual studio locally

$natlink_binary=Get-ChildItem NatlinkSource/Debug/*.pyd
cp $natlink_binary  C:\Python38-32\Lib\site-packages\natlinkcore\
echo copied natlink.dll to site packages\natlinkcore\