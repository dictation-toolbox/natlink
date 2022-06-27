'''Python portion of Natlink, a compatibility module for Dragon Naturally Speaking'''
__version__="0.1"
#pylint:disable=C0114, W0401
from typing import Optional

from .config import NoGoodConfigFoundException
from .loader import NatlinkMain
from .loader import run as run_loader
from .redirect_output import redirect as redirect_all_output_to_natlink_window

active_loader: Optional[NatlinkMain] = None
