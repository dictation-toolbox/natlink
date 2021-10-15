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

## Technical

- Build pyd for Dragon 15 and for 12-14, make installer choose correct dll and move
- Use link to python3X.pyd, calculated at install time, instead of including it with installer
- Use .pth file to direct our COM server instead of or supplementing registry keys

## Technicalities

- No default natlink ini file is actually defined (where get_natlink_system_config_filename looks)
