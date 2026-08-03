"""Example: dictation object — capture free-form speech into a text buffer.

Demonstrates DictObj lifecycle:
  1. Create and activate on a window
  2. Handle begin and change callbacks
  3. Read the text buffer
  4. Deactivate and destroy

Usage:
    python example_dictation.py

Requires Dragon to be running. Dictate freely — text appears in the
console as Dragon recognizes it.
"""

import sys
import time
sys.coinit_flags = 2  # STA

import natlink


class DictationCapture:
    """Captures dictation into a text buffer and prints changes."""

    def __init__(self):
        self.dobj = natlink.DictObj()
        self._prev_length = 0

    def start(self, window_handle=0):
        """Activate dictation on a window (0 = any window)."""
        self.dobj.setBeginCallback(self.on_begin)
        self.dobj.setChangeCallback(self.on_change)
        self.dobj.activate(window_handle)
        print("Dictation active. Speak freely.")

    def stop(self):
        """Deactivate and show final buffer."""
        text = self.dobj.getText(0, self.dobj.getLength())
        self.dobj.deactivate()
        # deactivate() alone releases nothing -- Dragon keeps every
        # reference on the dictation sink until destroy() is called.
        self.dobj.destroy()
        print(f"\nFinal buffer ({self.dobj.getLength()} chars):")
        print(text)

    def on_begin(self, module_info):
        """Called at the start of each utterance."""
        pass

    def on_change(self, start, del_count, text, sel_start, sel_end):
        """Called when Dragon modifies the text buffer.

        Args:
            start: offset where the change begins
            del_count: number of characters deleted
            text: new text inserted at start
            sel_start: new selection start
            sel_end: new selection end
        """
        length = self.dobj.getLength()
        full_text = self.dobj.getText(0, length)
        print(f"  [{length} chars] {full_text}")


def main():
    capture = DictationCapture()
    try:
        with natlink.natConnect():
            capture.start()
            print("Press Ctrl+C to stop.\n")
            try:
                natlink.waitForSpeech()
            except KeyboardInterrupt:
                pass
            capture.stop()  # must run before natDisconnect tears down COM
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
