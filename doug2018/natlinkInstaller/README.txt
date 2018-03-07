Release 4.1uniform-6:

- small change in DNSInstallDir, some users have the natspeak.exe not in Program but in App/Program
- Many things done, for making the new natlink.pyd for Dragon 15 work.
- Most things now seem to work.
- Getting the unittestNatlink better working and analysed.
- Lots of things for getting the (mainly future) conversion to all Unicode work.
Natlink:
- natlinkutils.py: trying a new detail in the activate/deactivate procedure of rules: at new activateAll or activateSet call, first the current active rules are deactivated. Previous this was done more subtle, but apparently sometimes this mechanism sucks. Maybe better with this trick!

---------------------------------------------
-important fix in natlink.pyd for DPI15
-natlinkmain adapted to this new pyd (callBack user gives now 4 parameters, including the user language)
-natlinkmain call functions in natlinkcorefunctions for collecting paths of Natlinks own directories. Will be documented soon.
-Installer program several fixes, especially for Dragon installed in non standard locations

Unimacro:
- quite a few grammars changed, see website Unimacro 

