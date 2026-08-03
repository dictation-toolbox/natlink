# -*- coding: utf-8 -*-
"""Vendored comtypes-generated wrappers for Dragon interfaces (DNS 13 / DPI 14).

Auto-generated from dragon_interfaces_v13_v14.tlb via comtypes.client.GetModule().
Scrubbed: absolute paths removed, stdole references replaced with comtypes.IUnknown.

DO NOT EDIT BY HAND — regenerate with: python scripts/gen_tlb_wrappers.py
"""

from ctypes import *
import comtypes
from comtypes import COMMETHOD, GUID, IUnknown
from ctypes import HRESULT
from ctypes.wintypes import _FILETIME
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from comtypes import hints


_lcid = 0  # change this if required
typelib_path = ''  # vendored — no TLB path needed
WSTRING = c_wchar_p
STRING = c_char_p

# values for enumeration '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0018'
SAPI_POSTYPE = 1
__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0018 = c_int  # enum

# values for enumeration '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0002'
VPS_UNKNOWN = 0
VPS_NOUN = 1
VPS_VERB = 2
VPS_ADVERB = 3
VPS_ADJECTIVE = 4
VPS_PROPERNOUN = 5
VPS_PRONOUN = 6
VPS_CONJUNCTION = 7
VPS_CARDINAL = 8
VPS_ORDINAL = 9
VPS_DETERMINER = 10
VPS_QUANTIFIER = 11
VPS_PUNCTUATION = 12
VPS_CONTRACTION = 13
VPS_INTERJECTION = 14
VPS_ABBREVIATION = 15
VPS_PREPOSITION = 16
__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0002 = c_int  # enum

# values for enumeration '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0003'
SRGRMFMT_CFG = 0
SRGRMFMT_LIMITEDDOMAIN = 1
SRGRMFMT_DICTATION = 2
SRGRMFMT_CFGNATIVE = 32768
SRGRMFMT_LIMITEDDOMAINNATIVE = 32769
SRGRMFMT_DICTATIONNATIVE = 32770
SRGRMFMT_DRAGONNATIVE1 = 33025
SRGRMFMT_DRAGONNATIVE2 = 33026
SRGRMFMT_DRAGONNATIVE3 = 33027
__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0003 = c_int  # enum

# values for enumeration '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0017'
CHARSET_TEXT = 0
CHARSET_IPAPHONETIC = 1
CHARSET_ENGINEPHONETIC = 2
__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0017 = c_int  # enum

# aliases for enums
SRGRMFMT = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0003
VOICECHARSET = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0017
VOICEPARTOFSPEECH = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0002



class IDgnSRTopic2W(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109021-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def New(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def Select(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def SpeakerCopy(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


IDgnSRTopic2W._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'New',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1'),
        (['in'], WSTRING, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Select',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SpeakerCopy',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1')
    ),
]

################################################################
# code template for IDgnSRTopic2W implementation
# class IDgnSRTopic2W_Impl(object):
#     def New(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def Select(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def SpeakerCopy(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0019(Structure):
    pass


POSINFO = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0019

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0019._fields_ = [
    ('POS_Type', __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0018),
    ('SAPI_POS', __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0002),
    ('Dgn_POS', c_ubyte * 16),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0019) == 24, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0019)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0019) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0019)


class IDgnSRWordEnumW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109009-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Next(self, p0: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def Skip(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Reset(self) -> hints.Hresult: ...
        def Clone(self) -> 'IDgnSRWordEnumW': ...
        def GetCount(self) -> hints.Incomplete: ...


IDgnSRWordEnumW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Next',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ubyte), 'p1'),
        (['out'], POINTER(c_ulong), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Skip',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD(
        [],
        HRESULT,
        'Clone',
        (['out'], POINTER(POINTER(IDgnSRWordEnumW)), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetCount',
        (['out'], POINTER(c_ulong), 'p0')
    ),
]

################################################################
# code template for IDgnSRWordEnumW implementation
# class IDgnSRWordEnumW_Impl(object):
#     def Next(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#
#     def Skip(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Reset(self):
#         '-no docstring-'
#         #return 
#
#     def Clone(self):
#         '-no docstring-'
#         #return p0
#
#     def GetCount(self):
#         '-no docstring-'
#         #return p0
#


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005(Structure):
    pass


__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005._fields_ = [
    ('LanguageID', c_ushort),
    ('szDialect', c_ushort * 64),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005) == 130, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005) == 2, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005)


class IVDct0NotifySinkA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108401-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Command(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TextSelChanged(self) -> hints.Hresult: ...
        def TextChanged(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TextBookmarkChanged(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def PhraseStart(self) -> hints.Hresult: ...
        def PhraseFinish(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def PhraseHypothesis(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def UtteranceBegin(self) -> hints.Hresult: ...
        def UtteranceEnd(self) -> hints.Hresult: ...
        def VUMeter(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def AttribChanged(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Interference(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Training(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Dictating(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Reserved15(self, p0: hints.Incomplete) -> hints.Hresult: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010(Structure):
    pass


SRPHRASEA = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010

IVDct0NotifySinkA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Command',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'TextSelChanged'),
    COMMETHOD(
        [],
        HRESULT,
        'TextChanged',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextBookmarkChanged',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'PhraseStart'),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseFinish',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(SRPHRASEA), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseHypothesis',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(SRPHRASEA), 'p1')
    ),
    COMMETHOD([], HRESULT, 'UtteranceBegin'),
    COMMETHOD([], HRESULT, 'UtteranceEnd'),
    COMMETHOD(
        [],
        HRESULT,
        'VUMeter',
        (['in'], c_ushort, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'AttribChanged',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Interference',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Training',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Dictating',
        (['in'], STRING, 'p0'),
        (['in'], c_int, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved15',
        (['in'], c_ulong, 'p0')
    ),
]

################################################################
# code template for IVDct0NotifySinkA implementation
# class IVDct0NotifySinkA_Impl(object):
#     def Command(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TextSelChanged(self):
#         '-no docstring-'
#         #return 
#
#     def TextChanged(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TextBookmarkChanged(self, p0):
#         '-no docstring-'
#         #return 
#
#     def PhraseStart(self):
#         '-no docstring-'
#         #return 
#
#     def PhraseFinish(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def PhraseHypothesis(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def UtteranceBegin(self):
#         '-no docstring-'
#         #return 
#
#     def UtteranceEnd(self):
#         '-no docstring-'
#         #return 
#
#     def VUMeter(self, p0):
#         '-no docstring-'
#         #return 
#
#     def AttribChanged(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Interference(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Training(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Dictating(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Reserved15(self, p0):
#         '-no docstring-'
#         #return 
#


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004(Structure):
    pass


__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004._fields_ = [
    ('LanguageID', c_ushort),
    ('szDialect', c_char * 64),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004) == 66, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004) == 2, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004)


class ISRResGraphW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9AA-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def BestPathPhoneme(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def BestPathWord(self, p0: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def GetPhonemeNode(self, p0: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def GetWordNode(self, p0: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def PathScorePhoneme(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Incomplete: ...
        def PathScoreWord(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Incomplete: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0012(Structure):
    pass


SRRESPHONEMENODE = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0012


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0013(Structure):
    pass


SRRESWORDNODE = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0013

ISRResGraphW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'BestPathPhoneme',
        (['in'], c_ulong, 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BestPathWord',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ulong), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetPhonemeNode',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(SRRESPHONEMENODE), 'p1'),
        (['in', 'out'], POINTER(c_ushort), 'p2'),
        (['in', 'out'], POINTER(c_ushort), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetWordNode',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(SRRESWORDNODE), 'p1'),
        (['out'], POINTER(c_ubyte), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PathScorePhoneme',
        (['in'], POINTER(c_ulong), 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_int), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PathScoreWord',
        (['in'], POINTER(c_ulong), 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_int), 'p2')
    ),
]

################################################################
# code template for ISRResGraphW implementation
# class ISRResGraphW_Impl(object):
#     def BestPathPhoneme(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def BestPathWord(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def GetPhonemeNode(self, p0):
#         '-no docstring-'
#         #return p1, p2, p3
#
#     def GetWordNode(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#
#     def PathScorePhoneme(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def PathScoreWord(self, p0, p1):
#         '-no docstring-'
#         #return p2
#


class ISRGramDictationW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9A3-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Context(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Hint(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Words(self, p0: hints.Incomplete) -> hints.Hresult: ...


ISRGramDictationW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Context',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Hint',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Words',
        (['in'], WSTRING, 'p0')
    ),
]

################################################################
# code template for ISRGramDictationW implementation
# class ISRGramDictationW_Impl(object):
#     def Context(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Hint(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Words(self, p0):
#         '-no docstring-'
#         #return 
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0013._fields_ = [
    ('dwNextWordNode', c_ulong),
    ('dwUpAlternateWordNode', c_ulong),
    ('dwDownAlternateWordNode', c_ulong),
    ('dwPreviousWordNode', c_ulong),
    ('dwPhonemeNode', c_ulong),
    ('qwStartTime', c_ulonglong),
    ('qwEndTime', c_ulonglong),
    ('dwWordScore', c_ulong),
    ('wVolume', c_ushort),
    ('wPitch', c_ushort),
    ('pos', __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0002),
    ('dwCFGParse', c_ulong),
    ('dwCue', c_ulong),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0013) == 64, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0013)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0013) == 8, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0013)


class IVDct0NotifySinkW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109401-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Command(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TextSelChanged(self) -> hints.Hresult: ...
        def TextChanged(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TextBookmarkChanged(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def PhraseStart(self) -> hints.Hresult: ...
        def PhraseFinish(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def PhraseHypothesis(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def UtteranceBegin(self) -> hints.Hresult: ...
        def UtteranceEnd(self) -> hints.Hresult: ...
        def VUMeter(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def AttribChanged(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Interference(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Training(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Dictating(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Reserved15(self, p0: hints.Incomplete) -> hints.Hresult: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011(Structure):
    pass


SRPHRASEW = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011

IVDct0NotifySinkW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Command',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'TextSelChanged'),
    COMMETHOD(
        [],
        HRESULT,
        'TextChanged',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextBookmarkChanged',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'PhraseStart'),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseFinish',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(SRPHRASEW), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseHypothesis',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(SRPHRASEW), 'p1')
    ),
    COMMETHOD([], HRESULT, 'UtteranceBegin'),
    COMMETHOD([], HRESULT, 'UtteranceEnd'),
    COMMETHOD(
        [],
        HRESULT,
        'VUMeter',
        (['in'], c_ushort, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'AttribChanged',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Interference',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Training',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Dictating',
        (['in'], WSTRING, 'p0'),
        (['in'], c_int, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved15',
        (['in'], c_ulong, 'p0')
    ),
]

################################################################
# code template for IVDct0NotifySinkW implementation
# class IVDct0NotifySinkW_Impl(object):
#     def Command(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TextSelChanged(self):
#         '-no docstring-'
#         #return 
#
#     def TextChanged(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TextBookmarkChanged(self, p0):
#         '-no docstring-'
#         #return 
#
#     def PhraseStart(self):
#         '-no docstring-'
#         #return 
#
#     def PhraseFinish(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def PhraseHypothesis(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def UtteranceBegin(self):
#         '-no docstring-'
#         #return 
#
#     def UtteranceEnd(self):
#         '-no docstring-'
#         #return 
#
#     def VUMeter(self, p0):
#         '-no docstring-'
#         #return 
#
#     def AttribChanged(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Interference(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Training(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Dictating(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Reserved15(self, p0):
#         '-no docstring-'
#         #return 
#


class IDgnSRTrainingA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108014-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def TrainingModeSet(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TrainingModeGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def TrainingPerform(self) -> hints.Hresult: ...
        def TrainingCancel(self) -> hints.Hresult: ...
        def TotalCountGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...


IDgnSRTrainingA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'TrainingModeSet',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TrainingModeGet',
        (['in', 'out'], POINTER(c_ulong), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD([], HRESULT, 'TrainingPerform'),
    COMMETHOD([], HRESULT, 'TrainingCancel'),
    COMMETHOD(
        [],
        HRESULT,
        'TotalCountGet',
        (['in', 'out'], POINTER(c_int), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
]

################################################################
# code template for IDgnSRTrainingA implementation
# class IDgnSRTrainingA_Impl(object):
#     def TrainingModeSet(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TrainingModeGet(self):
#         '-no docstring-'
#         #return p0, p1, p2
#
#     def TrainingPerform(self):
#         '-no docstring-'
#         #return 
#
#     def TrainingCancel(self):
#         '-no docstring-'
#         #return 
#
#     def TotalCountGet(self):
#         '-no docstring-'
#         #return p0, p1, p2
#


class ISRResAudio(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9A7-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def GetWAV(self) -> hints.Incomplete: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0001(Structure):
    pass


SDATA = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0001

ISRResAudio._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'GetWAV',
        (['out'], POINTER(SDATA), 'p0')
    ),
]

################################################################
# code template for ISRResAudio implementation
# class ISRResAudio_Impl(object):
#     def GetWAV(self):
#         '-no docstring-'
#         #return p0
#


class IDgnSRGramDictationA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108015-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def RecentBufferFlush(self) -> hints.Hresult: ...
        def RecentBufferCommit(self) -> hints.Hresult: ...
        def CommittedFlush(self) -> hints.Hresult: ...
        def Words(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


IDgnSRGramDictationA._methods_ = [
    COMMETHOD([], HRESULT, 'RecentBufferFlush'),
    COMMETHOD([], HRESULT, 'RecentBufferCommit'),
    COMMETHOD([], HRESULT, 'CommittedFlush'),
    COMMETHOD(
        [],
        HRESULT,
        'Words',
        (['in'], SDATA, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
]

################################################################
# code template for IDgnSRGramDictationA implementation
# class IDgnSRGramDictationA_Impl(object):
#     def RecentBufferFlush(self):
#         '-no docstring-'
#         #return 
#
#     def RecentBufferCommit(self):
#         '-no docstring-'
#         #return 
#
#     def CommittedFlush(self):
#         '-no docstring-'
#         #return 
#
#     def Words(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class IDgnVDctTextA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10840B-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def VisibleTextSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def VisibleTextGet(self) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def ThatGet(self) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def CorrectionDialog(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def RecentBufferCommit(self) -> hints.Hresult: ...


IDgnVDctTextA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'VisibleTextSet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'VisibleTextGet',
        (['out'], POINTER(c_ulong), 'p0'),
        (['out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ThatGet',
        (['out'], POINTER(c_ulong), 'p0'),
        (['out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'CorrectionDialog',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD([], HRESULT, 'RecentBufferCommit'),
]

################################################################
# code template for IDgnVDctTextA implementation
# class IDgnVDctTextA_Impl(object):
#     def VisibleTextSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def VisibleTextGet(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def ThatGet(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def CorrectionDialog(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def RecentBufferCommit(self):
#         '-no docstring-'
#         #return 
#


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0022(Structure):
    pass


VDCTTOPICA = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0022


class IVDct0TextA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10840A-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Lock(self) -> hints.Hresult: ...
        def UnLock(self) -> hints.Hresult: ...
        def TextGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...
        def TextSet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...
        def TextMove(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...
        def TextRemove(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def TextSelSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def TextSelGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def GetChanges(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def BookmarkAdd(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def BookmarkRemove(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def BookmarkMove(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def BookmarkQuery(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def BookmarkEnum(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Hint(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Words(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def ResultsGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def AutoLockSet(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def AutoLockGet(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def Reserved22(self, p0: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Reserved23(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0024(Structure):
    pass


VDCTBOOKMARK = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0024

IVDct0TextA._methods_ = [
    COMMETHOD([], HRESULT, 'Lock'),
    COMMETHOD([], HRESULT, 'UnLock'),
    COMMETHOD(
        [],
        HRESULT,
        'TextGet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['out'], POINTER(SDATA), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextSet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], STRING, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextMove',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextRemove',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextSelSet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextSelGet',
        (['in', 'out'], POINTER(c_ulong), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetChanges',
        (['in', 'out'], POINTER(c_ulong), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkAdd',
        (['in'], POINTER(VDCTBOOKMARK), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkRemove',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkMove',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkQuery',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(VDCTBOOKMARK), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkEnum',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(POINTER(VDCTBOOKMARK)), 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Hint',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Words',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ResultsGet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3'),
        (['out'], POINTER(POINTER(IUnknown)), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'AutoLockSet',
        (['in'], c_int, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'AutoLockGet',
        (['in', 'out'], POINTER(c_int), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved22',
        (['in'], c_ulong, 'p0'),
        (['out'], STRING, 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved23',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], STRING, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
]

################################################################
# code template for IVDct0TextA implementation
# class IVDct0TextA_Impl(object):
#     def Lock(self):
#         '-no docstring-'
#         #return 
#
#     def UnLock(self):
#         '-no docstring-'
#         #return 
#
#     def TextGet(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def TextSet(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#
#     def TextMove(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#
#     def TextRemove(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def TextSelSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def TextSelGet(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def GetChanges(self):
#         '-no docstring-'
#         #return p0, p1, p2, p3
#
#     def BookmarkAdd(self, p0):
#         '-no docstring-'
#         #return 
#
#     def BookmarkRemove(self, p0):
#         '-no docstring-'
#         #return 
#
#     def BookmarkMove(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def BookmarkQuery(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def BookmarkEnum(self, p0, p1):
#         '-no docstring-'
#         #return p2, p3
#
#     def Hint(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Words(self, p0):
#         '-no docstring-'
#         #return 
#
#     def ResultsGet(self, p0, p1):
#         '-no docstring-'
#         #return p2, p3, p4
#
#     def AutoLockSet(self, p0):
#         '-no docstring-'
#         #return 
#
#     def AutoLockGet(self):
#         '-no docstring-'
#         #return p0
#
#     def Reserved22(self, p0):
#         '-no docstring-'
#         #return p1, p2
#
#     def Reserved23(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0022._fields_ = [
    ('szTopic', c_char * 32),
    ('language', __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0022) == 98, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0022)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0022) == 2, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0022)


class ISRResMemory(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9AB-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Free(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Get(self) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def LockGet(self) -> hints.Incomplete: ...
        def LockSet(self, p0: hints.Incomplete) -> hints.Hresult: ...


ISRResMemory._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Free',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Get',
        (['out'], POINTER(c_ulong), 'p0'),
        (['out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'LockGet',
        (['out'], POINTER(c_int), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'LockSet',
        (['in'], c_int, 'p0')
    ),
]

################################################################
# code template for ISRResMemory implementation
# class ISRResMemory_Impl(object):
#     def Free(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Get(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def LockGet(self):
#         '-no docstring-'
#         #return p0
#
#     def LockSet(self, p0):
#         '-no docstring-'
#         #return 
#

LANGUAGEA = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004


class ISRGramNotifySinkA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{EFEEA350-CE5E-11CD-9D96-00AA002FC7C9}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def BookMark(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Paused(self) -> hints.Hresult: ...
        def PhraseFinish(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> hints.Hresult: ...
        def PhraseHypothesis(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> hints.Hresult: ...
        def PhraseStart(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def ReEvaluate(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Training(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def UnArchive(self, p0: hints.Incomplete) -> hints.Hresult: ...


ISRGramNotifySinkA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'BookMark',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'Paused'),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseFinish',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulonglong, 'p1'),
        (['in'], c_ulonglong, 'p2'),
        (['in'], POINTER(SRPHRASEA), 'p3'),
        (['in'], POINTER(IUnknown), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseHypothesis',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulonglong, 'p1'),
        (['in'], c_ulonglong, 'p2'),
        (['in'], POINTER(SRPHRASEA), 'p3'),
        (['in'], POINTER(IUnknown), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseStart',
        (['in'], c_ulonglong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ReEvaluate',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Training',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'UnArchive',
        (['in'], POINTER(IUnknown), 'p0')
    ),
]

################################################################
# code template for ISRGramNotifySinkA implementation
# class ISRGramNotifySinkA_Impl(object):
#     def BookMark(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Paused(self):
#         '-no docstring-'
#         #return 
#
#     def PhraseFinish(self, p0, p1, p2, p3, p4):
#         '-no docstring-'
#         #return 
#
#     def PhraseHypothesis(self, p0, p1, p2, p3, p4):
#         '-no docstring-'
#         #return 
#
#     def PhraseStart(self, p0):
#         '-no docstring-'
#         #return 
#
#     def ReEvaluate(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Training(self, p0):
#         '-no docstring-'
#         #return 
#
#     def UnArchive(self, p0):
#         '-no docstring-'
#         #return 
#


class IDgnVDctTextW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10940B-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def VisibleTextSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def VisibleTextGet(self) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def ThatGet(self) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def CorrectionDialog(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def RecentBufferCommit(self) -> hints.Hresult: ...


IDgnVDctTextW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'VisibleTextSet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'VisibleTextGet',
        (['out'], POINTER(c_ulong), 'p0'),
        (['out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ThatGet',
        (['out'], POINTER(c_ulong), 'p0'),
        (['out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'CorrectionDialog',
        (['in'], c_int, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD([], HRESULT, 'RecentBufferCommit'),
]

################################################################
# code template for IDgnVDctTextW implementation
# class IDgnVDctTextW_Impl(object):
#     def VisibleTextSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def VisibleTextGet(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def ThatGet(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def CorrectionDialog(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def RecentBufferCommit(self):
#         '-no docstring-'
#         #return 
#


class IDgnSRWordPrefixEnumW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109017-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Next(self, p0: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def Skip(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Reset(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Clone(self) -> 'IDgnSRWordPrefixEnumW': ...
        def GetCount(self) -> hints.Incomplete: ...


IDgnSRWordPrefixEnumW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Next',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ubyte), 'p1'),
        (['out'], POINTER(c_ulong), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Skip',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reset',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Clone',
        (['out'], POINTER(POINTER(IDgnSRWordPrefixEnumW)), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetCount',
        (['out'], POINTER(c_ulong), 'p0')
    ),
]

################################################################
# code template for IDgnSRWordPrefixEnumW implementation
# class IDgnSRWordPrefixEnumW_Impl(object):
#     def Next(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#
#     def Skip(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Reset(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Clone(self):
#         '-no docstring-'
#         #return p0
#
#     def GetCount(self):
#         '-no docstring-'
#         #return p0
#


class IDgnSRGramDictationW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109015-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def RecentBufferFlush(self) -> hints.Hresult: ...
        def RecentBufferCommit(self) -> hints.Hresult: ...
        def CommittedFlush(self) -> hints.Hresult: ...
        def Words(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


IDgnSRGramDictationW._methods_ = [
    COMMETHOD([], HRESULT, 'RecentBufferFlush'),
    COMMETHOD([], HRESULT, 'RecentBufferCommit'),
    COMMETHOD([], HRESULT, 'CommittedFlush'),
    COMMETHOD(
        [],
        HRESULT,
        'Words',
        (['in'], SDATA, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
]

################################################################
# code template for IDgnSRGramDictationW implementation
# class IDgnSRGramDictationW_Impl(object):
#     def RecentBufferFlush(self):
#         '-no docstring-'
#         #return 
#
#     def RecentBufferCommit(self):
#         '-no docstring-'
#         #return 
#
#     def CommittedFlush(self):
#         '-no docstring-'
#         #return 
#
#     def Words(self, p0, p1):
#         '-no docstring-'
#         #return 
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0024._fields_ = [
    ('dwID', c_ulong),
    ('dwPosn', c_ulong),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0024) == 8, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0024)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0024) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0024)

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011._pack_ = 4

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011._fields_ = [
    ('dwSize', c_ulong),
    ('abWords', POINTER(c_ubyte)),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011) == 12, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011)


class ISRResBasicA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{05EB6C66-DBAB-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def PhraseGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Identify(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def TimeGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def FlagsGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...


ISRResBasicA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'PhraseGet',
        (['in'], c_ulong, 'p0'),
        (['in', 'out'], POINTER(SRPHRASEA), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Identify',
        (
            ['in', 'out'],
            POINTER(GUID),
            'p0',
        )
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TimeGet',
        (['in', 'out'], POINTER(c_ulonglong), 'p0'),
        (['in', 'out'], POINTER(c_ulonglong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'FlagsGet',
        (['in'], c_ulong, 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
]

################################################################
# code template for ISRResBasicA implementation
# class ISRResBasicA_Impl(object):
#     def PhraseGet(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def Identify(self):
#         '-no docstring-'
#         #return p0
#
#     def TimeGet(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def FlagsGet(self, p0):
#         '-no docstring-'
#         #return p1
#


class IDgnSRGramSelectA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10801A-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def WordsSet(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def WordsChange(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def WordsDelete(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def WordsInsert(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def WordsGet(self) -> hints.Incomplete: ...


IDgnSRGramSelectA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'WordsSet',
        (['in'], SDATA, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordsChange',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], SDATA, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordsDelete',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordsInsert',
        (['in'], c_ulong, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordsGet',
        (['out'], POINTER(SDATA), 'p0')
    ),
]

################################################################
# code template for IDgnSRGramSelectA implementation
# class IDgnSRGramSelectA_Impl(object):
#     def WordsSet(self, p0):
#         '-no docstring-'
#         #return 
#
#     def WordsChange(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def WordsDelete(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def WordsInsert(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def WordsGet(self):
#         '-no docstring-'
#         #return p0
#


class IDgnSSvcInterpreterA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108203-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Register(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def CheckScript(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def ExecuteScript(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def ExecuteScriptWithListResults(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete, p5: hints.Incomplete, p6: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


class IDgnSSvcActionNotifySink(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108202-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def PlaybackDone(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def PlaybackAborted(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ExecutionDone(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def ExecutionStatus(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ExecutionAborted(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...


IDgnSSvcInterpreterA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Register',
        (['in'], POINTER(IDgnSSvcActionNotifySink), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'CheckScript',
        (['in'], STRING, 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ExecuteScript',
        (['in'], STRING, 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2'),
        (['in'], STRING, 'p3'),
        (['in'], c_ulong, 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ExecuteScriptWithListResults',
        (['in'], STRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], POINTER(c_ubyte), 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4'),
        (['in'], STRING, 'p5'),
        (['in'], c_ulong, 'p6')
    ),
]

################################################################
# code template for IDgnSSvcInterpreterA implementation
# class IDgnSSvcInterpreterA_Impl(object):
#     def Register(self, p0):
#         '-no docstring-'
#         #return 
#
#     def CheckScript(self, p0):
#         '-no docstring-'
#         #return p1, p2
#
#     def ExecuteScript(self, p0, p3, p4):
#         '-no docstring-'
#         #return p1, p2
#
#     def ExecuteScriptWithListResults(self, p0, p1, p2, p5, p6):
#         '-no docstring-'
#         #return p3, p4
#


class IDgnSRTopic2A(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108021-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def New(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def Select(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def SpeakerCopy(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


IDgnSRTopic2A._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'New',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1'),
        (['in'], STRING, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Select',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SpeakerCopy',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1')
    ),
]

################################################################
# code template for IDgnSRTopic2A implementation
# class IDgnSRTopic2A_Impl(object):
#     def New(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def Select(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def SpeakerCopy(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class IDgnSRGramSelectW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10901A-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def WordsSet(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def WordsChange(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def WordsDelete(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def WordsInsert(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def WordsGet(self) -> hints.Incomplete: ...


IDgnSRGramSelectW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'WordsSet',
        (['in'], SDATA, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordsChange',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], SDATA, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordsDelete',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordsInsert',
        (['in'], c_ulong, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordsGet',
        (['out'], POINTER(SDATA), 'p0')
    ),
]

################################################################
# code template for IDgnSRGramSelectW implementation
# class IDgnSRGramSelectW_Impl(object):
#     def WordsSet(self, p0):
#         '-no docstring-'
#         #return 
#
#     def WordsChange(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def WordsDelete(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def WordsInsert(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def WordsGet(self):
#         '-no docstring-'
#         #return p0
#


class IVoiceDictation0W(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109400-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Register(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete, p5: hints.Incomplete, p6: hints.Incomplete) -> hints.Hresult: ...
        def SiteInfoGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def SiteInfoSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def SessionSerialize(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TopicEnum(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def TopicAddString(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def TopicAddGrammar(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def TopicRemove(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TopicSerialize(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TopicDeserialize(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Activate(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Deactivate(self) -> hints.Hresult: ...
        def Reserved15(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0021(Structure):
    pass


VDSITEINFOW = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0021


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0023(Structure):
    pass


VDCTTOPICW = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0023
LANGUAGEW = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005

IVoiceDictation0W._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Register',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1'),
        (['in'], POINTER(IUnknown), 'p2'),
        (['in'], WSTRING, 'p3'),
        (['in'], POINTER(IUnknown), 'p4'),
        (
            ['in'],
            GUID,
            'p5',
        ),
        (['in'], c_ulong, 'p6')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SiteInfoGet',
        (['in'], WSTRING, 'p0'),
        (['in'], POINTER(VDSITEINFOW), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SiteInfoSet',
        (['in'], WSTRING, 'p0'),
        (['in'], POINTER(VDSITEINFOW), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SessionSerialize',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicEnum',
        (['in', 'out'], POINTER(POINTER(VDCTTOPICW)), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicAddString',
        (['in'], WSTRING, 'p0'),
        (['in'], POINTER(LANGUAGEW), 'p1'),
        (['in'], POINTER(POINTER(c_ushort)), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicAddGrammar',
        (['in'], WSTRING, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicRemove',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicSerialize',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicDeserialize',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Activate',
        (['in'], c_int, 'p0')
    ),
    COMMETHOD([], HRESULT, 'Deactivate'),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved15',
        (['in'], c_ulong, 'p0'),
        (['in'], VDCTBOOKMARK, 'p1')
    ),
]

################################################################
# code template for IVoiceDictation0W implementation
# class IVoiceDictation0W_Impl(object):
#     def Register(self, p0, p1, p2, p3, p4, p5, p6):
#         '-no docstring-'
#         #return 
#
#     def SiteInfoGet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def SiteInfoSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def SessionSerialize(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TopicEnum(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def TopicAddString(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def TopicAddGrammar(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def TopicRemove(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TopicSerialize(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TopicDeserialize(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Activate(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Deactivate(self):
#         '-no docstring-'
#         #return 
#
#     def Reserved15(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class Library(object):
    """Dragon/SAPI Marshal Interfaces (DNS 13)"""
    name = 'DragonProxyStubLib_v13_v14'
    _reg_typelib_ = ('{DD100101-6205-11CF-AE61-0000E8A28647}', 1, 0)


class ILexPronounceA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{2F26B9C0-DB31-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Add(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete, p5: hints.Incomplete) -> hints.Hresult: ...
        def Get(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete, p5: hints.Incomplete, p6: hints.Incomplete, p7: hints.Incomplete, p8: hints.Incomplete, p9: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def Remove(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


ILexPronounceA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Add',
        (['in'], VOICECHARSET, 'p0'),
        (['in'], STRING, 'p1'),
        (['in'], STRING, 'p2'),
        (['in'], VOICEPARTOFSPEECH, 'p3'),
        (['in'], POINTER(c_ubyte), 'p4'),
        (['in'], c_ulong, 'p5')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Get',
        (['in'], VOICECHARSET, 'p0'),
        (['in'], STRING, 'p1'),
        (['in'], c_ushort, 'p2'),
        (['in', 'out'], STRING, 'p3'),
        (['in'], c_ulong, 'p4'),
        (['in', 'out'], POINTER(c_ulong), 'p5'),
        (['in', 'out'], POINTER(VOICEPARTOFSPEECH), 'p6'),
        (['in', 'out'], POINTER(c_ubyte), 'p7'),
        (['in'], c_ulong, 'p8'),
        (['in', 'out'], POINTER(c_ulong), 'p9')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Remove',
        (['in'], STRING, 'p0'),
        (['in'], c_ushort, 'p1')
    ),
]

################################################################
# code template for ILexPronounceA implementation
# class ILexPronounceA_Impl(object):
#     def Add(self, p0, p1, p2, p3, p4, p5):
#         '-no docstring-'
#         #return 
#
#     def Get(self, p0, p1, p2, p4, p8):
#         '-no docstring-'
#         #return p3, p5, p6, p7, p9
#
#     def Remove(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class IDgnErrorW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109005-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def LastErrorGet(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def ErrorMessageGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0016(Structure):
    pass


DGN_ERROR_W = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0016

IDgnErrorW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'LastErrorGet',
        (['in', 'out'], POINTER(DGN_ERROR_W), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ErrorMessageGet',
        (['in', 'out'], POINTER(c_ushort), 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
]

################################################################
# code template for IDgnErrorW implementation
# class IDgnErrorW_Impl(object):
#     def LastErrorGet(self):
#         '-no docstring-'
#         #return p0
#
#     def ErrorMessageGet(self, p1):
#         '-no docstring-'
#         #return p0, p2
#


class ISRGramCFGA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{05EB6C64-DBAB-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def LinkQuery(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...
        def ListAppend(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ListGet(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def ListRemove(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ListSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ListQuery(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...


ISRGramCFGA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'LinkQuery',
        (['in'], STRING, 'p0'),
        (['in', 'out'], POINTER(c_int), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListAppend',
        (['in'], STRING, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListGet',
        (['in'], STRING, 'p0'),
        (['out'], POINTER(SDATA), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListRemove',
        (['in'], STRING, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListSet',
        (['in'], STRING, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListQuery',
        (['in'], STRING, 'p0'),
        (['in', 'out'], POINTER(c_int), 'p1')
    ),
]

################################################################
# code template for ISRGramCFGA implementation
# class ISRGramCFGA_Impl(object):
#     def LinkQuery(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def ListAppend(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ListGet(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def ListRemove(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ListSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ListQuery(self, p0):
#         '-no docstring-'
#         #return p1
#


class IDgnLexWordW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109501-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Add(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...
        def GuessPartOfSpeechandAdd(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> hints.Hresult: ...
        def GuessPartOfSpeech(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Incomplete: ...
        def Get(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def Remove(self, p0: hints.Incomplete) -> hints.Hresult: ...


IDgnLexWordW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Add',
        (['in'], WSTRING, 'p0'),
        (['in'], POINTER(POSINFO), 'p1'),
        (['in'], POINTER(c_ubyte), 'p2'),
        (['in'], c_ulong, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GuessPartOfSpeechandAdd',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1'),
        (['in'], WSTRING, 'p2'),
        (['in'], POINTER(c_ubyte), 'p3'),
        (['in'], c_ulong, 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GuessPartOfSpeech',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1'),
        (['in'], WSTRING, 'p2'),
        (['in', 'out'], POINTER(POSINFO), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Get',
        (['in'], WSTRING, 'p0'),
        (['in', 'out'], POINTER(POSINFO), 'p1'),
        (['in', 'out'], POINTER(c_ubyte), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Remove',
        (['in'], WSTRING, 'p0')
    ),
]

################################################################
# code template for IDgnLexWordW implementation
# class IDgnLexWordW_Impl(object):
#     def Add(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#
#     def GuessPartOfSpeechandAdd(self, p0, p1, p2, p3, p4):
#         '-no docstring-'
#         #return 
#
#     def GuessPartOfSpeech(self, p0, p1, p2):
#         '-no docstring-'
#         #return p3
#
#     def Get(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#
#     def Remove(self, p0):
#         '-no docstring-'
#         #return 
#


class ISRResBasicW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9A5-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def PhraseGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Identify(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def TimeGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def FlagsGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...


ISRResBasicW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'PhraseGet',
        (['in'], c_ulong, 'p0'),
        (['in', 'out'], POINTER(SRPHRASEW), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Identify',
        (
            ['in', 'out'],
            POINTER(GUID),
            'p0',
        )
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TimeGet',
        (['in', 'out'], POINTER(c_ulonglong), 'p0'),
        (['in', 'out'], POINTER(c_ulonglong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'FlagsGet',
        (['in'], c_ulong, 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
]

################################################################
# code template for ISRResBasicW implementation
# class ISRResBasicW_Impl(object):
#     def PhraseGet(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def Identify(self):
#         '-no docstring-'
#         #return p0
#
#     def TimeGet(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def FlagsGet(self, p0):
#         '-no docstring-'
#         #return p1
#


class IDgnSRResGraphW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109020-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def GetWordNode(self, p0: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0014(Structure):
    pass


DGNSRRESWORDNODE = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0014

IDgnSRResGraphW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'GetWordNode',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(DGNSRRESWORDNODE), 'p1'),
        (['out'], POINTER(c_ubyte), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
]

################################################################
# code template for IDgnSRResGraphW implementation
# class IDgnSRResGraphW_Impl(object):
#     def GetWordNode(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#


class IDgnSRLexiconA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108011-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def WordEnum(self) -> 'IDgnSRWordEnumA': ...
        def WordPrefixEnum(self) -> 'IDgnSRWordPrefixEnumA': ...
        def WordTest(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Incomplete: ...
        def WordFromPrefix(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def WordFromPron(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


class IDgnSRWordEnumA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108009-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Next(self, p0: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def Skip(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Reset(self) -> hints.Hresult: ...
        def Clone(self) -> 'IDgnSRWordEnumA': ...
        def GetCount(self) -> hints.Incomplete: ...


class IDgnSRWordPrefixEnumA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108017-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Next(self, p0: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def Skip(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Reset(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Clone(self) -> 'IDgnSRWordPrefixEnumA': ...
        def GetCount(self) -> hints.Incomplete: ...


IDgnSRLexiconA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'WordEnum',
        (['out'], POINTER(POINTER(IDgnSRWordEnumA)), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordPrefixEnum',
        (['out'], POINTER(POINTER(IDgnSRWordPrefixEnumA)), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordTest',
        (['in'], c_ulong, 'p0'),
        (['in'], STRING, 'p1'),
        (['in', 'out'], POINTER(c_int), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordFromPrefix',
        (['in'], STRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], STRING, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordFromPron',
        (['in'], STRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], STRING, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
]

################################################################
# code template for IDgnSRLexiconA implementation
# class IDgnSRLexiconA_Impl(object):
#     def WordEnum(self):
#         '-no docstring-'
#         #return p0
#
#     def WordPrefixEnum(self):
#         '-no docstring-'
#         #return p0
#
#     def WordTest(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def WordFromPrefix(self, p0, p1, p2):
#         '-no docstring-'
#         #return p3, p4
#
#     def WordFromPron(self, p0, p1, p2):
#         '-no docstring-'
#         #return p3, p4
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0021._fields_ = [
    ('dwAutoGainEnable', c_ulong),
    ('dwAwakeState', c_ulong),
    ('dwThreshold', c_ulong),
    ('dwDevice', c_ulong),
    ('dwEnable', c_ulong),
    ('szMicrophone', c_ushort * 32),
    ('szSpeaker', c_ushort * 32),
    ('gModeID', GUID),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0021) == 164, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0021)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0021) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0021)

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010._pack_ = 4

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010._fields_ = [
    ('dwSize', c_ulong),
    ('abWords', POINTER(c_ubyte)),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010) == 12, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010)


class IDgnExtModSupStringsA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108601-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def GetSpecialString(self, p0: hints.Incomplete, p1: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def SetSpecialString(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def GetResourceString(self, p0: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def GetStringParameter(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...
        def GetWindowModuleFileName(self, p0: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


IDgnExtModSupStringsA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'GetSpecialString',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['out'], STRING, 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SetSpecialString',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], STRING, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetResourceString',
        (['in'], c_ulong, 'p0'),
        (['out'], STRING, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetStringParameter',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetWindowModuleFileName',
        (['in'], c_ulong, 'p0'),
        (['out'], STRING, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], POINTER(c_ulong), 'p3')
    ),
]

################################################################
# code template for IDgnExtModSupStringsA implementation
# class IDgnExtModSupStringsA_Impl(object):
#     def GetSpecialString(self, p0, p1, p3):
#         '-no docstring-'
#         #return p2, p4
#
#     def SetSpecialString(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def GetResourceString(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def GetStringParameter(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def GetWindowModuleFileName(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#

IDgnSSvcActionNotifySink._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'PlaybackDone',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PlaybackAborted',
        (['in'], c_ulong, 'p0'),
        (['in'], HRESULT, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ExecutionDone',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ExecutionStatus',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ExecutionAborted',
        (['in'], c_ulong, 'p0'),
        (['in'], HRESULT, 'p1'),
        (['in'], c_ulong, 'p2')
    ),
]

################################################################
# code template for IDgnSSvcActionNotifySink implementation
# class IDgnSSvcActionNotifySink_Impl(object):
#     def PlaybackDone(self, p0):
#         '-no docstring-'
#         #return 
#
#     def PlaybackAborted(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ExecutionDone(self, p0):
#         '-no docstring-'
#         #return 
#
#     def ExecutionStatus(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ExecutionAborted(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#


class IVDct0TextW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10940A-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Lock(self) -> hints.Hresult: ...
        def UnLock(self) -> hints.Hresult: ...
        def TextGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...
        def TextSet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...
        def TextMove(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...
        def TextRemove(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def TextSelSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def TextSelGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def GetChanges(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def BookmarkAdd(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def BookmarkRemove(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def BookmarkMove(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def BookmarkQuery(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def BookmarkEnum(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Hint(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Words(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def ResultsGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def AutoLockSet(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def AutoLockGet(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def Reserved22(self, p0: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Reserved23(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...


IVDct0TextW._methods_ = [
    COMMETHOD([], HRESULT, 'Lock'),
    COMMETHOD([], HRESULT, 'UnLock'),
    COMMETHOD(
        [],
        HRESULT,
        'TextGet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['out'], POINTER(SDATA), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextSet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], WSTRING, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextMove',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextRemove',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextSelSet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TextSelGet',
        (['in', 'out'], POINTER(c_ulong), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetChanges',
        (['in', 'out'], POINTER(c_ulong), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkAdd',
        (['in'], POINTER(VDCTBOOKMARK), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkRemove',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkMove',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkQuery',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(VDCTBOOKMARK), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookmarkEnum',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(POINTER(VDCTBOOKMARK)), 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Hint',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Words',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ResultsGet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3'),
        (['out'], POINTER(POINTER(IUnknown)), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'AutoLockSet',
        (['in'], c_int, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'AutoLockGet',
        (['in', 'out'], POINTER(c_int), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved22',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ushort), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved23',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], WSTRING, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
]

################################################################
# code template for IVDct0TextW implementation
# class IVDct0TextW_Impl(object):
#     def Lock(self):
#         '-no docstring-'
#         #return 
#
#     def UnLock(self):
#         '-no docstring-'
#         #return 
#
#     def TextGet(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def TextSet(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#
#     def TextMove(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#
#     def TextRemove(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def TextSelSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def TextSelGet(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def GetChanges(self):
#         '-no docstring-'
#         #return p0, p1, p2, p3
#
#     def BookmarkAdd(self, p0):
#         '-no docstring-'
#         #return 
#
#     def BookmarkRemove(self, p0):
#         '-no docstring-'
#         #return 
#
#     def BookmarkMove(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def BookmarkQuery(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def BookmarkEnum(self, p0, p1):
#         '-no docstring-'
#         #return p2, p3
#
#     def Hint(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Words(self, p0):
#         '-no docstring-'
#         #return 
#
#     def ResultsGet(self, p0, p1):
#         '-no docstring-'
#         #return p2, p3, p4
#
#     def AutoLockSet(self, p0):
#         '-no docstring-'
#         #return 
#
#     def AutoLockGet(self):
#         '-no docstring-'
#         #return p0
#
#     def Reserved22(self, p0):
#         '-no docstring-'
#         #return p1, p2
#
#     def Reserved23(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0016._fields_ = [
    ('m_nCode', c_int),
    ('m_szParms', c_ushort * 300),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0016) == 604, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0016)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0016) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0016)

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0014._fields_ = [
    ('dwNextWordNode', c_ulong),
    ('dwUpAlternateWordNode', c_ulong),
    ('dwDownAlternateWordNode', c_ulong),
    ('dwPreviousWordNode', c_ulong),
    ('dwPhonemeNode', c_ulong),
    ('qwStartTime', c_ulonglong),
    ('qwEndTime', c_ulonglong),
    ('dwWordScore', c_ulong),
    ('wVolume', c_ushort),
    ('wPitch', c_ushort),
    ('pos', __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0002),
    ('dwCFGParse', c_ulong),
    ('dwCue', c_ulong),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0014) == 64, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0014)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0014) == 8, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0014)


class ISRSpeakerA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9AF-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Delete(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Enum(self, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Merge(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def New(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Query(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Read(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Revert(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Select(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Write(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...


ISRSpeakerA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Delete',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Enum',
        (['out'], POINTER(STRING), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Merge',
        (['in'], STRING, 'p0'),
        (['in'], POINTER(c_ubyte), 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'New',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Query',
        (['in', 'out'], STRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Read',
        (['in'], STRING, 'p0'),
        (['in', 'out'], POINTER(POINTER(c_ubyte)), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Revert',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Select',
        (['in'], STRING, 'p0'),
        (['in'], c_int, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Write',
        (['in'], STRING, 'p0'),
        (['in'], POINTER(c_ubyte), 'p1'),
        (['in'], c_ulong, 'p2')
    ),
]

################################################################
# code template for ISRSpeakerA implementation
# class ISRSpeakerA_Impl(object):
#     def Delete(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Enum(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def Merge(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def New(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Query(self, p1):
#         '-no docstring-'
#         #return p0, p2
#
#     def Read(self, p0):
#         '-no docstring-'
#         #return p1, p2
#
#     def Revert(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Select(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Write(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#


class IDgnSRLexiconW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109011-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def WordEnum(self) -> 'IDgnSRWordEnumW': ...
        def WordPrefixEnum(self) -> 'IDgnSRWordPrefixEnumW': ...
        def WordTest(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Incomplete: ...
        def WordFromPrefix(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def WordFromPron(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


IDgnSRLexiconW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'WordEnum',
        (['out'], POINTER(POINTER(IDgnSRWordEnumW)), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordPrefixEnum',
        (['out'], POINTER(POINTER(IDgnSRWordPrefixEnumW)), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordTest',
        (['in'], c_ulong, 'p0'),
        (['in'], WSTRING, 'p1'),
        (['in', 'out'], POINTER(c_int), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordFromPrefix',
        (['in'], WSTRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], WSTRING, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WordFromPron',
        (['in'], WSTRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], WSTRING, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
]

################################################################
# code template for IDgnSRLexiconW implementation
# class IDgnSRLexiconW_Impl(object):
#     def WordEnum(self):
#         '-no docstring-'
#         #return p0
#
#     def WordPrefixEnum(self):
#         '-no docstring-'
#         #return p0
#
#     def WordTest(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def WordFromPrefix(self, p0, p1, p2):
#         '-no docstring-'
#         #return p3, p4
#
#     def WordFromPron(self, p0, p1, p2):
#         '-no docstring-'
#         #return p3, p4
#


class IDgnSRResSelect(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10801B-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def GetInfo(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...


IDgnSRResSelect._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'GetInfo',
        (
            ['in'],
            GUID,
            'p0',
        ),
        (['in'], c_ulong, 'p1'),
        (['out'], POINTER(c_ulong), 'p2'),
        (['out'], POINTER(c_ulong), 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
]

################################################################
# code template for IDgnSRResSelect implementation
# class IDgnSRResSelect_Impl(object):
#     def GetInfo(self, p0, p1):
#         '-no docstring-'
#         #return p2, p3, p4
#


class ISRGramCFGW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{ECC0B180-C743-11CD-80E5-00AA003E4B50}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def LinkQuery(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...
        def ListAppend(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ListGet(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def ListRemove(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ListSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ListQuery(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...


ISRGramCFGW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'LinkQuery',
        (['in'], WSTRING, 'p0'),
        (['in', 'out'], POINTER(c_int), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListAppend',
        (['in'], WSTRING, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListGet',
        (['in'], WSTRING, 'p0'),
        (['out'], POINTER(SDATA), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListRemove',
        (['in'], WSTRING, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListSet',
        (['in'], WSTRING, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ListQuery',
        (['in'], WSTRING, 'p0'),
        (['in', 'out'], POINTER(c_int), 'p1')
    ),
]

################################################################
# code template for ISRGramCFGW implementation
# class ISRGramCFGW_Impl(object):
#     def LinkQuery(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def ListAppend(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ListGet(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def ListRemove(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ListSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ListQuery(self, p0):
#         '-no docstring-'
#         #return p1
#


class ISRCentralW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{B9BD3860-44DB-101B-90A8-00AA003E4B50}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def ModeGet(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def GrammarLoad(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Incomplete: ...
        def Pause(self) -> hints.Hresult: ...
        def PosnGet(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def Resume(self) -> hints.Hresult: ...
        def ToFileTime(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...
        def Register(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Incomplete: ...
        def UnRegister(self, p0: hints.Incomplete) -> hints.Hresult: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0007(Structure):
    pass


SRMODEINFOW = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0007


class ISRGramNotifySinkW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{F106BFA0-C743-11CD-80E5-00AA003E4B50}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def BookMark(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Paused(self) -> hints.Hresult: ...
        def PhraseFinish(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> hints.Hresult: ...
        def PhraseHypothesis(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> hints.Hresult: ...
        def PhraseStart(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def ReEvaluate(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Training(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def UnArchive(self, p0: hints.Incomplete) -> hints.Hresult: ...


class ISRNotifySink(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9B0-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def AttribChanged(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Interference(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def Sound(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def UtteranceBegin(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def UtteranceEnd(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def VUMeter(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


ISRCentralW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'ModeGet',
        (['in', 'out'], POINTER(SRMODEINFOW), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GrammarLoad',
        (['in'], SRGRMFMT, 'p0'),
        (['in'], SDATA, 'p1'),
        (['in'], POINTER(ISRGramNotifySinkW), 'p2'),
        (
            ['in'],
            GUID,
            'p3',
        ),
        (['out'], POINTER(POINTER(IUnknown)), 'p4')
    ),
    COMMETHOD([], HRESULT, 'Pause'),
    COMMETHOD(
        [],
        HRESULT,
        'PosnGet',
        (['in', 'out'], POINTER(c_ulonglong), 'p0')
    ),
    COMMETHOD([], HRESULT, 'Resume'),
    COMMETHOD(
        [],
        HRESULT,
        'ToFileTime',
        (['in'], POINTER(c_ulonglong), 'p0'),
        (['in', 'out'], POINTER(_FILETIME), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Register',
        (['in'], POINTER(ISRNotifySink), 'p0'),
        (
            ['in'],
            GUID,
            'p1',
        ),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'UnRegister',
        (['in'], c_ulong, 'p0')
    ),
]

################################################################
# code template for ISRCentralW implementation
# class ISRCentralW_Impl(object):
#     def ModeGet(self):
#         '-no docstring-'
#         #return p0
#
#     def GrammarLoad(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return p4
#
#     def Pause(self):
#         '-no docstring-'
#         #return 
#
#     def PosnGet(self):
#         '-no docstring-'
#         #return p0
#
#     def Resume(self):
#         '-no docstring-'
#         #return 
#
#     def ToFileTime(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def Register(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def UnRegister(self, p0):
#         '-no docstring-'
#         #return 
#


class ISRResCorrectionA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{05EB6C67-DBAB-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Correction(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Validate(self, p0: hints.Incomplete) -> hints.Hresult: ...


ISRResCorrectionA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Correction',
        (['in'], POINTER(SRPHRASEA), 'p0'),
        (['in'], c_ushort, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Validate',
        (['in'], c_ushort, 'p0')
    ),
]

################################################################
# code template for ISRResCorrectionA implementation
# class ISRResCorrectionA_Impl(object):
#     def Correction(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Validate(self, p0):
#         '-no docstring-'
#         #return 
#


class IDgnSSvcInterpreterW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109203-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Register(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def CheckScript(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def ExecuteScript(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def ExecuteScriptWithListResults(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete, p5: hints.Incomplete, p6: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


IDgnSSvcInterpreterW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Register',
        (['in'], POINTER(IDgnSSvcActionNotifySink), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'CheckScript',
        (['in'], WSTRING, 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ExecuteScript',
        (['in'], WSTRING, 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2'),
        (['in'], WSTRING, 'p3'),
        (['in'], c_ulong, 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ExecuteScriptWithListResults',
        (['in'], WSTRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], POINTER(c_ubyte), 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4'),
        (['in'], WSTRING, 'p5'),
        (['in'], c_ulong, 'p6')
    ),
]

################################################################
# code template for IDgnSSvcInterpreterW implementation
# class IDgnSSvcInterpreterW_Impl(object):
#     def Register(self, p0):
#         '-no docstring-'
#         #return 
#
#     def CheckScript(self, p0):
#         '-no docstring-'
#         #return p1, p2
#
#     def ExecuteScript(self, p0, p3, p4):
#         '-no docstring-'
#         #return p1, p2
#
#     def ExecuteScriptWithListResults(self, p0, p1, p2, p5, p6):
#         '-no docstring-'
#         #return p3, p4
#


class IDgnSRAudioFileSourceA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108008-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def FileNameSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def EnableSet(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def FileClose(self) -> hints.Hresult: ...


IDgnSRAudioFileSourceA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'FileNameSet',
        (['in'], c_ulong, 'p0'),
        (['in'], STRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'EnableSet',
        (['in'], c_int, 'p0')
    ),
    COMMETHOD([], HRESULT, 'FileClose'),
]

################################################################
# code template for IDgnSRAudioFileSourceA implementation
# class IDgnSRAudioFileSourceA_Impl(object):
#     def FileNameSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def EnableSet(self, p0):
#         '-no docstring-'
#         #return 
#
#     def FileClose(self):
#         '-no docstring-'
#         #return 
#

IDgnSRWordEnumA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Next',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ubyte), 'p1'),
        (['out'], POINTER(c_ulong), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Skip',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD(
        [],
        HRESULT,
        'Clone',
        (['out'], POINTER(POINTER(IDgnSRWordEnumA)), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetCount',
        (['out'], POINTER(c_ulong), 'p0')
    ),
]

################################################################
# code template for IDgnSRWordEnumA implementation
# class IDgnSRWordEnumA_Impl(object):
#     def Next(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#
#     def Skip(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Reset(self):
#         '-no docstring-'
#         #return 
#
#     def Clone(self):
#         '-no docstring-'
#         #return p0
#
#     def GetCount(self):
#         '-no docstring-'
#         #return p0
#


class IDgnSREngineControlW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109000-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def GetVersion(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def GetMicState(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def SetMicState(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def SaveSpeaker(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def GetChangedInfo(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Resume(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def RecognitionMimic(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def Preinitialize(self) -> hints.Hresult: ...
        def SpeakerRename(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


IDgnSREngineControlW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'GetVersion',
        (['in', 'out'], POINTER(c_ushort), 'p0'),
        (['in', 'out'], POINTER(c_ushort), 'p1'),
        (['in', 'out'], POINTER(c_ushort), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetMicState',
        (['in', 'out'], POINTER(c_ushort), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SetMicState',
        (['in'], c_ushort, 'p0'),
        (['in'], c_int, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SaveSpeaker',
        (['in'], c_int, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetChangedInfo',
        (['in', 'out'], POINTER(c_int), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Resume',
        (['in'], c_ulonglong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'RecognitionMimic',
        (['in'], c_ulong, 'p0'),
        (['in'], SDATA, 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD([], HRESULT, 'Preinitialize'),
    COMMETHOD(
        [],
        HRESULT,
        'SpeakerRename',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1')
    ),
]

################################################################
# code template for IDgnSREngineControlW implementation
# class IDgnSREngineControlW_Impl(object):
#     def GetVersion(self):
#         '-no docstring-'
#         #return p0, p1, p2
#
#     def GetMicState(self):
#         '-no docstring-'
#         #return p0
#
#     def SetMicState(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def SaveSpeaker(self, p0):
#         '-no docstring-'
#         #return 
#
#     def GetChangedInfo(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def Resume(self, p0):
#         '-no docstring-'
#         #return 
#
#     def RecognitionMimic(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def Preinitialize(self):
#         '-no docstring-'
#         #return 
#
#     def SpeakerRename(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class IDgnSRAudioFileSourceW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109008-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def FileNameSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def EnableSet(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def FileClose(self) -> hints.Hresult: ...


IDgnSRAudioFileSourceW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'FileNameSet',
        (['in'], c_ulong, 'p0'),
        (['in'], WSTRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'EnableSet',
        (['in'], c_int, 'p0')
    ),
    COMMETHOD([], HRESULT, 'FileClose'),
]

################################################################
# code template for IDgnSRAudioFileSourceW implementation
# class IDgnSRAudioFileSourceW_Impl(object):
#     def FileNameSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def EnableSet(self, p0):
#         '-no docstring-'
#         #return 
#
#     def FileClose(self):
#         '-no docstring-'
#         #return 
#


class ILexPronounceW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9A2-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Add(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete, p5: hints.Incomplete) -> hints.Hresult: ...
        def Get(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete, p5: hints.Incomplete, p6: hints.Incomplete, p7: hints.Incomplete, p8: hints.Incomplete, p9: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def Remove(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


ILexPronounceW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Add',
        (['in'], VOICECHARSET, 'p0'),
        (['in'], WSTRING, 'p1'),
        (['in'], WSTRING, 'p2'),
        (['in'], VOICEPARTOFSPEECH, 'p3'),
        (['in'], POINTER(c_ubyte), 'p4'),
        (['in'], c_ulong, 'p5')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Get',
        (['in'], VOICECHARSET, 'p0'),
        (['in'], WSTRING, 'p1'),
        (['in'], c_ushort, 'p2'),
        (['in', 'out'], POINTER(c_ushort), 'p3'),
        (['in'], c_ulong, 'p4'),
        (['in', 'out'], POINTER(c_ulong), 'p5'),
        (['in', 'out'], POINTER(VOICEPARTOFSPEECH), 'p6'),
        (['in', 'out'], POINTER(c_ubyte), 'p7'),
        (['in'], c_ulong, 'p8'),
        (['in', 'out'], POINTER(c_ulong), 'p9')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Remove',
        (['in'], WSTRING, 'p0'),
        (['in'], c_ushort, 'p1')
    ),
]

################################################################
# code template for ILexPronounceW implementation
# class ILexPronounceW_Impl(object):
#     def Add(self, p0, p1, p2, p3, p4, p5):
#         '-no docstring-'
#         #return 
#
#     def Get(self, p0, p1, p2, p4, p8):
#         '-no docstring-'
#         #return p3, p5, p6, p7, p9
#
#     def Remove(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class ISRGramCommonA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{05EB6C63-DBAB-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Activate(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def Archive(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def BookMark(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Deactivate(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def DeteriorationGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def DeteriorationSet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def TrainDlg(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def TrainPhrase(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def TrainQuery(self, p0: hints.Incomplete) -> hints.Incomplete: ...


ISRGramCommonA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Activate',
        (['in'], SRGRMFMT, 'p0'),
        (['in'], c_int, 'p1'),
        (['in'], STRING, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Archive',
        (['in'], c_int, 'p0'),
        (['in', 'out'], POINTER(c_ubyte), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookMark',
        (['in'], c_ulonglong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Deactivate',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'DeteriorationGet',
        (['in', 'out'], POINTER(c_ulong), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'DeteriorationSet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TrainDlg',
        (['in'], c_ulong, 'p0'),
        (['in'], STRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TrainPhrase',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(SDATA), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TrainQuery',
        (['in', 'out'], POINTER(c_ulong), 'p0')
    ),
]

################################################################
# code template for ISRGramCommonA implementation
# class ISRGramCommonA_Impl(object):
#     def Activate(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def Archive(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def BookMark(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Deactivate(self, p0):
#         '-no docstring-'
#         #return 
#
#     def DeteriorationGet(self):
#         '-no docstring-'
#         #return p0, p1, p2
#
#     def DeteriorationSet(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def TrainDlg(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def TrainPhrase(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def TrainQuery(self):
#         '-no docstring-'
#         #return p0
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0023._fields_ = [
    ('szTopic', c_ushort * 32),
    ('language', __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0023) == 194, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0023)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0023) == 2, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0023)


class IDgnSREngineControlA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108000-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def GetVersion(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def GetMicState(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def SetMicState(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def SaveSpeaker(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def GetChangedInfo(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Resume(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def RecognitionMimic(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def Preinitialize(self) -> hints.Hresult: ...
        def SpeakerRename(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


IDgnSREngineControlA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'GetVersion',
        (['in', 'out'], POINTER(c_ushort), 'p0'),
        (['in', 'out'], POINTER(c_ushort), 'p1'),
        (['in', 'out'], POINTER(c_ushort), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetMicState',
        (['in', 'out'], POINTER(c_ushort), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SetMicState',
        (['in'], c_ushort, 'p0'),
        (['in'], c_int, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SaveSpeaker',
        (['in'], c_int, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetChangedInfo',
        (['in', 'out'], POINTER(c_int), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Resume',
        (['in'], c_ulonglong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'RecognitionMimic',
        (['in'], c_ulong, 'p0'),
        (['in'], SDATA, 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD([], HRESULT, 'Preinitialize'),
    COMMETHOD(
        [],
        HRESULT,
        'SpeakerRename',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1')
    ),
]

################################################################
# code template for IDgnSREngineControlA implementation
# class IDgnSREngineControlA_Impl(object):
#     def GetVersion(self):
#         '-no docstring-'
#         #return p0, p1, p2
#
#     def GetMicState(self):
#         '-no docstring-'
#         #return p0
#
#     def SetMicState(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def SaveSpeaker(self, p0):
#         '-no docstring-'
#         #return 
#
#     def GetChangedInfo(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def Resume(self, p0):
#         '-no docstring-'
#         #return 
#
#     def RecognitionMimic(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def Preinitialize(self):
#         '-no docstring-'
#         #return 
#
#     def SpeakerRename(self, p0, p1):
#         '-no docstring-'
#         #return 
#

ISRNotifySink._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'AttribChanged',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Interference',
        (['in'], c_ulonglong, 'p0'),
        (['in'], c_ulonglong, 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Sound',
        (['in'], c_ulonglong, 'p0'),
        (['in'], c_ulonglong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'UtteranceBegin',
        (['in'], c_ulonglong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'UtteranceEnd',
        (['in'], c_ulonglong, 'p0'),
        (['in'], c_ulonglong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'VUMeter',
        (['in'], c_ulonglong, 'p0'),
        (['in'], c_ushort, 'p1')
    ),
]

################################################################
# code template for ISRNotifySink implementation
# class ISRNotifySink_Impl(object):
#     def AttribChanged(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Interference(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def Sound(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def UtteranceBegin(self, p0):
#         '-no docstring-'
#         #return 
#
#     def UtteranceEnd(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def VUMeter(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class ISRResCorrectionW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9A8-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Correction(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Validate(self, p0: hints.Incomplete) -> hints.Hresult: ...


ISRResCorrectionW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Correction',
        (['in'], POINTER(SRPHRASEW), 'p0'),
        (['in'], c_ushort, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Validate',
        (['in'], c_ushort, 'p0')
    ),
]

################################################################
# code template for ISRResCorrectionW implementation
# class ISRResCorrectionW_Impl(object):
#     def Correction(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Validate(self, p0):
#         '-no docstring-'
#         #return 
#


class IDgnExtModSupStringsW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109601-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def GetSpecialString(self, p0: hints.Incomplete, p1: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def SetSpecialString(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def GetResourceString(self, p0: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def GetStringParameter(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...
        def GetWindowModuleFileName(self, p0: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


IDgnExtModSupStringsW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'GetSpecialString',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['out'], POINTER(c_ushort), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SetSpecialString',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], WSTRING, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetResourceString',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ushort), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetStringParameter',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetWindowModuleFileName',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ushort), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], POINTER(c_ulong), 'p3')
    ),
]

################################################################
# code template for IDgnExtModSupStringsW implementation
# class IDgnExtModSupStringsW_Impl(object):
#     def GetSpecialString(self, p0, p1, p3):
#         '-no docstring-'
#         #return p2, p4
#
#     def SetSpecialString(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def GetResourceString(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def GetStringParameter(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def GetWindowModuleFileName(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#


class IDgnSSvcOutputEventA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108201-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Register(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def PlayString(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Incomplete: ...
        def NameFromKey(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p5: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def PlayEvents(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...
        def Reserved7(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Incomplete: ...
        def Reserved8(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0015(Structure):
    pass


HOOK_EVENTMSG = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0015

IDgnSSvcOutputEventA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Register',
        (['in'], POINTER(IDgnSSvcActionNotifySink), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PlayString',
        (['in'], STRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'NameFromKey',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], STRING, 'p4'),
        (['in', 'out'], POINTER(c_ulong), 'p5')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PlayEvents',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(HOOK_EVENTMSG), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved7',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved8',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(HOOK_EVENTMSG), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
]

################################################################
# code template for IDgnSSvcOutputEventA implementation
# class IDgnSSvcOutputEventA_Impl(object):
#     def Register(self, p0):
#         '-no docstring-'
#         #return 
#
#     def PlayString(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return p4
#
#     def NameFromKey(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return p4, p5
#
#     def PlayEvents(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#
#     def Reserved7(self, p0, p1, p2):
#         '-no docstring-'
#         #return p3
#
#     def Reserved8(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#


class IDgnGetSinkFlags(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108010-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def SinkFlagsGet(self, p0: hints.Incomplete) -> hints.Incomplete: ...


IDgnGetSinkFlags._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'SinkFlagsGet',
        (['in', 'out'], POINTER(c_ulong), 'p0')
    ),
]

################################################################
# code template for IDgnGetSinkFlags implementation
# class IDgnGetSinkFlags_Impl(object):
#     def SinkFlagsGet(self):
#         '-no docstring-'
#         #return p0
#


class IDgnSREngineNotifySinkW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109001-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def AttribChanged2(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Paused(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def MimicDone(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ErrorHappened(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Progress(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


IDgnSREngineNotifySinkW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'AttribChanged2',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Paused',
        (['in'], c_ulonglong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'MimicDone',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(IUnknown), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ErrorHappened',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Progress',
        (['in'], c_int, 'p0'),
        (['in'], WSTRING, 'p1')
    ),
]

################################################################
# code template for IDgnSREngineNotifySinkW implementation
# class IDgnSREngineNotifySinkW_Impl(object):
#     def AttribChanged2(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Paused(self, p0):
#         '-no docstring-'
#         #return 
#
#     def MimicDone(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ErrorHappened(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Progress(self, p0, p1):
#         '-no docstring-'
#         #return 
#


class ISRResGraphA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{05EB6C68-DBAB-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def BestPathPhoneme(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def BestPathWord(self, p0: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def GetPhonemeNode(self, p0: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def GetWordNode(self, p0: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def PathScorePhoneme(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Incomplete: ...
        def PathScoreWord(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Incomplete: ...


ISRResGraphA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'BestPathPhoneme',
        (['in'], c_ulong, 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BestPathWord',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ulong), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetPhonemeNode',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(SRRESPHONEMENODE), 'p1'),
        (['in', 'out'], POINTER(c_ushort), 'p2'),
        (['in', 'out'], STRING, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetWordNode',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(SRRESWORDNODE), 'p1'),
        (['out'], POINTER(c_ubyte), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PathScorePhoneme',
        (['in'], POINTER(c_ulong), 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_int), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PathScoreWord',
        (['in'], POINTER(c_ulong), 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_int), 'p2')
    ),
]

################################################################
# code template for ISRResGraphA implementation
# class ISRResGraphA_Impl(object):
#     def BestPathPhoneme(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def BestPathWord(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def GetPhonemeNode(self, p0):
#         '-no docstring-'
#         #return p1, p2, p3
#
#     def GetWordNode(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#
#     def PathScorePhoneme(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def PathScoreWord(self, p0, p1):
#         '-no docstring-'
#         #return p2
#

IDgnSRWordPrefixEnumA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Next',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(c_ubyte), 'p1'),
        (['out'], POINTER(c_ulong), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Skip',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Reset',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Clone',
        (['out'], POINTER(POINTER(IDgnSRWordPrefixEnumA)), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetCount',
        (['out'], POINTER(c_ulong), 'p0')
    ),
]

################################################################
# code template for IDgnSRWordPrefixEnumA implementation
# class IDgnSRWordPrefixEnumA_Impl(object):
#     def Next(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#
#     def Skip(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Reset(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Clone(self):
#         '-no docstring-'
#         #return p0
#
#     def GetCount(self):
#         '-no docstring-'
#         #return p0
#


class ISRCentralA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{2F26B9C2-DB31-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def ModeGet(self) -> hints.Incomplete: ...
        def GrammarLoad(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Incomplete: ...
        def Pause(self) -> hints.Hresult: ...
        def PosnGet(self) -> hints.Incomplete: ...
        def Resume(self) -> hints.Hresult: ...
        def ToFileTime(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def Register(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Incomplete: ...
        def UnRegister(self, p0: hints.Incomplete) -> hints.Hresult: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0006(Structure):
    pass


SRMODEINFOA = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0006

ISRCentralA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'ModeGet',
        (['out'], POINTER(SRMODEINFOA), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GrammarLoad',
        (['in'], SRGRMFMT, 'p0'),
        (['in'], SDATA, 'p1'),
        (['in'], POINTER(ISRGramNotifySinkA), 'p2'),
        (
            ['in'],
            GUID,
            'p3',
        ),
        (['out'], POINTER(POINTER(IUnknown)), 'p4')
    ),
    COMMETHOD([], HRESULT, 'Pause'),
    COMMETHOD(
        [],
        HRESULT,
        'PosnGet',
        (['out'], POINTER(c_ulonglong), 'p0')
    ),
    COMMETHOD([], HRESULT, 'Resume'),
    COMMETHOD(
        [],
        HRESULT,
        'ToFileTime',
        (['in'], POINTER(c_ulonglong), 'p0'),
        (['out'], POINTER(_FILETIME), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Register',
        (['in'], POINTER(ISRNotifySink), 'p0'),
        (
            ['in'],
            GUID,
            'p1',
        ),
        (['out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'UnRegister',
        (['in'], c_ulong, 'p0')
    ),
]

################################################################
# code template for ISRCentralA implementation
# class ISRCentralA_Impl(object):
#     def ModeGet(self):
#         '-no docstring-'
#         #return p0
#
#     def GrammarLoad(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return p4
#
#     def Pause(self):
#         '-no docstring-'
#         #return 
#
#     def PosnGet(self):
#         '-no docstring-'
#         #return p0
#
#     def Resume(self):
#         '-no docstring-'
#         #return 
#
#     def ToFileTime(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def Register(self, p0, p1):
#         '-no docstring-'
#         #return p2
#
#     def UnRegister(self, p0):
#         '-no docstring-'
#         #return 
#


class IDgnSRGramCommon(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108006-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def SpecialGrammar(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Identify(self) -> hints.Incomplete: ...
        def Reserved5(self) -> hints.Hresult: ...
        def Reserved6(self) -> hints.Hresult: ...


IDgnSRGramCommon._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'SpecialGrammar',
        (['in'], c_int, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Identify',
        (
            ['out'],
            POINTER(GUID),
            'p0',
        )
    ),
    COMMETHOD([], HRESULT, 'Reserved5'),
    COMMETHOD([], HRESULT, 'Reserved6'),
]

################################################################
# code template for IDgnSRGramCommon implementation
# class IDgnSRGramCommon_Impl(object):
#     def SpecialGrammar(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Identify(self):
#         '-no docstring-'
#         #return p0
#
#     def Reserved5(self):
#         '-no docstring-'
#         #return 
#
#     def Reserved6(self):
#         '-no docstring-'
#         #return 
#


class IDgnSRSpeakerA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10801C-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def EnumBaseModels(self, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def New(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def GetSpeakerDirectory(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


IDgnSRSpeakerA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'EnumBaseModels',
        (['out'], POINTER(STRING), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'New',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetSpeakerDirectory',
        (['in'], STRING, 'p0'),
        (['in', 'out'], STRING, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
]

################################################################
# code template for IDgnSRSpeakerA implementation
# class IDgnSRSpeakerA_Impl(object):
#     def EnumBaseModels(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def New(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def GetSpeakerDirectory(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#


class ISRSpeakerW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{090CD9AE-DA1A-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Delete(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Enum(self, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Merge(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def New(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Query(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Read(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def Revert(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Select(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Write(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...


ISRSpeakerW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Delete',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Enum',
        (['out'], POINTER(POINTER(c_ushort)), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Merge',
        (['in'], WSTRING, 'p0'),
        (['in'], POINTER(c_ubyte), 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'New',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Query',
        (['in', 'out'], POINTER(c_ushort), 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Read',
        (['in'], WSTRING, 'p0'),
        (['in', 'out'], POINTER(POINTER(c_ubyte)), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Revert',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Select',
        (['in'], WSTRING, 'p0'),
        (['in'], c_int, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Write',
        (['in'], WSTRING, 'p0'),
        (['in'], POINTER(c_ubyte), 'p1'),
        (['in'], c_ulong, 'p2')
    ),
]

################################################################
# code template for ISRSpeakerW implementation
# class ISRSpeakerW_Impl(object):
#     def Delete(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Enum(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def Merge(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def New(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Query(self, p1):
#         '-no docstring-'
#         #return p0, p2
#
#     def Read(self, p0):
#         '-no docstring-'
#         #return p1, p2
#
#     def Revert(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Select(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Write(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#


class ISRGramCommonW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{E8C3E160-C743-11CD-80E5-00AA003E4B50}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Activate(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def Archive(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def BookMark(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Deactivate(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def DeteriorationGet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def DeteriorationSet(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def TrainDlg(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def TrainPhrase(self, p0: hints.Incomplete) -> hints.Incomplete: ...
        def TrainQuery(self, p0: hints.Incomplete) -> hints.Incomplete: ...


ISRGramCommonW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Activate',
        (['in'], SRGRMFMT, 'p0'),
        (['in'], c_int, 'p1'),
        (['in'], WSTRING, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Archive',
        (['in'], c_int, 'p0'),
        (['in', 'out'], POINTER(c_ubyte), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'BookMark',
        (['in'], c_ulonglong, 'p0'),
        (['in'], c_ulong, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Deactivate',
        (['in'], WSTRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'DeteriorationGet',
        (['in', 'out'], POINTER(c_ulong), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1'),
        (['in', 'out'], POINTER(c_ulong), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'DeteriorationSet',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TrainDlg',
        (['in'], c_ulong, 'p0'),
        (['in'], WSTRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TrainPhrase',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(SDATA), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TrainQuery',
        (['in', 'out'], POINTER(c_ulong), 'p0')
    ),
]

################################################################
# code template for ISRGramCommonW implementation
# class ISRGramCommonW_Impl(object):
#     def Activate(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def Archive(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#
#     def BookMark(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Deactivate(self, p0):
#         '-no docstring-'
#         #return 
#
#     def DeteriorationGet(self):
#         '-no docstring-'
#         #return p0, p1, p2
#
#     def DeteriorationSet(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def TrainDlg(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def TrainPhrase(self, p0):
#         '-no docstring-'
#         #return p1
#
#     def TrainQuery(self):
#         '-no docstring-'
#         #return p0
#


class IDgnSREngineNotifySinkA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108001-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def AttribChanged2(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Paused(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def MimicDone(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def ErrorHappened(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Progress(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


IDgnSREngineNotifySinkA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'AttribChanged2',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Paused',
        (['in'], c_ulonglong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'MimicDone',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(IUnknown), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ErrorHappened',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Progress',
        (['in'], c_int, 'p0'),
        (['in'], STRING, 'p1')
    ),
]

################################################################
# code template for IDgnSREngineNotifySinkA implementation
# class IDgnSREngineNotifySinkA_Impl(object):
#     def AttribChanged2(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Paused(self, p0):
#         '-no docstring-'
#         #return 
#
#     def MimicDone(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def ErrorHappened(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Progress(self, p0, p1):
#         '-no docstring-'
#         #return 
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0007._fields_ = [
    ('gEngineID', GUID),
    ('szMfgName', c_ushort * 262),
    ('szProductName', c_ushort * 262),
    ('gModeID', GUID),
    ('szModeName', c_ushort * 262),
    ('language', __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005),
    ('dwSequencing', c_ulong),
    ('dwMaxWordsVocab', c_ulong),
    ('dwMaxWordsState', c_ulong),
    ('dwGrammars', c_ulong),
    ('dwFeatures', c_ulong),
    ('dwInterfaces', c_ulong),
    ('dwEngineFeatures', c_ulong),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0007) == 1764, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0007)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0007) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0007)


class IVoiceDictation0A(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108400-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Register(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete, p5: hints.Incomplete, p6: hints.Incomplete) -> hints.Hresult: ...
        def SiteInfoGet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def SiteInfoSet(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def SessionSerialize(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TopicEnum(self, p0: hints.Incomplete, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def TopicAddString(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete) -> hints.Hresult: ...
        def TopicAddGrammar(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def TopicRemove(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TopicSerialize(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def TopicDeserialize(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Activate(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Deactivate(self) -> hints.Hresult: ...
        def Reserved15(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...


class __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0020(Structure):
    pass


VDSITEINFOA = __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0020

IVoiceDictation0A._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Register',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1'),
        (['in'], POINTER(IUnknown), 'p2'),
        (['in'], STRING, 'p3'),
        (['in'], POINTER(IUnknown), 'p4'),
        (
            ['in'],
            GUID,
            'p5',
        ),
        (['in'], c_ulong, 'p6')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SiteInfoGet',
        (['in'], STRING, 'p0'),
        (['in'], POINTER(VDSITEINFOA), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SiteInfoSet',
        (['in'], STRING, 'p0'),
        (['in'], POINTER(VDSITEINFOA), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'SessionSerialize',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicEnum',
        (['in', 'out'], POINTER(POINTER(VDCTTOPICA)), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicAddString',
        (['in'], STRING, 'p0'),
        (['in'], POINTER(LANGUAGEA), 'p1'),
        (['in'], POINTER(STRING), 'p2')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicAddGrammar',
        (['in'], STRING, 'p0'),
        (['in'], SDATA, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicRemove',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicSerialize',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'TopicDeserialize',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Activate',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'Deactivate'),
    COMMETHOD(
        [],
        HRESULT,
        'Reserved15',
        (['in'], c_ulong, 'p0'),
        (['in'], VDCTBOOKMARK, 'p1')
    ),
]

################################################################
# code template for IVoiceDictation0A implementation
# class IVoiceDictation0A_Impl(object):
#     def Register(self, p0, p1, p2, p3, p4, p5, p6):
#         '-no docstring-'
#         #return 
#
#     def SiteInfoGet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def SiteInfoSet(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def SessionSerialize(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TopicEnum(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def TopicAddString(self, p0, p1, p2):
#         '-no docstring-'
#         #return 
#
#     def TopicAddGrammar(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def TopicRemove(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TopicSerialize(self, p0):
#         '-no docstring-'
#         #return 
#
#     def TopicDeserialize(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Activate(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Deactivate(self):
#         '-no docstring-'
#         #return 
#
#     def Reserved15(self, p0, p1):
#         '-no docstring-'
#         #return 
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0006._fields_ = [
    ('gEngineID', GUID),
    ('szMfgName', c_char * 262),
    ('szProductName', c_char * 262),
    ('gModeID', GUID),
    ('szModeName', c_char * 262),
    ('language', __MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004),
    ('dwSequencing', c_ulong),
    ('dwMaxWordsVocab', c_ulong),
    ('dwMaxWordsState', c_ulong),
    ('dwGrammars', c_ulong),
    ('dwFeatures', c_ulong),
    ('dwInterfaces', c_ulong),
    ('dwEngineFeatures', c_ulong),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0006) == 912, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0006)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0006) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0006)


class IDgnSSvcOutputEventW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD109201-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Register(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def PlayString(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> hints.Incomplete: ...
        def NameFromKey(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p5: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def PlayEvents(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Hresult: ...
        def KeyFromName(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def NameFromKey2(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p5: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


IDgnSSvcOutputEventW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Register',
        (['in'], POINTER(IDgnSSvcActionNotifySink), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PlayString',
        (['in'], WSTRING, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'NameFromKey',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ushort), 'p4'),
        (['in', 'out'], POINTER(c_ulong), 'p5')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PlayEvents',
        (['in'], c_ulong, 'p0'),
        (['in'], POINTER(HOOK_EVENTMSG), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'KeyFromName',
        (['in'], c_ulong, 'p0'),
        (['in'], WSTRING, 'p1'),
        (['in', 'out'], POINTER(c_ubyte), 'p2'),
        (['in', 'out'], POINTER(c_ubyte), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'NameFromKey2',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulong, 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ushort), 'p4'),
        (['in', 'out'], POINTER(c_ulong), 'p5')
    ),
]

################################################################
# code template for IDgnSSvcOutputEventW implementation
# class IDgnSSvcOutputEventW_Impl(object):
#     def Register(self, p0):
#         '-no docstring-'
#         #return 
#
#     def PlayString(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return p4
#
#     def NameFromKey(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return p4, p5
#
#     def PlayEvents(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return 
#
#     def KeyFromName(self, p0, p1):
#         '-no docstring-'
#         #return p2, p3
#
#     def NameFromKey2(self, p0, p1, p2, p3):
#         '-no docstring-'
#         #return p4, p5
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0001._fields_ = [
    ('pData', POINTER(c_ubyte)),
    ('dwSize', c_ulong),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0001) == 16, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0001)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0001) == 8, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0001)

ISRGramNotifySinkW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'BookMark',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD([], HRESULT, 'Paused'),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseFinish',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulonglong, 'p1'),
        (['in'], c_ulonglong, 'p2'),
        (['in'], POINTER(SRPHRASEW), 'p3'),
        (['in'], POINTER(IUnknown), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseHypothesis',
        (['in'], c_ulong, 'p0'),
        (['in'], c_ulonglong, 'p1'),
        (['in'], c_ulonglong, 'p2'),
        (['in'], POINTER(SRPHRASEW), 'p3'),
        (['in'], POINTER(IUnknown), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'PhraseStart',
        (['in'], c_ulonglong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'ReEvaluate',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Training',
        (['in'], c_ulong, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'UnArchive',
        (['in'], POINTER(IUnknown), 'p0')
    ),
]

################################################################
# code template for ISRGramNotifySinkW implementation
# class ISRGramNotifySinkW_Impl(object):
#     def BookMark(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Paused(self):
#         '-no docstring-'
#         #return 
#
#     def PhraseFinish(self, p0, p1, p2, p3, p4):
#         '-no docstring-'
#         #return 
#
#     def PhraseHypothesis(self, p0, p1, p2, p3, p4):
#         '-no docstring-'
#         #return 
#
#     def PhraseStart(self, p0):
#         '-no docstring-'
#         #return 
#
#     def ReEvaluate(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Training(self, p0):
#         '-no docstring-'
#         #return 
#
#     def UnArchive(self, p0):
#         '-no docstring-'
#         #return 
#


class IDgnLexWordA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108501-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Add(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def GuessPartOfSpeechandAdd(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> hints.Hresult: ...
        def GuessPartOfSpeech(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> hints.Incomplete: ...
        def Get(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...
        def Remove(self, p0: hints.Incomplete) -> hints.Hresult: ...


IDgnLexWordA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Add',
        (['in'], STRING, 'p0'),
        (['in', 'out'], POINTER(POSINFO), 'p1'),
        (['in', 'out'], POINTER(c_ubyte), 'p2'),
        (['in'], c_ulong, 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GuessPartOfSpeechandAdd',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1'),
        (['in'], STRING, 'p2'),
        (['in'], POINTER(c_ubyte), 'p3'),
        (['in'], c_ulong, 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GuessPartOfSpeech',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1'),
        (['in'], STRING, 'p2'),
        (['in', 'out'], POINTER(POSINFO), 'p3')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Get',
        (['in'], STRING, 'p0'),
        (['in', 'out'], POINTER(POSINFO), 'p1'),
        (['in', 'out'], POINTER(c_ubyte), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['out'], POINTER(c_ulong), 'p4')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Remove',
        (['in'], STRING, 'p0')
    ),
]

################################################################
# code template for IDgnLexWordA implementation
# class IDgnLexWordA_Impl(object):
#     def Add(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2
#
#     def GuessPartOfSpeechandAdd(self, p0, p1, p2, p3, p4):
#         '-no docstring-'
#         #return 
#
#     def GuessPartOfSpeech(self, p0, p1, p2):
#         '-no docstring-'
#         #return p3
#
#     def Get(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#
#     def Remove(self, p0):
#         '-no docstring-'
#         #return 
#


class IDgnVDctNotifySink(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10840C-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def ErrorHappened(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def WarningHappened(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def JITPause(self) -> hints.Hresult: ...
        def HotKeyHappened(self, p0: hints.Incomplete) -> hints.Hresult: ...


IDgnVDctNotifySink._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'ErrorHappened',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'WarningHappened',
        (['in'], POINTER(IUnknown), 'p0')
    ),
    COMMETHOD([], HRESULT, 'JITPause'),
    COMMETHOD(
        [],
        HRESULT,
        'HotKeyHappened',
        (['in'], c_ulong, 'p0')
    ),
]

################################################################
# code template for IDgnVDctNotifySink implementation
# class IDgnVDctNotifySink_Impl(object):
#     def ErrorHappened(self, p0):
#         '-no docstring-'
#         #return 
#
#     def WarningHappened(self, p0):
#         '-no docstring-'
#         #return 
#
#     def JITPause(self):
#         '-no docstring-'
#         #return 
#
#     def HotKeyHappened(self, p0):
#         '-no docstring-'
#         #return 
#

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0012._fields_ = [
    ('dwNextPhonemeNode', c_ulong),
    ('dwUpAlternatePhonemeNode', c_ulong),
    ('dwDownAlternatePhonemeNode', c_ulong),
    ('dwPreviousPhonemeNode', c_ulong),
    ('dwWordNode', c_ulong),
    ('qwStartTime', c_ulonglong),
    ('qwEndTime', c_ulonglong),
    ('dwPhonemeScore', c_ulong),
    ('wVolume', c_ushort),
    ('wPitch', c_ushort),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0012) == 48, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0012)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0012) == 8, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0012)

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0015._fields_ = [
    ('message', c_ulong),
    ('paramL', c_ulong),
    ('paramH', c_ulong),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0015) == 12, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0015)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0015) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0015)

__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0020._fields_ = [
    ('dwAutoGainEnable', c_ulong),
    ('dwAwakeState', c_ulong),
    ('dwThreshold', c_ulong),
    ('dwDevice', c_ulong),
    ('dwEnable', c_ulong),
    ('szMicrophone', c_char * 32),
    ('szSpeaker', c_char * 32),
    ('gModeID', GUID),
]

assert sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0020) == 100, sizeof(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0020)
assert alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0020) == 4, alignment(__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0020)


class IDgnSRSpeakerW(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD10901C-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def EnumBaseModels(self, p1: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...
        def New(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def GetSpeakerDirectory(self, p0: hints.Incomplete, p1: hints.Incomplete, p2: hints.Incomplete, p3: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete]: ...


IDgnSRSpeakerW._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'EnumBaseModels',
        (['out'], POINTER(POINTER(c_ushort)), 'p0'),
        (['in', 'out'], POINTER(c_ulong), 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'New',
        (['in'], WSTRING, 'p0'),
        (['in'], WSTRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'GetSpeakerDirectory',
        (['in'], WSTRING, 'p0'),
        (['in', 'out'], POINTER(c_ushort), 'p1'),
        (['in'], c_ulong, 'p2'),
        (['in', 'out'], POINTER(c_ulong), 'p3')
    ),
]

################################################################
# code template for IDgnSRSpeakerW implementation
# class IDgnSRSpeakerW_Impl(object):
#     def EnumBaseModels(self):
#         '-no docstring-'
#         #return p0, p1
#
#     def New(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def GetSpeakerDirectory(self, p0, p2):
#         '-no docstring-'
#         #return p1, p3
#


class ISRGramDictationA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{05EB6C65-DBAB-11CD-B3CA-00AA0047BA4F}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def Context(self, p0: hints.Incomplete, p1: hints.Incomplete) -> hints.Hresult: ...
        def Hint(self, p0: hints.Incomplete) -> hints.Hresult: ...
        def Words(self, p0: hints.Incomplete) -> hints.Hresult: ...


ISRGramDictationA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'Context',
        (['in'], STRING, 'p0'),
        (['in'], STRING, 'p1')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Hint',
        (['in'], STRING, 'p0')
    ),
    COMMETHOD(
        [],
        HRESULT,
        'Words',
        (['in'], STRING, 'p0')
    ),
]

################################################################
# code template for ISRGramDictationA implementation
# class ISRGramDictationA_Impl(object):
#     def Context(self, p0, p1):
#         '-no docstring-'
#         #return 
#
#     def Hint(self, p0):
#         '-no docstring-'
#         #return 
#
#     def Words(self, p0):
#         '-no docstring-'
#         #return 
#


class IDgnSRResGraphA(comtypes.IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{DD108020-6205-11CF-AE61-0000E8A28647}')
    _idlflags_ = []

    if TYPE_CHECKING:  # commembers
        def GetWordNode(self, p0: hints.Incomplete, p3: hints.Incomplete, p4: hints.Incomplete) -> tuple[hints.Incomplete, hints.Incomplete, hints.Incomplete]: ...


IDgnSRResGraphA._methods_ = [
    COMMETHOD(
        [],
        HRESULT,
        'GetWordNode',
        (['in'], c_ulong, 'p0'),
        (['out'], POINTER(DGNSRRESWORDNODE), 'p1'),
        (['out'], POINTER(c_ubyte), 'p2'),
        (['in'], c_ulong, 'p3'),
        (['in', 'out'], POINTER(c_ulong), 'p4')
    ),
]

################################################################
# code template for IDgnSRResGraphA implementation
# class IDgnSRResGraphA_Impl(object):
#     def GetWordNode(self, p0, p3):
#         '-no docstring-'
#         #return p1, p2, p4
#

__all__ = [
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0019',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0002',
    'VPS_ORDINAL', 'IDgnSRTopic2A', 'IDgnSRLexiconA',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0018',
    'ISRGramNotifySinkW', 'VPS_ADJECTIVE', 'VPS_CARDINAL',
    'VDCTTOPICA', 'IVoiceDictation0W', 'VPS_PREPOSITION',
    'VDCTTOPICW', 'VPS_VERB',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0020',
    'IDgnSRGramCommon', 'VPS_DETERMINER', 'ISRCentralA',
    'IDgnSREngineNotifySinkA', 'ISRResBasicW', 'IDgnGetSinkFlags',
    'VOICEPARTOFSPEECH', 'typelib_path', 'SRGRMFMT_CFG',
    'CHARSET_ENGINEPHONETIC',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0016',
    'IDgnExtModSupStringsA', 'ILexPronounceA', 'SRRESWORDNODE',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0017',
    'CHARSET_IPAPHONETIC', 'VDSITEINFOA',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0001',
    'IDgnSRTopic2W', 'IDgnSRSpeakerA', 'SRGRMFMT_DRAGONNATIVE2',
    'IDgnSRGramSelectA',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0004',
    'ISRResBasicA', 'SRGRMFMT_DRAGONNATIVE1', 'IDgnLexWordW',
    'SRGRMFMT_DICTATION', 'ISRGramDictationW', 'ILexPronounceW',
    'IDgnSRGramDictationW', 'IDgnSRAudioFileSourceA',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0006',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0023',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0011',
    'ISRGramCFGA', 'ISRResGraphW', 'VDSITEINFOW',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0015',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0013',
    'VPS_ADVERB', 'Library', 'IDgnSRResGraphA', 'POSINFO',
    'SRMODEINFOW', 'IDgnSSvcInterpreterW', 'IVDct0NotifySinkW',
    'ISRResAudio', 'IDgnSRAudioFileSourceW', 'IDgnSREngineControlA',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0003',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0012',
    'IDgnSREngineControlW', 'VPS_INTERJECTION',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0010',
    'VPS_CONTRACTION', 'IDgnSRWordPrefixEnumA', 'ISRResGraphA',
    'SRGRMFMT_DICTATIONNATIVE', 'IDgnSRGramSelectW',
    'ISRResCorrectionA', 'IDgnSRResSelect',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0007',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0024',
    'ISRNotifySink', 'VOICECHARSET', 'IDgnSRTrainingA',
    'VPS_PUNCTUATION', 'ISRGramNotifySinkA', 'SDATA', 'SRPHRASEA',
    'LANGUAGEW', 'IDgnSSvcOutputEventA', 'ISRCentralW', 'SRPHRASEW',
    'VPS_PRONOUN', 'DGNSRRESWORDNODE', 'ISRGramCommonW',
    'IVDct0NotifySinkA', 'IDgnVDctTextA', 'IDgnSRWordPrefixEnumW',
    'ISRGramCommonA', 'IVDct0TextW', 'SRGRMFMT_LIMITEDDOMAINNATIVE',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0005',
    'VPS_PROPERNOUN', 'ISRResCorrectionW', 'SAPI_POSTYPE',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0014',
    'IDgnSRLexiconW', 'IDgnSRSpeakerW', 'SRGRMFMT_DRAGONNATIVE3',
    'CHARSET_TEXT', 'VPS_NOUN', 'IDgnSRWordEnumW', 'ISRResMemory',
    'SRMODEINFOA', 'SRGRMFMT', 'IDgnExtModSupStringsW', 'ISRSpeakerW',
    'IDgnSSvcOutputEventW', 'SRRESPHONEMENODE',
    'IDgnSSvcActionNotifySink', 'DGN_ERROR_W', 'IVDct0TextA',
    'IVoiceDictation0A', 'ISRGramDictationA', 'LANGUAGEA',
    'SRGRMFMT_CFGNATIVE', 'IDgnSSvcInterpreterA', 'IDgnSRWordEnumA',
    'HOOK_EVENTMSG', 'VDCTBOOKMARK', 'VPS_QUANTIFIER',
    'VPS_CONJUNCTION', 'IDgnVDctNotifySink', 'ISRSpeakerA',
    'VPS_UNKNOWN', 'IDgnLexWordA', 'IDgnVDctTextW',
    'VPS_ABBREVIATION', 'IDgnSRResGraphW',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0022',
    'ISRGramCFGW', 'SRGRMFMT_LIMITEDDOMAIN',
    '__MIDL___MIDL_itf_dragon_interfaces_0000_0000_0021',
    'IDgnErrorW', 'IDgnSREngineNotifySinkW', 'IDgnSRGramDictationA'
]


