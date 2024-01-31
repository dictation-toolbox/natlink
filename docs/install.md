# Install Natlink

## Preinstall requirements

- DPI 16, 15,14, 13 or derivative of the same version
- Make sure any previous versions of Natlink are unregistered and uninstalled. (Dragon must be close during that process)

## Install

1. Download the latest [Natlink](https://github.com/dictation-toolbox/natlink/releases)
   
   - Python 3.10.X 32 bit is required. (if you don't have Python 3.10 installed Natlink Installer will install it off path for you automatically)
   - Do not uncheck the default `Py Launcher`

2. Run the Natlink Installer and a GUI should pop up at the end.
   
   - Note: After install natlink can be reconfigured Using `Configure Natlink via CLI` Natlink start menu.
   - **Optionally** install other Python packages via commandline with Natlink's python interpreter utilizing `Natlink Python Environment` 

3. Configure the Natlink GUI
   
   ![natlink_gui](/images/natlink_gui.png)
   
   - **Optionally** Check the relevant project Dragonfly or Unimacro to configure the file path to the grammars.

4. Start Dragon start Dragon, the `Messages from Natlink` window should show loading a dragonfly script.  In the picture blow is an example loading module`_caster` is `_caster.py`.

   ![natlink_running](/images/natlink_running.png)

Scrips starting with an underscore and ending in .py `_*.py` will be imported in alphabetical order, except `__init__.py` will be loaded first if it exists. 

The Natlink setup program creates a shortcut `Natlink Python Environment` which will open a terminal session with the correct Python in the path for the end-user to install dependencies.