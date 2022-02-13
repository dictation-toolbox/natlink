"""example file for loading natlink from the default (fallback) location

It gives config information
"""
#pylint:disable=W0212
import sys
import sysconfig
from pprint import pprint

print()
print()
print("I'm _config_info.py and I'm being loaded, too, on my own.")
print()
print("This is your Python configuration as per sysconfig:")
print("---------------------------------------------------")
sysconfig._main()
print("This is your Python system path sys.path:")
print("-----------------------------------------")
pprint(sys.path)
print("End of _config_info.py info.")
print("-----------------------------")
