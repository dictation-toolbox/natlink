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
print(r'By default this config directory should be: "~\.natlink", with "~" being your HOME directory: "{home}"')
print()
print('There is also a custom way to configure the directory your "natlink.ini" file then should be:')
print()
print('Specify the environment variable "NATLINK_USERDIR", which should point to an existing directory.')
print()
print('When this directory does not hold the file "natlink.ini", you can copy it from "{this_dir}",')
print('or run the configure program of Natlink ("configurenatlink.pyw" or "natlinkconfigfunctions.py").')
print('The default version of "natlink.ini" will be copied into the correct place, and you can proceed with ')
print('configuring the additional options in order to get started with using Natlink.')

natlink_userdir = getenv("NATLINK_USERDIR")

if natlink_userdir:
    if isdir(natlink_userdir):
        print(f'You specified "NATLINK_USERDIR" to "{natlink_userdir}".')
        print('So the Natlink should startup with these messages. ')
        print('Probably you do not have a proper "natlink.ini" file into this path.')
        print('Please run the configure program of Natlink ("configurenatlink.pyw" or "natlinkconfigfunctions.py")')
    else:
        print(f'You specified "NATLINK_USERDIR" to "{natlink_userdir}", but this is not a valid directory path')
else:
    print()
    print('You did not set "NATLINK_USERDIR" on your windows system')
    print(f'The config file "natlink.ini" should now be in "{home}\\.natlink\\natlink.ini"')
    print()
    print(f'So... please copy the file "{this_dir}\\natlink.ini" into this location, or (better)')
    print('Please run the configure program of Natlink ("configurenatlink.pyw" or "natlinkconfigfunctions.py")')

print()

print('After all these steps, (re)start Dragon and good luck...\n\n\n')

