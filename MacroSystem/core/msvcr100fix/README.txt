1. On some Windows 7 systems, with python 2.6 or python 2.7 installed the configure program does not run correct, probably because the file "msvcr100.dll" cannot be found.

2. Also it can happen that the configure program runs correct, but after enabling NatLink, the GUID error shows up.

3. I believe this fix is quite old, and should not be tried on Windows 10 any more. Please inform me if you have better information.
(Quintijn, January 2019)
-----------------------------------------------------

When you disable NatLink, Dragon starts as usual.

Solution (on Windows 7, 32 bits computer with Natspeak 10):
-goto the natlink core directory (eg C:\NatLink\NatLink\MacroSystem\core) and then
-goto the subdirectory msvcr100fix.
-copy the dll file msvcr100.dll into the core directory or into the C:\Windows\System32 directory. For the latter choice you need to confirm the action.

-Restart Dragon. Hopefully it works.

The problem can also possibly be solved by installing 

https://www.microsoft.com/en-us/download/details.aspx?id=26999

Please report your experiences to q.hoogenboom@antenna.nl

December 2016

