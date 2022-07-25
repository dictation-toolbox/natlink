"""
code to help with debugging including:
- enable python debuggers to attach.
currently on DAP debuggers are supported.
https://microsoft.github.io/debug-adapter-protocol/
There are several, Microsoft Visual Studio COde is known to work.
There are several, Microsoft Visual Studio COde is known to work.

If you know how to add support for another debugger please add it.

Written by Doug Ransom, 2021
"""
#pylint:disable=C0116, W0703
import os
import debugpy
from natlinkcore import natlinkstatus

__status = natlinkstatus.NatlinkStatus()
__natLinkPythonDebugPortEnviornmentVar= "NatlinkPyDebugPort"
__natLinkPythonDebugOnStartupVar="NatlinkPyDebugStartup"

__pyDefaultPythonExecutor = "python.exe"
__debug_started=False
default_debugpy_port=7474
__debugpy_debug_port=default_debugpy_port
__debugger="not configured"
dap="DAP"

#bring a couple functions from DAP and export from our namespace
dap_is_client_connected=debugpy.is_client_connected
dap_breakpoint = debugpy.breakpoint

def dap_info():
    return f"""
Debugger: {__debugger}  DAP Port:{__debugpy_debug_port} IsClientConnected: {dap_is_client_connected()} Default DAP Port {default_debugpy_port} 
Debug Started:{__debug_started}
"""

def start_dap():
    #pylint:disable=W0603
    global  __debug_started,__debugpy_debug_port,__debugger
    if __debug_started:
        print(f"DAP already started with debugpy for port {__debugpy_debug_port}")
        return
    try:

        if __natLinkPythonDebugPortEnviornmentVar in os.environ:
            natLinkPythonPortStringVal = os.environ[__natLinkPythonDebugPortEnviornmentVar]
            __debugpy_debug_port = int(natLinkPythonPortStringVal)
        print(f"Starting debugpy on port {natLinkPythonPortStringVal}")

        python_exec =  __pyDefaultPythonExecutor  #for now, only the python in system path can be used for natlink and this module
        print(f"Python Executable (required for debugging): '{python_exec}'")
        debugpy.configure(python=f"{python_exec}")
        debugpy.listen(__debugpy_debug_port)
        print(f"debugpy listening on port {__debugpy_debug_port}")
        __debug_started = True
        __debugger = dap

        if __natLinkPythonDebugOnStartupVar in os.environ:
            dos_str=os.environ[__natLinkPythonDebugOnStartupVar]
            dos=len(dos_str)==1 and dos_str in "YyTt"

            if dos:
                print(f"Waiting for DAP debugger to attach now as {__natLinkPythonDebugOnStartupVar} is set to {dos_str}")
                debugpy.wait_for_client()


    except Exception as ee:
        print(f"""
    Exception {ee} while starting debug.  Possible cause is incorrect python executable specified {python_exec}
"""     )

def debug_check_on_startup():
    #pylint:disable=W0603
    global  __debug_started,__debugpy_debug_port,__debugger
    debug_instructions = f"{__status.getCoreDirectory()}\\debugging python instructions.docx"
    print(f"Instructions for attaching a python debugger are in {debug_instructions} ")
    if __natLinkPythonDebugPortEnviornmentVar in os.environ:
        start_dap()






