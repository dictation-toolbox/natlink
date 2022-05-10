Configure Natlink
=================

Location of 'natlink.ini'
-------------------------

The config file `natlink.ini` will by default be in `~\\.natlink`, so a subdirectory of your home directory, typically `C:\\Users\\Name`.

When running the `natlinkconfigfunctions.py` (soon to be released), next step is automatically performed:

- copy the file `natlink.ini` from the 'fallback' location  into your home directory, subdirectory `.natlink`. So copy "C:\\Program Files (x86)\\Natlink\\DefaultConfig\\natlink.ini" to "C:\\Users\\Name\\.natlink\\natlink.ini".

- When you want another directory for your file `natlink.ini` to be in, you can set this in the environment variable 'NATLINK_USERDIR'.

Adding directories to the configuration
---------------------------------------

This will be done with the config program, (`configurenatlink.pyw`, not in the release yet) and `natlinkconfigfunctions.py` (not in the release yet)

For manually adding directories, see examples below, but beware of the paths. As these examples show, you can use a shared (eg Dropbox, OneDrive) folder for directories.  The different `'User'` directories are subdirectories of '`C:\\Users\\Name\\Dropbox\\NatlinkUser`'.

Note: the file `natlink.ini` should not be in a shared folder.

- Add Dragonfly:

::

   [directories]
   dragonflyuserdirectory = C:\Users\Name\Dropbox\NatlinkUser\DragonflyUser

- Add UserDirectory (Dragonfly users can choose between 'Add Dragonfly' or this option):

::

   [directories]
   userdirectory = C:\Users\Name\Dropbox\NatlinkUser\UserDir

- Add vocola:

::

   [directories]
   vocoladirectory = C:\Python38-32\lib\site-packages\vocola2
   vocolagrammarsdirectory = C:\Users\Name\Dropbox\NatlinkUser\VocolaUserDir\VocolaGrammars

- Add Unimacro:

::

   [directories]
   unimacrodirectory = C:\Python38-32\lib\site-packages\unimacro
   unimacrogrammarsdirectory = C:\Users\Name\Dropbox\NatlinkUser\UnimacroUser\ActiveGrammars


Set the log_level
-------------------

You can set the log_level, controlling the abundance of information messages in the "Messages from Natlink" window with the following option (choices are DEBUG, INFO, WARNING).

::

    [settings]
    log_level = INFO

More will follow here...
