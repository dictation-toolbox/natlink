"""Output redirection — routes sys.stdout/stderr through notify_text."""

import logging
import sys


class _OutputRedirector:
    """Redirects sys.stdout or sys.stderr through notify_text.

    Implements the full TextIO interface so code that inspects stream
    properties (logging, pytest, IDE consoles) works correctly.
    """

    def __init__(self, level: int = logging.INFO):
        self._level = level
        self._original = sys.stderr if level >= logging.ERROR else sys.stdout
        self.encoding = getattr(self._original, "encoding", "utf-8")
        self.errors = getattr(self._original, "errors", "strict")
        self.newlines = None
        self.mode = "w"

    def write(self, text: str) -> int:
        if text and text.strip():
            try:
                from natlink_compat import notify_text
                notify_text(text, level=self._level)
            except Exception:
                # Never let UI dispatch crash the caller; fall back to the
                # original stream so early-startup output isn't lost.
                if self._original is not None:
                    try:
                        self._original.write(text)
                    except Exception:
                        pass
        return len(text) if text else 0

    def writelines(self, lines) -> None:
        for line in lines:
            self.write(line)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass

    @property
    def closed(self) -> bool:
        return False

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def isatty(self) -> bool:
        return False

    def fileno(self) -> int:
        if self._original is not None and hasattr(self._original, 'fileno'):
            return self._original.fileno()
        raise OSError("stream has no fileno")

    def read(self, *args):
        raise OSError("not readable")

    def readline(self, *args):
        raise OSError("not readable")

    def readlines(self, *args):
        raise OSError("not readable")

    def seek(self, *args):
        raise OSError("not seekable")

    def tell(self) -> int:
        raise OSError("not seekable")

    def truncate(self, *args):
        raise OSError("not seekable")


def install_redirect():
    """Replace sys.stdout/stderr with redirectors that route through notify_text."""
    sys.stdout = _OutputRedirector(level=logging.INFO)
    sys.stderr = _OutputRedirector(level=logging.ERROR)


def uninstall_redirect():
    """Restore original sys.stdout/stderr."""
    if isinstance(sys.stdout, _OutputRedirector):
        sys.stdout = sys.stdout._original
    if isinstance(sys.stderr, _OutputRedirector):
        sys.stderr = sys.stderr._original
