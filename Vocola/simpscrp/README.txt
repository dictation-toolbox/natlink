[building simpscrp for a given Python by Rick]


First off, the only purpose of simpscrp is so Vocola can launch a
command-line exe without flashing a black window, and wait for it to
finish. With all the python stuff now integrated there's probably a
better way.

As I recall, the procedure is:

1) open the project in visual studio

2) Make sure you're using the "Release" build settings

3) in the project properties, update the python reference in the include
   path and in the link path to point to the right folders for the new
   python, and update the .dll target to write to a new folder, e.g. 2.6

4) rename the resulting .dll to .pyd


It doesn't take long, but does require having python installed.



I haven't been following python too closely, but I think I read that 2.6
was the end of the line for the 2's, and python 3 will no longer require
modules to recompiled for major releases.
