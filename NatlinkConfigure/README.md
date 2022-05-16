The natlinkconfigfunctions.py is now a very much simplified compared with the python2 version.

This is because the natlink installer program handles the enabling of Natlink itself. Elevated mode is
no longer needed.

The GUI program is NOT running yet, please ignore configurenatlink.pyw for the time being

============
so... below is not active now:

With the GUI (configurenatlink.pyw) you can configure NatLink, Vocola and Unimacro, but also DragonFly, via the UserDirectory.

This program is written in wxPython.  

The definitions are made with the (nonfree) program: wxDesigner (see http://www.roebling.de)

The definition file for wxDesigner is called configurenatlink.wdr, these definitions that were 
translated by wxDesigner into configurenatlink_wdr.py, and it is this file that is used by configurenatlink.pyw.

It is unwise to edit these 2 files by hand, as they will be regenerated if a new wxDesigner run is done.

The program configurenatlink.pyw uses uses functions from the module: natlinkconfigfunctions.py.

If the GUI program doesn't work for some reason, you can fall back to
the command line interface, which is contained in
natlinkconfigfunctions.py.  Just start this program from the start
menu or the folder that you are in now, preferably in elevated mode too with start_natlinkconfigfunctions.py

=======================================
Quintijn Hoogenboom, February 18, 2008, (...)April 2022 (python3)



