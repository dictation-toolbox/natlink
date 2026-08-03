"""Microsoft SAPI 4.0 standard constants from speech.h.

Source: Reference/natlink-master/NatlinkSource/COM/speech.h
(c) Microsoft Corporation
"""

# ---------------------------------------------------------------------------
# VOICECHARSET enum
# ---------------------------------------------------------------------------
CHARSET_TEXT = 0
CHARSET_IPAPHONETIC = 1
CHARSET_ENGINEPHONETIC = 2

# ---------------------------------------------------------------------------
# VOICEPARTOFSPEECH enum
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# ISRNotifySink — attribute codes (ISRNSAC_*)
# ---------------------------------------------------------------------------
ISRNSAC_AUTOGAINENABLE = 1
ISRNSAC_THRESHOLD = 2
ISRNSAC_ECHO = 3
ISRNSAC_ENERGYFLOOR = 4
ISRNSAC_MICROPHONE = 5
ISRNSAC_REALTIME = 6
ISRNSAC_SPEAKER = 7
ISRNSAC_TIMEOUT = 8
ISRNSAC_STARTLISTENING = 9
ISRNSAC_STOPLISTENING = 10

# ---------------------------------------------------------------------------
# ISRGramNotifySink — PhraseFinish flags (ISRNOTEFIN_*)
# ---------------------------------------------------------------------------
ISRNOTEFIN_RECOGNIZED = 1 << 0       # 0x01
ISRNOTEFIN_THISGRAMMAR = 1 << 1      # 0x02
ISRNOTEFIN_FROMTHISGRAMMAR = 1 << 2  # 0x04

# ---------------------------------------------------------------------------
# ISRResCorrection — confidence levels
# ---------------------------------------------------------------------------
SRCORCONFIDENCE_SOME = 0x0001
SRCORCONFIDENCE_VERY = 0x0002

# ---------------------------------------------------------------------------
# Grammar header types (SRHDRTYPE_*)
# ---------------------------------------------------------------------------
SRHDRTYPE_CFG = 0
SRHDRTYPE_LIMITEDDOMAIN = 1
SRHDRTYPE_DICTATION = 2

# ---------------------------------------------------------------------------
# Grammar CFG symbol types (SRCFG_*)
# ---------------------------------------------------------------------------
SRCFG_STARTOPERATION = 1
SRCFG_ENDOPERATION = 2
SRCFG_WORD = 3
SRCFG_RULE = 4
SRCFG_WILDCARD = 5
SRCFG_LIST = 6

# ---------------------------------------------------------------------------
# Grammar CFG operation codes (SRCFGO_*)
# ---------------------------------------------------------------------------
SRCFGO_SEQUENCE = 1
SRCFGO_ALTERNATIVE = 2
SRCFGO_REPEAT = 3
SRCFGO_OPTIONAL = 4

# ---------------------------------------------------------------------------
# Grammar chunk IDs (SRCKCFG_*)
# ---------------------------------------------------------------------------
SRCKCFG_WORDS = 2
SRCKCFG_RULES = 3
SRCKCFG_EXPORTRULES = 4
SRCKCFG_IMPORTRULES = 5
SRCKCFG_LISTS = 6

# ---------------------------------------------------------------------------
# SRGRMFMT enum — grammar format types
# ---------------------------------------------------------------------------
SRGRMFMT_CFG = 0x0000
SRGRMFMT_LIMITEDDOMAIN = 0x0001
SRGRMFMT_DICTATION = 0x0002
SRGRMFMT_CFGNATIVE = 0x8000
SRGRMFMT_LIMITEDDOMAINNATIVE = 0x8001
SRGRMFMT_DICTATIONNATIVE = 0x8002
# Dragon-specific additions (also in dspeech.h)
SRGRMFMT_DRAGONNATIVE1 = 0x8101   # SELECT grammar
SRGRMFMT_DRAGONNATIVE2 = 0x8102
SRGRMFMT_DRAGONNATIVE3 = 0x8103

# ---------------------------------------------------------------------------
# SR errors — SRERROR(x) = 0x80040400 + x, SPEECHERROR(x) = 0x80040200 + x
# ---------------------------------------------------------------------------
_SRERROR_BASE = 0x80040400
_SPEECHERROR_BASE = 0x80040200

SRERR_NONE = 0x00000000                                   # S_OK
SRERR_OUTOFDISK = _SPEECHERROR_BASE + 5                   # 0x80040205
SRERR_NOTSUPPORTED = 0x80004001                            # E_NOTIMPL
SRERR_NOTENOUGHDATA = 0x80040201                           # AUDERR_NOTENOUGHDATA
SRERR_VALUEOUTOFRANGE = 0x8000FFFF                         # E_UNEXPECTED
SRERR_GRAMMARTOOCOMPLEX = _SRERROR_BASE + 6                # 0x80040406
SRERR_GRAMMARWRONGTYPE = _SRERROR_BASE + 7                 # 0x80040407
SRERR_INVALIDWINDOW = 0x8004000F                           # OLE_E_INVALIDHWND
SRERR_INVALIDPARAM = 0x80070057                            # E_INVALIDARG
SRERR_INVALIDMODE = _SPEECHERROR_BASE + 6                  # 0x80040206
SRERR_TOOMANYGRAMMARS = _SRERROR_BASE + 11                 # 0x8004040B
SRERR_INVALIDLIST = _SPEECHERROR_BASE + 7                  # 0x80040207
SRERR_WAVEDEVICEBUSY = 0x80040203                          # AUDERR_WAVEDEVICEBUSY
SRERR_WAVEFORMATNOTSUPPORTED = 0x80040202                  # AUDERR_WAVEFORMATNOTSUPPORTED
SRERR_INVALIDCHAR = _SPEECHERROR_BASE + 8                  # 0x80040208
SRERR_GRAMTOOCOMPLEX = SRERR_GRAMMARTOOCOMPLEX             # alias
SRERR_GRAMTOOLARGE = _SRERROR_BASE + 17                    # 0x80040411
SRERR_INVALIDINTERFACE = 0x80004002                        # E_NOINTERFACE
SRERR_INVALIDKEY = _SPEECHERROR_BASE + 9                   # 0x80040209
SRERR_INVALIDFLAG = 0x80040204                             # AUDERR_INVALIDFLAG
SRERR_GRAMMARERROR = _SRERROR_BASE + 22                    # 0x80040416
SRERR_INVALIDRULE = _SRERROR_BASE + 23                     # 0x80040417
SRERR_RULEALREADYACTIVE = _SRERROR_BASE + 24               # 0x80040418
SRERR_RULENOTACTIVE = _SRERROR_BASE + 25                   # 0x80040419
SRERR_NOUSERSELECTED = _SRERROR_BASE + 26                  # 0x8004041A
SRERR_BAD_PRONUNCIATION = _SRERROR_BASE + 27               # 0x8004041B
SRERR_DATAFILEERROR = _SRERROR_BASE + 28                   # 0x8004041C
SRERR_GRAMMARALREADYACTIVE = _SRERROR_BASE + 29            # 0x8004041D
SRERR_GRAMMARNOTACTIVE = _SRERROR_BASE + 30                # 0x8004041E
SRERR_GLOBALGRAMMARALREADYACTIVE = _SRERROR_BASE + 31      # 0x8004041F
SRERR_LANGUAGEMISMATCH = _SRERROR_BASE + 32                # 0x80040420
SRERR_MULTIPLELANG = _SRERROR_BASE + 33                    # 0x80040421
SRERR_LDGRAMMARNOWORDS = _SRERROR_BASE + 34                # 0x80040422
SRERR_NOLEXICON = _SRERROR_BASE + 35                       # 0x80040423
SRERR_SPEAKEREXISTS = _SRERROR_BASE + 36                   # 0x80040424
SRERR_GRAMMARENGINEMISMATCH = _SRERROR_BASE + 37           # 0x80040425
SRERR_BOOKMARKEXISTS = _SRERROR_BASE + 38                  # 0x80040426
SRERR_BOOKMARKDOESNOTEXIST = _SRERROR_BASE + 39            # 0x80040427
SRERR_MICWIZARDCANCELED = _SRERROR_BASE + 40               # 0x80040428
SRERR_WORDTOOLONG = _SRERROR_BASE + 41                     # 0x80040429
SRERR_BAD_WORD = _SRERROR_BASE + 42                        # 0x8004042A

# speech.h: SPEECHERROR(14) — comment in speech.h says 0x8004020D but the macro
# evaluates to 0x8004020E.  The C++ compiles the macro, so 0x8004020E is what Dragon
# actually returns.  Prior Python code had 0x8004020D (copied from the wrong comment).
E_BUFFERTOOSMALL = _SPEECHERROR_BASE + 14                  # 0x8004020E

# ---------------------------------------------------------------------------
# Lexicon errors — LEXERROR(x) = 0x80040800 + x, LEXWARNING(x) = 0x00040800 + x
# ---------------------------------------------------------------------------
_LEXERROR_BASE = 0x80040800

LEXERR_INVALIDTEXTCHAR = _LEXERROR_BASE + 0x01             # 0x80040801
LEXERR_INVALIDSENSE = _LEXERROR_BASE + 0x02                # 0x80040802
LEXERR_NOTINLEX = _LEXERROR_BASE + 0x03                    # 0x80040803
LEXERR_OUTOFDISK = _LEXERROR_BASE + 0x04                   # 0x80040804
LEXERR_INVALIDPRONCHAR = _LEXERROR_BASE + 0x05             # 0x80040805
LEXERR_ALREADYINLEX = 0x00040806                           # LEXWARNING (success HRESULT)
LEXERR_PRNBUFTOOSMALL = _LEXERROR_BASE + 0x07              # 0x80040807
LEXERR_ENGBUFTOOSMALL = _LEXERROR_BASE + 0x08              # 0x80040808
LEXERR_INVALIDLEX = _LEXERROR_BASE + 0x09                  # 0x80040809
