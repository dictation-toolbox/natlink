"""module that is loaded when no config file is found elsewhere

It gives the instructions for a correct place to put natlink.ini in
"""
import os
import os.path
from natlinkcore import getThisDir

join, expanduser, getenv = os.path.join, os.path.expanduser, os.getenv
isfile, isdir = os.path.isfile, os.path.isdir
home = expanduser('~')

thisFile = __file__
_this_dir, this_filename = __file__.rsplit('\\', 1)
thisDir = getThisDir(__file__)
if _this_dir != thisDir:
    print(f'Working with symlinks! Point to the sitepackages directory: "{_this_dir}", but edit in "{thisDir}"')
this_dir = thisDir

print(f'\n\n'
    f'\nThis is the file "{this_filename}" from directory "{this_dir}"'
    f'\nThis directory holds the default "natlink.ini" file, when it is not found the default or configured directory.'
    f'\n\n'
    rf'The default directory is: "~\.natlink", with "~" being your HOME directory: "{home}".'
    f'\tSo: "{home}\\.natlink"'
    f"\n"
    f'\nThere is also a custom way to configure the directory of your "natlink.ini" file:'
    f'\n'
    f'\nSpecify the environment variable "NATLINK_USERDIR", which should point to an existing directory.'
    f'\nNote: this directory may NOT be a shared directory, like Dropbox or OneDrive.'
    f'\nseveral directories to be configured may be shared however, but others must be local, which is hopefully '
    f'\nensured well enough in the config program.'
    f'\n'
    f'\nWhen this directory does not hold the file "natlink.ini",\nyou can copy it from "{this_dir}",'
    f'\nor (easier) run the configure program of Natlink, see below.'
    f'\n'
    f'\tWhen you run this program, the default version of "natlink.ini" will be copied into'
    f'\tthe correct place, and you can proceed with configuring'
    f'\tthe additional options in order to get started with using Natlink.'
    f'\n' )

















if False:
    print()
    print()
    print(f'This is the file "{this_filename}" from directory "{this_dir}"')
    print('This directory holds the default "natlink.ini" file, when it is not found the default or configured directory.')
    print()
    print(rf'The default directory is: "~\.natlink", with "~" being your HOME directory: "{home}".')
    print(f'\tSo: "{home}\\.natlink"')
    print()
    print('There is also a custom way to configure the directory of your "natlink.ini" file:')
    print()
    print('Specify the environment variable "NATLINK_USERDIR", which should point to an existing directory.')
    print('Note: this directory may NOT be a shared directory, like Dropbox or OneDrive.')
    print('several directories to be configured may be shared however, but others must be local, which is hopefully ')
    print('ensured well enough in the config program.')
    print()
    print(f'When this directory does not hold the file "natlink.ini",\nyou can copy it from "{this_dir}",')
    print('or (easier) run the configure program of Natlink, see below.')
    print()
    print('\tWhen you run this program, the default version of "natlink.ini" will be copied into')
    print('\tthe correct place, and you can proceed with configuring')
    print('\tthe additional options in order to get started with using Natlink.')
    print()


natlink_userdir = getenv("NATLINK_USERDIR")

if natlink_userdir:
    if isdir(natlink_userdir):
        print(f'You specified "NATLINK_USERDIR" to "{natlink_userdir}".')
        print('So Natlink should not startup with these messages. ')
        print('Probably you do not have a proper "natlink.ini" file into this path.')
        print('Please run the configure program of Natlink:')
    else:
        print(f'You specified "NATLINK_USERDIR" to "{natlink_userdir}", but this is not a valid directory path')
else:
    print()
    print('You did not set "NATLINK_USERDIR" on your windows system')
    print(f'The config file "natlink.ini" should now be in "{home}\\.natlink\\natlink.ini"')
    print()
    print(f'So... please copy the file "{this_dir}\\natlink.ini" into this location, or (BETTER)')
    print(r'run the configure program of Natlink:')

print()
print('Please try to run the config program (Command Line Interface) by running ***"natlinkconfig"***')
print('\tfrom the Windows command prompt.')
print()

print('After all these steps, (re)start Dragon and good luck...\n\n\n')

