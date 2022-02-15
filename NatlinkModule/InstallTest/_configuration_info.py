"""example file for loading natlink from the default (fallback) location

It gives configuration information

When in trouble, rename this file to "_configuration_info.py" and rerun Dragon.
Otherwise, this file will not be loaded from this location.
"""
#pylint:disable=W0212
import sys
import sysconfig
from pprint import pprint

print()
print()
print("I'm _configuration_info.py and I'm being loaded, too, on my own.")
print()
print("This is your windows version from sys.getwindowsversion():")
print("---------------------------------------------------")
print(f'{sys.getwindowsversion()}')
print(f'and the "build" number: {sys.getwindowsversion()}')
print()
print("This is your Python configuration as per sysconfig:")
print("---------------------------------------------------")
sysconfig._main()
print("This is your Python system path sys.path:")
print("-----------------------------------------")
pprint(sys.path)
print("End of _configuration_info.py info.")
print("-----------------------------")
