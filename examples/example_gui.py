"""Example custom GUI for natlink — tkinter UIProvider implementation.

Demonstrates implementing the UIProvider protocol to replace natlink's
default Win32 tray icon and output window with a custom tkinter GUI.

Two required methods: on_state_changed() and on_text().
Optional extensions: show_output(), hide_output(), clear_output().

Usage:
    import natlink
    from example_gui import TkUIProvider

    natlink.set_ui_provider(TkUIProvider())
    natlink.natConnect()
    natlink.waitForSpeech()

Grammar authors can access the active provider:
    provider = natlink.get_ui_provider()
    if hasattr(provider, "show_output"):
        provider.show_output()
"""

import logging
import threading
import tkinter as tk
from tkinter import scrolledtext

import natlink
from natlink import PHASE_CONNECTED, PHASE_ERROR

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared tkinter thread
# ---------------------------------------------------------------------------

_tk_root = None
_tk_ready = threading.Event()
_tk_thread = None


def _ensure_tk():
    """Start the shared tkinter thread if not already running."""
    global _tk_thread
    if _tk_thread is not None and _tk_thread.is_alive():
        return _tk_root
    _tk_ready.clear()
    _tk_thread = threading.Thread(target=_tk_run, daemon=True, name="tk-gui")
    _tk_thread.start()
    _tk_ready.wait(timeout=5)
    return _tk_root


def _tk_run():
    global _tk_root
    _tk_root = tk.Tk()
    _tk_root.withdraw()
    _tk_ready.set()
    _tk_root.mainloop()


def _tk_after(fn, *args):
    """Schedule fn(*args) on the tkinter thread."""
    if _tk_root:
        _tk_root.after(0, lambda: fn(*args))


# ---------------------------------------------------------------------------
# UIProvider — unified tkinter GUI
# ---------------------------------------------------------------------------

class TkUIProvider:
    """UIProvider using tkinter for status bar and output window.

    Required protocol methods:
        on_state_changed(state)  — update status bar
        on_text(text, level=20)  — append to output window

    Optional extensions (used by natlink_ui.show_output() etc.):
        show_output()  — bring output window to front
        hide_output()  — hide output window
        clear_output() — clear output window text
    """

    def __init__(self):
        self._status_window = None
        self._status_label = None
        self._output_window = None
        self._output_text = None
        _ensure_tk()
        ready = threading.Event()
        _tk_after(self._create, ready)
        ready.wait(timeout=5)

    def _create(self, ready):
        self._status_window = tk.Toplevel(_tk_root)
        self._status_window.title("Natlink")
        self._status_window.geometry("250x30+10+10")
        self._status_window.attributes("-topmost", True)
        self._status_window.overrideredirect(True)

        self._status_label = tk.Label(
            self._status_window, text="Natlink - Starting",
            bg="gray", fg="white", font=("Arial", 10, "bold"))
        self._status_label.pack(fill=tk.BOTH, expand=True)
        self._status_label.bind("<Button-3>", self._show_menu)

        self._output_window = tk.Toplevel(_tk_root)
        self._output_window.title("Natlink Output")
        self._output_window.geometry("600x400")
        self._output_window.protocol("WM_DELETE_WINDOW",
                                      self._output_window.withdraw)

        self._output_text = scrolledtext.ScrolledText(
            self._output_window, wrap=tk.WORD, state=tk.DISABLED,
            font=("Consolas", 10))
        self._output_text.pack(fill=tk.BOTH, expand=True)
        self._output_text.tag_configure("error", foreground="red")

        self._output_window.withdraw()
        ready.set()

    # --- Required UIProvider methods ---

    def on_state_changed(self, state) -> None:
        colors = {PHASE_CONNECTED: "green", PHASE_ERROR: "orange"}
        color = colors.get(state.phase, "red")
        text = f"Natlink - {state.phase.replace('_', ' ')}"

        if state.phase == PHASE_CONNECTED and state.mic_state:
            text = f"{state.user_name or 'Connected'} — mic {state.mic_state}"
        elif state.phase == PHASE_ERROR and state.error_message:
            text = f"Natlink - {state.error_message}"

        _tk_after(self._update_status, color, text)

    def on_text(self, text: str, level: int = 20) -> None:
        if self._output_text is None:
            return
        tag = "error" if level >= 30 else ""

        def _append():
            self._output_text.config(state=tk.NORMAL)
            self._output_text.insert(tk.END, text, tag)
            if not text.endswith("\n"):
                self._output_text.insert(tk.END, "\n", tag)
            self._output_text.see(tk.END)
            self._output_text.config(state=tk.DISABLED)

        _tk_after(_append)

    # --- Optional extensions (used by natlink_ui.show_output() etc.) ---

    def show_output(self):
        if self._output_window:
            _tk_after(self._output_window.deiconify)

    def hide_output(self):
        if self._output_window:
            _tk_after(self._output_window.withdraw)

    def clear_output(self):
        def _clear():
            if self._output_text:
                self._output_text.config(state=tk.NORMAL)
                self._output_text.delete("1.0", tk.END)
                self._output_text.config(state=tk.DISABLED)
        _tk_after(_clear)

    def stop(self):
        if self._status_window:
            _tk_after(self._status_window.destroy)
        if self._output_window:
            _tk_after(self._output_window.destroy)

    # --- Internal ---

    def _update_status(self, color, text):
        if self._status_label:
            self._status_label.config(bg=color, text=text)
        if self._status_window:
            self._status_window.deiconify()

    def _show_menu(self, event):
        menu = tk.Menu(self._status_window, tearoff=0)

        menu.add_command(label="Show Output",
                         command=lambda: self.show_output())
        menu.add_separator()
        menu.add_command(label="Restart Dragon",
                         command=lambda: self._dispatch(natlink.restart_dragon))
        menu.add_command(label="Reload Grammars",
                         command=lambda: self._dispatch(natlink.reload_grammars))
        menu.add_separator()

        mic_menu = tk.Menu(menu, tearoff=0)
        mic_menu.add_command(label="On",
                             command=lambda: self._dispatch(natlink.set_mic, "on"))
        mic_menu.add_command(label="Off",
                             command=lambda: self._dispatch(natlink.set_mic, "off"))
        mic_menu.add_command(label="Sleep",
                             command=lambda: self._dispatch(natlink.set_mic, "sleeping"))
        menu.add_cascade(label="Microphone", menu=mic_menu)

        menu.add_separator()
        menu.add_command(label="Exit",
                         command=lambda: self._dispatch(natlink.exit_natlink))

        menu.post(event.x_root, event.y_root)

    def _dispatch(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()
