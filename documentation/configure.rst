Configure Natlink
=================

Location of 'natlink.ini'
-------------------------

The config file `natlink.ini` will by default be in `~\\.natlink`, so a subdirectory of your home directory, typically `C:\\Users\\Name`.

When you run the config program `natlinkconfig_gui.py`, the next step is automatically performed:

- copy the file `natlink.ini` from the 'fallback' location  into your home directory, subdirectory `.natlink`. So copy "C:\\Program Files (x86)\\Natlink\\DefaultConfig\\natlink.ini" to "C:\\Users\\Name\\.natlink\\natlink.ini".

- When you want another directory for your file `natlink.ini` to be in, you can set this in the environment variable 'NATLINK_USERDIR'. For example, when you want your config files (especially `natlink.ini`) in a subdirectory of your Documents folder, set this environment variable to '~/Documents/.natlink'.

Adding directories to the configuration
---------------------------------------

This will be done with the config program (`natlinkconfig_gui.py`), or with the Command Line Interface `natlinkconfig_cli.py`. Both programs can be started from the Windows Command Line.

Note: the Command Line Interface can also be used in batch mode.

Special directory directives:

- "~" points to your 'home' directory, most often 'C:\\Users\\Name'. This is one directory above your 'Documents' directory. The config program translates chosen paths to this better readable '~', when possible.
- "natlink_userdir": this "variable" points to the directory where your config file, 'natlink.ini', is located. By default this is the directory '.natlink' in your home directory. But your can set the environment variable NATLINK_USERDIR, see above. Note: the path should always end with the directory '.natlink'! For some "automatic defined" directories, especially for `unimacro` and `vocola`, this 'natlink_userdir' is also used. The directory MUST be a local directory.

User Directories
-----------------

Other directories, "user directories", can be set on a network drive (Dropbox, OneDrive), if you prefer. When you enable 'Dragonfly', 'Vocola' or 'Unimacro' (or any of them), the config program will also install and if possible update the required package. When you want to force an upgrade of a package, first disable the package and then enable again.

:Dragonfly:
    The user directory is where you can put your python grammar files. Previous, the Natlink user directory was defined for this. You could keep using this directory too, but install/upgrade of Dragonfly is not maintained in that case.
    
:Vocola:
    By specifying a directory where your user command files will be located (.vcl), you enable Vocola.
    
:Unimacro:
    By specifying a directory where your user config files (.ini) will be located, you enable Unimacro. Note Unimacro is not ready for a release yet.
    
:NatlinkUser:
    The "package independent" Natlink user directory can also be specified as a directory where you can put your python grammar files.
    
    

Set the log_level
-------------------

You can set the log_level, controlling the abundance of information messages in the "Messages from Natlink" window with the following option (choices are DEBUG, INFO, WARNING).

::

    [settings]
    log_level = INFO


Manual editing natlink.ini
------------------------------

You can always manually inspect and adapt your 'natlink.ini' file.

Restart Dragon
--------------

After making changes in your configuration, always restart Dragon! Keep your eye on the 'Messages from Natlink' window!