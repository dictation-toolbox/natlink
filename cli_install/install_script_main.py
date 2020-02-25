import argparse
import traceback
from cli_install.install_script_functions import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Installation and configuration of Natlink and its dependency (python-32bit)")
    parser.add_argument("--python_version", type=str, default="3.7", help='Python "3.7"(default), "3.8" are supported. If you already have Python 3.7 or 3.8  installed in the default location this step will be skipped.')
    args = parser.parse_args()
    try:
        pass

        create_tmp_folder()
        download_and_install_python(args.python_version)
        clone_natlink()
        # delete_tmp_folder()
    except Exception as e:
        track = traceback.format_exc()
        print(track)
        print("Something went wrong")
        input("Press something to exit")
        exit(0)
    input("Press something to continue")



