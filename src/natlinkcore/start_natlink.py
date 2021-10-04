"""this module should be called from the natlink.pyd module

it imports natlinkmain, and runs natlinkmain.start_natlink()

Finetuning can be done in this module, without having to change anything in the C++ code

For example when going in test mode for Natlink itself, the start_natlink() call can be commented.
Quintijn, March, 2021
"""
from natlinkcore import natlinkmain
natlinkmain.start_natlink()
