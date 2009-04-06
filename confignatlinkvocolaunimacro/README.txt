This GUI ready for use.

With this GUI you can configure NatLink.  It is written in wxPython.  

The definitions are made with the (nonfree) wxDesigner program. (http://www.roebling.de)

The definition file for wxDesigner is called configurenatlink.wdr.

But the definitions that are read by wxPython are in:
configurenatlink_wdr.py

It is unwise to edit these 2 files by hand, as they will be regenerated if a new wxDesigner run is done.

The program itself is in: configurenatlink.py

It uses functions from the module: natlinkconfigfunctions.py.

If the GUI program doesn't work for some reason, you can fall back to
the command line interface, which is contained in
natlinkconfigfunctions.py.  Just start this program from the start
menu or the folder that you are in now.


Quintijn Hoogenboom, February 18, ???, reviewed April 6, 2009
