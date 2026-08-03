"""natlink_com — Direct COM backend for natlink.

Provides 64-bit out-of-process COM calls to Dragon NaturallySpeaking
via comtypes and custom marshal DLLs for cross-bitness marshaling.
"""

from ._com_bridge import NatlinkCOM
from ._errors import NatlinkCOMError
from ._gram_obj import ComGramObj
from ._res_obj import ComResObj
from ._dict_obj import ComDictObj
from ._ini_file import IniFile
from ._config import print_config
from ._win32 import (msgbox, MB_ICONERROR, MB_ICONWARNING, MB_ICONQUESTION,
                     MB_YESNO, IDYES, IDNO)
from ._launcher import request_shutdown, signal_restart
