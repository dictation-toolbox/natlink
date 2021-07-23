
import sys
import sysconfig

def python_info():
    """ return information about the python version and environment as  a string."""
# print out python information
    python_sys_props = ["prefix", "base_prefix", "executable",
                        "implementation", "path", "platform", "version_info"]

    config_info=list(sysconfig.get_paths().items())
    sy_info =  list((p, sys.__dict__[p])  for p in python_sys_props)
    py_info=config_info+sy_info
    py_info_strs="\n".join(list(map(str,py_info)))
    return py_info_strs

def print_python_info():
        return print(f"Python Information:\n{python_info()}")

print_python_info()

