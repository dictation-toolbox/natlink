# There are two kinds of files in this directory as expressed by two targets.
# The first target NatlinkModule expresses natlink and its Python and pyd contents.
# The second target InstallTest just records the files that the installer needs to
# slurp up so that an InstallTest directory can be included on the instalee machine.
# The use of these files is explicated in the inno-setup-natlink.iss: every file there
# must be mentioned here! 

# CMake stupidly does not propagate file dependencies of targets across directories.
# Thus, the targets are actually expressed as stamp files, with a StampDriver 
# ghost target to drive them.  
# See https://samthursfield.wordpress.com/2015/11/21/cmake-dependencies-between-targets-and-files-and-custom-commands/
add_custom_target(StampDriver DEPENDS NatlinkModule.STAMP InstallTest.STAMP)

add_custom_command(OUTPUT NatlinkModule.STAMP
  COMMAND cmake -E touch NatlinkModule.STAMP
  DEPENDS 
  natlink13_pyd natlink15_pyd # binary targets
  __init__.py config.py gramparser.py loader.py 
  redirect_output.py _natlink_core.pyi py.typed)

add_custom_command(OUTPUT InstallTest.STAMP
  COMMAND cmake -E touch InstallTest.STAMP
  DEPENDS
  InstallTest/__init__.py InstallTest/natlink.ini 
  InstallTest/_meet_natlink.py InstallTest/zebra.py)

# NOTE: setup.py is not currently useable