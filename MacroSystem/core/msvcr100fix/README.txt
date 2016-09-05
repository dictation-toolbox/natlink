On some Windows 7 systems, with python 2.6 or python 2.7 installed the configure program does not run correct, probably because the file "msvcr100.dll" cannot be found.

Possibly you can fix this by copying the file in this directory into C:\Windows\System32 (if it is already there, please rename the previous one before copying).

You can then probably run the configure program.

After running the configure program you can remove the msvcr100.dll file again from the System32 directory if you wish and rename the previous version, if it was there.

Please report your experiences to q.hoogenboom@antenna.nl

December 2015