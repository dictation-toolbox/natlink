"""module that is loaded when no config file is found elsewhere

It gives the instructions for a correct place to put natlink.ini in
"""
import os
import os.path
join, expanduser, getenv = os.path.join, os.path.expanduser, os.getenv
home = expanduser('~')

thisFile = __file__
this_dir, this_filename = __file__.rsplit('\\', 1)

print()
print()
print(f' This is the __init__.py from directory {this_dir}')
print('This directory holds the default "natlink.ini" file, when it is not')
print('found in any of the other possible directories.')
print()

print(r'By default this config file is stored in ~\.natlink\natlink.ini')
print(f'with "~" your HOME directory: {home}')

print(r'Alternatively you can store your config file in  "~\Documents\.natlink\natlink.ini"')

print('You can also choose to set the environment variable "DICTATIONTOOLBOXHOME" to ')
print('a self chosen directory. Environment variables can be used in the ')
print('definition of "DICTATIONTOOLBOXHOME".')

dictationtoolboxhome = getenv("DICTATIONTOOLBOXHOME")
if dictationtoolboxhome:
    print()
    print(f'You have set your "DICTATIONTOOLBOXHOME" to:')
    print(f'\t{dictationtoolboxhome}, so please ensure you ')
    print(f'\tcreate a subdirectory ".natlink",')
    print(f'\tand copy "{this_dir}\\natlink.ini" into {dictationtoolboxhome}\\.natlink\\natlink.ini')
else:
    print('You did not set "DICTATIONTOOLBOXHOME"')
    
print('When you have chosen your location for your "natlink.ini" file, ')
print('please copy the file "{this_dir}\\natlink.ini" into this location')
print('and proceed with manual configuration or via natlinkconfig program (to be fixed yet)')
 
print()
print()

print('After all these steps, restart Dragon...')

