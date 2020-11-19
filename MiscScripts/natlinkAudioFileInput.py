"""
Command-line program for using Natlink's inputFromFile() function to process
speech from a wave file.

It looks like Dragon expects wave files to have a 16 kHz sample rate, a
signed 16-bit (LE) format and one recording channel. A NatError will be
raised if the file was not accepted.
"""

import argparse

import natlink
import win32api
import win32con


def main():
    # Define required and optional command-line arguments.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Script for safely using Natlink's inputFromFile() "
        "function.\n\n"
        "This script is intended to be run in a dedicated process in "
        "order to work around potential page faults."
    )
    parser.add_argument(
        "file", type=argparse.FileType("r"),
        help="Name of the wave file to take input from."
    )
    parser.add_argument(
        "--no-utt-detect", default=False, action="store_true",
        help="Do not perform utterance detection (i.e. don't split speech "
        "at pauses) when processing the specified wave file. Use this if "
        "the file contains only one utterance."
    )

    # Parse command-line arguments.
    args = parser.parse_args()

    # Get the filename and uttdetect arguments.
    f = args.file
    filename = f.name
    f.close()  # Close the file object created by argparse
    uttdetect = 0 if args.no_utt_detect else 1

    # Instruct Windows to suppress the error reporting window if this script
    # causes a page fault.
    win32api.SetErrorMode(win32con.SEM_NOGPFAULTERRORBOX)

    # Connect to NatSpeak.
    natlink.natConnect()
    try:
        # Process the specified wave file using the specified options.
        natlink.inputFromFile(filename, 0, [], uttdetect)
    finally:
        # Disconnect from NatSpeak.
        natlink.natDisconnect()


if __name__ == '__main__':
    main()
