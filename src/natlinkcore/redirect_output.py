# new redirect trick, starting june 2020 (by Jan Scheffczyk)
# this module is imported by natlink.pyd.
# So apart from starting natlink via natlink.pyd (as called from Dragon),
# redirection of stdout and stderr is never done (unless you import this module)
#pylint:disable=C0114, C0115, 
import sys
from types import TracebackType
from typing import TextIO, Optional, Type, Iterator, AnyStr, Iterable, List
from  pydebugstring.output import outputDebugString

outputDebugString(f"Loading {__file__}  sys.path={sys.path}" )

outputDebugString(f"{__file__} importing _natlink_core" )

from natlink import _natlink_core as natlink

outputDebugString(f"{__file__} imported _natlink_core" )


class FakeTextIO(TextIO):
    def __enter__(self) -> TextIO:
        pass

    def close(self) -> None:
        pass

    def fileno(self) -> int:
        raise NotImplementedError()

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        return False

    def read(self, n: int = ...) -> AnyStr:
        raise NotImplementedError()

    def readable(self) -> bool:
        return False

    def readline(self, limit: int = ...) -> AnyStr:
        raise NotImplementedError()

    def readlines(self, hint: int = ...) -> List[AnyStr]:
        raise NotImplementedError()

    def seek(self, offset: int, whence: int = ...) -> int:
        raise NotImplementedError()

    def seekable(self) -> bool:
        return False

    def tell(self) -> int:
        raise NotImplementedError()

    def truncate(self, size: Optional[int] = ...) -> int:
        raise NotImplementedError()

    def writable(self) -> bool:
        return True

    def write(self, s: AnyStr) -> int:
        raise NotImplementedError()

    def writelines(self, lines: Iterable[AnyStr]) -> None:
        raise NotImplementedError()

    def __next__(self) -> AnyStr:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[AnyStr]:
        raise NotImplementedError()

    def __exit__(self, t: Optional[Type[BaseException]], value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> Optional[bool]:
        pass


class NewStdout(FakeTextIO):
    softspace = 1

    def write(self, text: AnyStr) -> int:
        if not isinstance(text, str):
            raise ValueError(f'Can only write str, not {type(text)}')
        natlink.displayText(text, False)
        return len(text)


class NewStderr(FakeTextIO):
    softspace = 1

    def write(self, text: AnyStr) -> int:
        if not isinstance(text, str):
            raise ValueError(f'Can only write str, not {type(text)}')
        natlink.displayText(text, True)
        return len(text)


def redirect() -> None:
    outputDebugString(f"In {__file__}.redirect()" )
    sys.stdout = NewStdout()
    sys.stderr = NewStderr()


outputDebugString(f"{__file__}  loaded" )