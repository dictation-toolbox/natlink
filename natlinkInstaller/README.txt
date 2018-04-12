Release 4.1uniform-7:

-some disturbing errors in the config program have been corrected, thanks to feedback from Doug Ransom and Tim Harper.
Natlinkutils.py:
- important change: the state of the activeRules is maintained in a dict, in which the value of each rule is the window handle it is activated in. Analogous to the activate_rule function that is used in Vocola.
- all the activating/deactivating is not running correct, we hope to tackle this problem soon.

4.1uniform-6:
- small change in DNSInstallDir, some users have the natspeak.exe not in Program but in App/Program
- Many things done, for making the new natlink.pyd for Dragon 15 work.
- Most things now seem to work.
- Getting the unittestNatlink better working and analysed.
- Lots of things for getting the (mainly future) conversion to all Unicode work.

---------------------------------------------
-important fix in natlink.pyd for DPI15
-natlinkmain adapted to this new pyd (callBack user gives now 4 parameters, including the user language)
-natlinkmain call functions in natlinkcorefunctions for collecting paths of Natlinks own directories. Will be documented soon.
-Installer program several fixes, especially for Dragon installed in non standard locations

Unimacro:
- quite a few grammars changed, see website Unimacro 

