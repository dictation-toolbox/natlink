"""module that is loaded when no config file is found elsewhere

It gives the instructions for a correct place to put natlink.ini in
"""
import os
import os.path
join, expanduser, getenv = os.path.join, os.path.expanduser, os.getenv
isfile, isdir = os.path.isfile, os.path.isdir
home = expanduser('~')

thisFile = __file__
this_dir, this_filename = __file__.rsplit('\\', 1)

print()
print()
print(f'This is the file "{this_filename}" from directory "{this_dir}"')
print('This directory holds the default "natlink.ini" file, when it is not found in any of the other possible directories.')
print()
print(r'By default this config file should be stored in "~\.natlink\natlink.ini",')
print(f'\twith "~" being your HOME directory: "{home}"')
print()
print('There are two other ways to configure name and/or location of your "natlink.ini" file:')
print()
print('1. specify the environment variable "NATLINK_INI", pointing to an existing file,')
print()
print('2. define the environment variable "DICTATIONTOOLBOXHOME" to a valid directory.')
print('   This directory should hold a subdirectory ".natlink" and a config file "natlink.ini".')

natlink_ini = getenv("NATLINK_INI")
dictationtoolboxhome = getenv("DICTATIONTOOLBOXHOME")

if natlink_ini:
    if isfile(natlink_ini):
        print(f'You specified "NATLINK_INI" to "{natlink_ini}", so the Natlink should not appear here.')
        print('Please try/retry to copy the sample "natlink.ini" file into this path.')
    else:
        print(f'You specified "NATLINK_INI" to "{natlink_ini}", but this is not a valid path')
        print('Please copy the sample "natlink.ini" file into this path,\n\tor change/remove the environment variable "NATLINK_INI".')
        
elif dictationtoolboxhome:
    print('You have set your "DICTATIONTOOLBOXHOME" to:')
    if not os.path.isdir(dictationtoolboxhome):
        print(f'Please create this directory "{dictationtoolboxhome}"\n\tand a subdirectory ".natlink"\n\tand then copy your sample "natlink.ini" file into this subdirectory')
    else:
        subdirectory = join(dictationtoolboxhome, '.natlink')
        if not os.path.isdir(subdirectory):
            print(f'Please create a subdirectory ".natlink" in {dictationtoolboxhome}\n\tand then copy your sample "natlink.ini" file into this subdirectory')
        else:
            inifile = join(subdirectory, 'natlink.ini')
            if not os.path.isfile(inifile):
                print(f'Please copy your sample "natlink.ini" file into "{subdirectory}"')
    print()
    print('When you do not want to user environment variable "DICTATIONTOOLBOXHOME", remove it from your system')
    print()
else:
    print()
    print('You did not set "NATLINK_INI" or "DICTATIONTOOLBOXHOME" on your windows system')
    print(f'The config file "natlink.ini" should now be in "{home}\\.natlink\\natlink.ini"')
    print()
    print(f'So... please copy the file "{this_dir}\\natlink.ini" into this location.')
    print('====DO NOT FORGET the ".natlink" subdirectory!')

print()
print('Then proceed with manual configuration or with')
print('configuration or with via natlinkconfig program (to be fixed yet).')
print('When manually configuring "natlink.ini", comment out the line starting with "default_config"')

 
print()
print()

print('After all these steps, restart Dragon and good luck...\n\n\n')

