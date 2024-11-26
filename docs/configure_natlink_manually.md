# Editing natlink.ini

You can always manually inspect and adapt your `natlink.ini` file.

## Location of natlink.ini

The config file `natlink.ini` will by default be in `%UserProfile%\.natlink` In your user profile.

- Optionally set environmental variable `NATLINK_SETTINGSDIR` to set the location of natlink files like natlink.ini. For example`%UserProfile%\Documents\.natlink`.

When you run the config program `natlinkconfig_gui` in the from windows start menu, the next step is automatically performed:

- Generating a default config

```ini
  [directories]
  # for most users, this section is all you need
  my_scripts=C:\Users\user\dragonfly-scripts
  system_wide_scripts=C:\Path\To\Shared\Scripts

  [userenglish-directories]
  only_loaded_if_profile_userenglish_active=C:\User\user\english-only-scripts

  [userspanish-directories]
  only_loaded_if_profile_userspanish_active=C:\User\user\spanish-only-scripts

  [settings]
  log_level=INFO
```

## Add Python packages

As an end user of Natlink, you may be never need to write your own
grammar, and you won't need programming skills. You will need to Python
packages and grammars and perhaps do some small amount of configuration
on your computer.

Grammars are implemented as Python modules. A Python module is a single
Python file which is identified with the `.py` extension. Natlink
needs to know to load these Python modules. This is done through the configuration file natlink.ini.

natlink.ini has a `[directories]` setting that lists the directories
(file folders) natlink loads grammars from. You can add as many as you
need.

Python packages can be specified by their name instead of full path to where the module was installed (tyically with pip). pip can put packages in varying places difficult for end-users to local. typically in `c:/program files/.../site-packages` or 

```ini
  [directories]
  # for most users, this section is all you need
  my_scripts=C:\Users\user\dragonfly-scripts
  system_wide_scripts=C:\Path\To\Shared\Scripts

  [userenglish-directories]
  only_loaded_if_profile_userenglish_active=C:\User\user\english-only-scripts

  [userspanish-directories]
  only_loaded_if_profile_userspanish_active=C:\User\user\spanish-only-scripts

  [settings]
  log_level=INFO~/AppData/.../site-packages.`
```

- For example

`unimacro=unimacro`

- instead of

`unimacro=C:\Users\Doug\AppData\Roaming\Python\Python310\site-packages\unimacro`

See  **Installing a Published Grammar** for more details

## Setting User Directories

Same as `directories`, but scripts are only loaded if the active user profile is .
This section may be repeated any number of times for different users.
This is useful e.g. if you have multiple user profiles for different languages.
The relative load order between global and user directories is the order of appearance in the config.

Special directory directives:

- `~` points to your home directory, most often
  ``C:\Users\UsersName` or %UserProfile%. This is one directory above your Documents directory. The config program translates chosen paths to this better readable` ~` when possible.
- `natlink_userdir`: this `variable` points to the directory where
  your config file, `natlink.ini`, is located. By default this is
  the directory `.natlink` in your home directory. But your can set
  the environment variable `NATLINK_SETTINGSDIR`, see above.
  - Note: the path should always end with the directory `.natlink`! For some `automatic defined` directories, especially for`unimacro`, this `natlink_userdir` is also used. The directory MUST be a local
    directory.

Other directories, `user directories`, can be set on a network drive
(Dropbox, OneDrive), if you prefer. When you enable `Dragonfly` `cola` `Unimacro`(or any of them), the config program will
also install and if possible update the required package. When you want
to force an upgrade of a package, first disable the package and then
enable again.

**NatlinkUser**

- The package independent Natlink user directory can also be
  
  ```
  specified as a directory where you can put your python grammar
  files.
  ```

**Dragonfly**

- The user directory is where you can put your python grammar files.
  
  ```
  The Natlink user directory was defined for this. You could
  keep using this directory too, but install/upgrade of Dragonfly is
  not maintained in that case.
  ```

**Vocola**

- By specifying a directory where your user command files will be
  
  ```
  located (.vcl), you enable Vocola.
  ```

**Unimacro**

- By specifying a directory where your user config files (.ini) will
  
  ```
  be located, you enable Unimacro. Note Unimacro is not ready for a
  release yet.
  ```

# Installing a Published Grammar

Follow the instructions for the specific grammar or extension. If the
author has published the package xyz to PyPI [https://pypi.org/](https://pypi.org/) you
will be able to install it with a command line 'pip install xyz' in a
command shell or powershell prompt and add the necessary lines to
natlink.ini (something like xyz=xyz).

They might provide other instructions on installing the package with
pip, or just provide a python file for you to figure out what to deal
with. In the case where they just provide you python files, the python
files module must be placed in a folder listed in the directories
section of natlink.ini.

As an end user of Natlink, you may be never need to write your own
grammar, and you won't need programming skills. You will need to Python
packages and grammars and perhaps do some small amount of configuration
on your computer.

Grammars are implemented as Python modules. A Python module is a single
Python file which is identified with the `.py` extension. Natlink
needs to know to load these Python modules. This is done through the configuration file natlink.ini.

natlink.ini has a `[directories]` setting that lists the directories
(file folders) natlink loads grammars from. You can add as many as you
need.

The directory can be: - the name of Python package you have installed.
Generally this is the easiest if someone has published a grammar as a
Python package. - a folder on your file system where you have placed the
Python file OR where an extension will place Python files.

In any case, Natlink will load all the python code in all the
directories listed in the natlink.ini config file.

It can be confusing becuase you might see two directories with similar
names. For example, Vocola uses two directories in natlink.ini.
Natlink.ini will have two lines for Vocola:

`[directories]`

`vocoladirectory = vocola2 vocolagrammarsdirectory =
natlink_userdirvocolagrammars`

This is because vocola has a bunch of Python that needs to be loaded
from the vocola2 Python package and a bunch more Python that vocola
itself creates at runtime and places in vocolagrammarsdirectory. Some
other natlink extensions do the same thing.

## Nakink Settings

The currently supported settings are:

- log_level: the log level to set the Natlink logger to. 
  Possible values are: `CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET`.
- `load_on_begin_utterance` (default: False): check for and load or reload any new or changed scripts at the beginning of each utterance.
- `load_on_mic_on` (default: True): check for and load or reload any new or changed scripts when the microphone state changes to "on".
- `load_on_startup` (default: True): check for and load scripts as soon as Dragon loads Natlink.
- `load_on_user_changed` (default: True): check for and load scripts when the user profile changes.
