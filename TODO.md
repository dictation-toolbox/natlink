# TODO

## Useage

- Accomodate normal people: `.natlink` -> `natlink.ini`
- Place natlink.ini in `/users/XXX/Documents` 
  - because `/users/XXX` not easily found - no shortcut provided standard by Windows 10
  - `Documents` folder is often backed up, but not its parent
- Download and launch Python installer if Python not found? 
  - The installer can be executed with correct options by a shell command.
- Let installer install a template natlink ini file?
  - with suggestions for running Vocola, Unimacro, Caster, etc. -- all commented out
- Offer choices for further install, where the installer executes a script with py -m pip install XXX commands. 
  - best accommodate by each project using natlink defining its own version of the installer
  - that's done easily using git submodules
- setup.py does not work
   - need to modify `Nuance ` and `Natlink` registry entries in `C:\Program Files (x68)\...
- `File→Reload` (Natlink window) needs attention

## Technical

- Build pyd for Dragon for 12-16, make installer choose correct dll and move
- ~~Use link to python3X.pyd, calculated at install time, instead of including it with installer~~
- Use .pth file to direct our COM server instead of or supplementing registry keys?
- Correct dependencies on python source files in CMAKE

## Technicalities

- No default natlink ini file is actually defined (where get_natlink_system_config_filename looks)
- Remove setup.py from installation
- Build warnings
  - unsafe string functions