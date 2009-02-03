This GUI is now about ready for use.

With this GUI you can configure NatLink.  It is written in wxPython.  

The definitions are made with the (nonfree) wxDesigner program.  The
definition file for wxDesigner is called configurenatlink.wdr.

But the definitions that are read by wxPython are in:
configurenatlink_wdr.py

The program itself is in: configurenatlink.py

It uses functions from the module: natlinkconfigfunctions.py.

If the GUI program doesn't work for some reason, you can fall back to
the command line interface, which is contained in
natlinkconfigfunctions.py.  Just start this program from the start
menu or the folder that you are in now.

Quintijn Hoogenboom, February 18, took out in date
