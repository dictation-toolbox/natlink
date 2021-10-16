from typing import Optional

from ._natlink_core import *
from .config import NoGoodConfigFoundException
from .loader import NatlinkMain
from .loader import run as run_loader
from .redirect_output import redirect as redirect_all_output_to_natlink_window

active_loader: Optional[NatlinkMain] = None
