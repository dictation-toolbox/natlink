import argparse, sys, traceback

from cli_install.Configuration import Configuration
from cli_install.install_script_functions import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Installation and configuration of Natlink and its dependency")
    parser.add_argument("--python_version", type=str, default="3.7", help='Python "3.7"(default), "3.8" are supported. If you already have 32 bit versions of Python 3.7 or 3.8  installed in the default location this step will be skipped.')
    parser.add_argument("--status",action='store_true',help="Print the current configuration")
    args = parser.parse_args()
    print(args.status)

    inst = Installation_Routines(Configuration(""))

    if args.status:
        print("status")
        input("Press something to exit")
        sys.exit(0)

    try:
        print(args.python_version)

        inst.create_tmp_folder()
        inst.download_and_install_python(args.python_version)
        inst.clone_natlink()
        #delete_tmp_folder()
    except Exception as e:
        track = traceback.format_exc()
        print(track)
        print("Something went wrong")
        input("Press something to exit")
        exit(0)
    input("Press something to continue")



