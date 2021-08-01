#build an sdist (source distribution) package for natlink
#no wheel is built, one less thing to worry about
#use the no-setup option, which requires a 
flit build --format sdist  --no-setup-py