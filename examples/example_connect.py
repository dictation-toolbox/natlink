"""Example: connect to Dragon and query basic info.

The simplest possible natlink script — connect, read state, disconnect.

Usage:
    python example_connect.py

Requires Dragon to be running.
"""

import sys
sys.coinit_flags = 2  # STA mode — must be set before importing comtypes

import natlink


def main():
    with natlink.natConnect():
        user, directory = natlink.getCurrentUser()
        print(f"User: {user}")
        print(f"Directory: {directory}")

        mic = natlink.getMicState()
        print(f"Microphone: {mic}")

        module, title, hwnd = natlink.getCurrentModule()
        print(f"Foreground: {module}")
        print(f"  Title: {title}")
        print(f"  HWND: {hwnd}")

        running = natlink.isNatSpeakRunning()
        print(f"Dragon running: {bool(running)}")


if __name__ == "__main__":
    main()
