import sys
import sysconfig
from pprint import pprint
print("I'm _meet_natlink.py and I'm being loaded, too, on my own.")
print("This is your Python configuration as per sysconfig:")
print("---------------------------------------------------")
sysconfig._main()
print("This is your Python system path sys.path:")
print("-----------------------------------------")
pprint(sys.path)
print("End of _meet_natlink.py info.")
print("-----------------------------")
