import re
import subprocess
import wget
from zipfile import ZipFile

from cli_install.install_script_helpers import *


class AbortInstallation(Exception):
    pass


class configurations:
    TMP_FOLDER = os.getenv('APPDATA') + '\\natlink\\'
    NATLINK_INSTALL_DIR = "c:/natlink"
    SUPPORTED_PYTHON_VERSION = ["3.7", "3.8"]

    SUPPORTED_PYTHON_LINKS = {"3.7": "https://www.python.org/ftp/python/3.7.6/python-3.7.6.exe",
                              "3.8": "https://www.python.org/ftp/python/3.8.1/python-3.8.1.exe"}

    def __init__(self):
        pass


def download_and_install_python(python_version):
    """
    First this function checks if a compatible python version is already installed on the system.
    Is no compatible version is found it downloads and installs the projects default python version.
    :param python_version:
    """

    def install_python(version):
        if not query_yes_no(f"Would you like to install Python {version} 32bit"):
            print(
                "You cannot use Natlink without a compatible Python version. Please reconsider and start the script again.")
            raise AbortInstallation

        print(f"Downloading Python version {version}")
        wget.download(configurations.SUPPORTED_PYTHON_LINKS[version], configurations.TMP_FOLDER + "python.exe")
        print("\n")
        # https://docs.python.org/3/using/windows.html
        subprocess.Popen([f"{configurations.TMP_FOLDER}python.exe" ,"/passive","PrependPath=1"], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT).communicate()
        # run_command(configurations.TMP_FOLDER + "python.exe /passive =1")

    # Checking for pre-existing python installations before invoking the actual installation function
    print("Looking for pre-existing python installations:")
    try:
        raw_python_versions_str, error = subprocess.Popen("py -0p", stdout=subprocess.PIPE,
                                                          stderr=subprocess.STDOUT).communicate()

    except:
        print("\tNo python installation was found on the system.")
        install_python(python_version)
        return

    else:
        # expected output: "Some silly text before the relevant information -3.7-32 c:path 3.8-64 c:path ..."
        raw_python_versions_str = raw_python_versions_str.decode(sys.stdout.encoding)
        splits = raw_python_versions_str.split()
        pattern = re.compile("-(\d.\d)-(32|64)")
        first_match = -1
        found_compatible_python_version = False

        for index, entry in enumerate(splits):
            match = pattern.match(entry)
            if match != None:  # relevant information starts here
                first_match = index

            if first_match > 0 and (index - first_match) % 2 == 0:
                if match.group(1) in configurations.SUPPORTED_PYTHON_VERSION and match.group(2) == "32":
                    found_compatible_python_version = True
                    print(f"\t[Compatible] Python {match.group(1)} {match.group(2)} bit {splits[index + 1]}")
                else:
                    print(f"\t[Not-Compatible] Python {match.group(1)} {match.group(2)} bit {splits[index + 1]}")

        if not found_compatible_python_version:
            install_python(python_version)
        else:
            print("\nUsing compatible preinstalled python. ")


def create_tmp_folder():
    """ Creates the temporary folder where  the downloads for the installation are stored. """

    path = configurations.TMP_FOLDER
    if os.path.exists(path):
        shutil.rmtree(path, onerror=onerror)
    while os.path.exists(path):  # wait until system deleted the folder
        pass
    if not os.path.exists(path):
        os.mkdir(path)


def clone_natlink():
    """Downloads the current release of Natlink and prompts the
        user to override previous Natlink installations if necessary"""

    path = configurations.NATLINK_INSTALL_DIR
    if os.path.exists(path) and os.path.exists(path + "/core"):
        print(f"{path} already exists! This suggests that you have Natlink already installed. ")
        if query_yes_no("Do you want to upgrade? Warning the core directory will be completely overwritten!"):
            shutil.rmtree(path + "/core")
        else:
            raise AbortInstallation

    elif os.path.exists(path):
        print(
            "This new Natlink version establishes and updated folder structure. To make sure everything works correctly this script will completely remove c:\\natlink and all subfolders.")
        if not query_yes_no(
                "[IMPORTANT] We highly recommend to backup c:/natlink/MacroSystem folder before continuing with the installation. Proceed to delete old Natlink folder?"):
            raise AbortInstallation
        shutil.rmtree(path, onerror=onerror)

    print("Downloading Natlink files: ")
    wget.download(
        "https://gitlab.com/knork/natlink2/-/archive/ba01632ff92a10b210c67883c2b77f0c85da7466/natlink2-ba01632ff92a10b210c67883c2b77f0c85da7466.zip",
        configurations.TMP_FOLDER + "natlink.zip")
    print("\n")
    with ZipFile(configurations.TMP_FOLDER + "natlink.zip", 'r') as zipObj:
        zipObj.extractall(configurations.TMP_FOLDER + "clone")
    print(f"Copying files to {configurations.NATLINK_INSTALL_DIR}")
    copytree(configurations.TMP_FOLDER + f"clone\\{os.listdir(configurations.TMP_FOLDER + 'clone')[0]}\\MacroSystem",
             configurations.NATLINK_INSTALL_DIR, )
