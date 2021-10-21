# There are two kinds of files in this directory as expressed by two targets.
# The first target NatlinkModule expresses natlink and its Python and pyd contents.
# The second target InstallTest just records the files that the installer needs to
# slurp up so that an InstallTest directory can be included on the instalee machine.
# The use of these files is explicated in the inno-setup-natlink.iss: every file there
# must be mentioned here!
add_custom_target(NatlinkModule ALL DEPENDS 
  __init__.py config.py gramparser.py
  loader.py redirect_output.py _natlink_core.pyi py.typed)
add_dependencies(NatlinkModule natlink13_pyd natlink15_pyd)

add_custom_target(InstallTest ALL DEPENDS
  InstallTest/__init_.py InstallTest/natlink.ini InstallTest/_meet_natlink.py
  InstallTest/zebra.py)

# NOTE: setup.py is not currently useable