"""Dragon extensions to SAPI 4.0 — constant definitions from dspeech.h.

Source: Reference/natlink-master/NatlinkSource/COM/dspeech.h
(c) Dragon Systems, Inc. 1998
"""

# ---------------------------------------------------------------------------
# IDgnSSvcActionNotifySink
# ---------------------------------------------------------------------------
ACTIONSTATUS_F_ALLOWHEARDWORD = 0x2
ACTIONSTATUS_F_ALLOWUSERINPUT = 0x4

# ---------------------------------------------------------------------------
# IDgnSREngineControl — microphone states
# ---------------------------------------------------------------------------
DGNMIC_DISABLED = 0
DGNMIC_OFF = 1
DGNMIC_ON = 2
DGNMIC_SLEEPING = 3
DGNMIC_PAUSE = 4
DGNMIC_RESUME = 5

# ---------------------------------------------------------------------------
# IDgnSREngineNotifySink — attribute codes
# ---------------------------------------------------------------------------
DGNSRAC_BASE = 1000
DGNSRAC_MICSTATE = DGNSRAC_BASE + 1       # 1001
DGNSRAC_REGISTRY = DGNSRAC_BASE + 2       # 1002
DGNSRAC_PLAYBACKDONE = DGNSRAC_BASE + 3   # 1003
DGNSRAC_TOPIC = DGNSRAC_BASE + 4          # 1004
DGNSRAC_LEXADD = DGNSRAC_BASE + 5         # 1005
DGNSRAC_LEXREMOVE = DGNSRAC_BASE + 6      # 1006

# ---------------------------------------------------------------------------
# IDgnSREngineNotifySink — engine sink flags
# ---------------------------------------------------------------------------
DGNSRSINKFLAG_SENDBEGINUTT = 0x01
DGNSRSINKFLAG_SENDENDUTT = 0x02
DGNSRSINKFLAG_SENDVUMETER = 0x04
DGNSRSINKFLAG_SENDATTRIB = 0x08
DGNSRSINKFLAG_SENDINTERFERENCE = 0x10
DGNSRSINKFLAG_SENDSOUND = 0x20
DGNSRSINKFLAG_SENDJITPAUSED = 0x40
DGNSRSINKFLAG_SENDERROR = 0x80
DGNSRSINKFLAG_SENDPROGRESS = 0x100
DGNSRSINKFLAG_SENDMIMICDONE = 0x200
DGNSRSINKFLAG_SENDALL = 0x3FF
DGNSRSINKFLAG_DEFAULT = (DGNSRSINKFLAG_SENDBEGINUTT |
                         DGNSRSINKFLAG_SENDENDUTT |
                         DGNSRSINKFLAG_SENDATTRIB)

# ---------------------------------------------------------------------------
# IDgnSREngineNotifySink — grammar sink flags
# ---------------------------------------------------------------------------
DGNSRGRAMSINKFLAG_SENDPHRASESTART = 0x1000
DGNSRGRAMSINKFLAG_SENDPHRASEHYPO = 0x2000
DGNSRGRAMSINKFLAG_SENDPHRASEFINISH = 0x4000
DGNSRGRAMSINKFLAG_SENDFOREIGNFINISH = 0x8000
DGNSRGRAMSINKFLAG_SENDALL = 0xF1FF
DGNSRGRAMSINKFLAG_DEFAULT = (DGNSRGRAMSINKFLAG_SENDPHRASESTART |
                             DGNSRGRAMSINKFLAG_SENDPHRASEFINISH)

# ---------------------------------------------------------------------------
# IDgnSREngineNotifySink — dictation sink flags
# ---------------------------------------------------------------------------
DGNDICTSINKFLAG_SENDPHRASEFINISH = DGNSRGRAMSINKFLAG_SENDPHRASEFINISH
DGNDICTSINKFLAG_SENDFOREIGNFINISH = DGNSRGRAMSINKFLAG_SENDFOREIGNFINISH
DGNDICTSINKFLAG_SENDPHRASEHYPO = DGNSRGRAMSINKFLAG_SENDPHRASEHYPO
DGNDICTSINKFLAG_SENDPHRASESTART = DGNSRGRAMSINKFLAG_SENDPHRASESTART
DGNDICTSINKFLAG_SENDATTRIB = DGNSRSINKFLAG_SENDATTRIB
DGNDICTSINKFLAG_SENDINTERFERENCE = DGNSRSINKFLAG_SENDINTERFERENCE
DGNDICTSINKFLAG_SENDBEGINUTT = DGNSRSINKFLAG_SENDBEGINUTT
DGNDICTSINKFLAG_SENDENDUTT = DGNSRSINKFLAG_SENDENDUTT
DGNDICTSINKFLAG_SENDVUMETER = DGNSRSINKFLAG_SENDVUMETER
DGNDICTSINKFLAG_SENDERROR = DGNSRSINKFLAG_SENDERROR
DGNDICTSINKFLAG_SENDTEXTCHANGED = 0x00010000
DGNDICTSINKFLAG_SENDTEXTSELCHANGED = 0x00020000
DGNDICTSINKFLAG_SENDTRAINING = 0x00040000
DGNDICTSINKFLAG_SENDWARNING = 0x00080000
DGNDICTSINKFLAG_SENDJITPAUSE = 0x00100000
DGNDICTSINKFLAG_SENDCORRECTIONHOTKEY = 0x00200000
DGNDICTSINKFLAG_SENDALL = 0x003F01FF
DGNDICTSINKFLAG_DEFAULT = (DGNDICTSINKFLAG_SENDTEXTCHANGED |
                           DGNDICTSINKFLAG_SENDTEXTSELCHANGED)

# ---------------------------------------------------------------------------
# IDgnSRParmEnum
# ---------------------------------------------------------------------------
CBMAX_SUBDIRNAME = 9
DGNNOTIFICATION_ATTRIB = 0x0001
DGNNOTIFICATION_UTTBEG = 0x0002
DGNNOTIFICATION_UTTEND = 0x0003
DGNNOTIFICATION_VUMETER = 0x0004
DGNNOTIFICATION_DGNATTRIB = 0x0005
DGNNOTIFICATION_JITPAUSE = 0x0006
DGNPAR_BOOL = 1
DGNPAR_INT = 2
DGNPAR_STRING = 3
DGNPAR_FLOAT = 4

# ---------------------------------------------------------------------------
# IDgnSRGramDictation
# ---------------------------------------------------------------------------
DGNWORDSFLAG_DOIMMED = 0x0001

# ---------------------------------------------------------------------------
# IDgnSSvcGUI
# ---------------------------------------------------------------------------
DGNGUI_SHOWMINIMAL = 0x1
DGNGUI_SHOWFULL = 0x2
DGNGUI_SHOWPERMANENT = 0x4

# ---------------------------------------------------------------------------
# IDgnSRAudioFileSource
# ---------------------------------------------------------------------------
DGN_SM_F_MENUACTIVE = 1
DGN_SM_F_MOVEWINDOW = 2
DGNUTTFLG_USELABEL = 0x0001
DGNUTTFLG_DETECTUTT = 0x0002
DGNUTTFLG_REALTIME = 0x0004
DGNUTTTYP_COMBINED = 0x0000   # .UTD
DGNUTTTYP_UTT = 0x0001        # .UTT
DGNUTTTYP_MSWAV = 0x0002      # .WAV
DGNUTTTYP_NISTWAV = 0x0003    # .NWV

# ---------------------------------------------------------------------------
# IDgnSRWordEnum — word flags
# ---------------------------------------------------------------------------
DGNWORDFLAG_USERADDED = 0x00000001
DGNWORDFLAG_VARADDED = 0x00000002
DGNWORDFLAG_CUSTOMPRON = 0x00000004
DGNWORDFLAG_NODELETE = 0x00000008
DGNWORDFLAG_PASSIVE_CAP_NEXT = 0x00000010
DGNWORDFLAG_ACTIVE_CAP_NEXT = 0x00000020
DGNWORDFLAG_UPPERCASE_NEXT = 0x00000040
DGNWORDFLAG_LOWERCASE_NEXT = 0x00000080
DGNWORDFLAG_NO_SPACE_NEXT = 0x00000100
DGNWORDFLAG_TWO_SPACES_NEXT = 0x00000200
DGNWORDFLAG_COND_NO_SPACE = 0x00000400
DGNWORDFLAG_CAP_ALL = 0x00000800
DGNWORDFLAG_UPPERCASE_ALL = 0x00001000
DGNWORDFLAG_LOWERCASE_ALL = 0x00002000
DGNWORDFLAG_NO_SPACE_ALL = 0x00004000
DGNWORDFLAG_RESET_NO_SPACE = 0x00008000
DGNWORDFLAG_SWALLOW_PERIOD = 0x00010000
DGNWORDFLAG_IS_PERIOD = 0x00020000
DGNWORDFLAG_NO_FORMATTING = 0x00040000
DGNWORDFLAG_NO_SPACE_CHANGE = 0x00080000
DGNWORDFLAG_NO_CAP_CHANGE = 0x00100000
DGNWORDFLAG_NO_SPACE_BEFORE = 0x00200000
DGNWORDFLAG_RESET_UC_LC_CAPS = 0x00400000
DGNWORDFLAG_NEW_LINE = 0x00800000
DGNWORDFLAG_NEW_PARAGRAPH = 0x01000000
DGNWORDFLAG_TITLE_MODE = 0x02000000
DGNWORDFLAG_BEGINNING_TITLE_MODE = 0x04000000
DGNWORDFLAG_SPACE_BAR = 0x08000000
DGNWORDFLAG_NOT_IN_DICTATION = 0x10000000
DGNWORDFLAG_GUESSEDPRON = 0x20000000
DGNWORDFLAG_TOPICADDED = 0x40000000

# ---------------------------------------------------------------------------
# IDgnSRWordEnum — test flags
# ---------------------------------------------------------------------------
DGNWORDTESTFLAG_CASESENSITIVE = 0x0001
DGNWORDTESTFLAG_DICTONLY = 0x0002
DGNWORDTESTFLAG_ACTIVEVOCONLY = 0x0004

# ---------------------------------------------------------------------------
# IDgnSRWordEnum — text parse flags
# ---------------------------------------------------------------------------
DGNTEXTPARSEFLAG_CASESENSITIVE = 0x0001
DGNTEXTPARSEFLAG_COMMANDS = 0x0002
DGNTEXTPARSEFLAG_ALLPATHS = 0x0004
DGNTEXTPARSEFLAG_DONTUSEBDFILTER = 0x0008
DGNTEXTPARSEFLAG_EXACTMATCH = 0x0010
DGNTEXTPARSEFLAG_NONCAPMATCH = 0x0020

# ---------------------------------------------------------------------------
# Token flags (text parse results)
# ---------------------------------------------------------------------------
TKNFLAG_DEFAULT = 0x0000
TKNFLAG_BEGINALT = 0x0001
TKNFLAG_ENDALT = 0x0002
TKNFLAG_BEGINSEQ = 0x0004
TKNFLAG_ENDSEQ = 0x0008
TKNFLAG_JUNK = 0x0010
TKNFLAG_SENTSTART = 0x0020
TKNFLAG_INACTIVEVOC = 0x0040
TKNFLAG_INBACKUPDICT = 0x0080

# ---------------------------------------------------------------------------
# IDgnSRTraining
# ---------------------------------------------------------------------------
DGNTRNMODE_NORMAL = 0x00000000
DGNTRNMODE_CALIBRATE = 0x00000001
DGNTRNMODE_CROSSWORD = 0x00000002
DGNTRNMODE_BATCHWORD = 0x00000003
DGNTRNMODE_SINGLESET = 0x00000004
DGNTRNMODE_SHORTBATCH = 0x00000005

# ---------------------------------------------------------------------------
# IDgnVCmd
# ---------------------------------------------------------------------------
DGNVCMDF_STOPONERROR = 1
DGNVCMDF_REPORTERRORS = 2
DGNVCMDF_JUSTPARSE = 4
DGNVCMDF_NOAUTOACTIVATE = 8
DGNVCMDF_REFCOUNT = 0x10
DGNVCMDF_GLOBALCMDFILE = 0x80000000

# ---------------------------------------------------------------------------
# IDgnVDctOpt
# ---------------------------------------------------------------------------
VDCTOPT_SELECT_XYZ_ENABLED = 0x00000001
VDCTOPT_LINE_TERMINATOR = 0x00000002
VDCTOPT_DICTATION_ONLY = 0x00000003

# ---------------------------------------------------------------------------
# IDgnVDctText
# ---------------------------------------------------------------------------
VDCT_CORRECTIONDIALOG_DEFAULT = 0x00000000
VDCT_CORRECTIONDIALOG_DBLCLK = 0x00000001

# ---------------------------------------------------------------------------
# IDgnVDctNotifySink
# ---------------------------------------------------------------------------
VDCTNOTIFY_CORRECTION_HOTKEY = 1

# ---------------------------------------------------------------------------
# IDgnVDctTranscribe
# ---------------------------------------------------------------------------
TRANSCRIBEFLAG_ALL_COMMANDS = 0
TRANSCRIBEFLAG_RESTRICTED_COMMANDS = 1
TRANSCRIBEFLAG_DICTATION_ONLY = 2

# ---------------------------------------------------------------------------
# IDgnSRBuildLM
# ---------------------------------------------------------------------------
SRBUILDSLOT_USER = 1
SRBUILDSLOT_VAR = 2
SRBUILDTYPE_NEW = 1
SRBUILDTYPE_INCREMENTAL = 2

# ---------------------------------------------------------------------------
# IVoiceDictation0
# ---------------------------------------------------------------------------
DGNVDCTRF_IGNOREHOTKEYS = 0x4

# ---------------------------------------------------------------------------
# Grammar header flags (SETBIT-based, from DGNSRHDR section)
# ---------------------------------------------------------------------------
DGNSRHDRFLAG_STATICXYZGRAMMAR = 1 << 26
DGNSRHDRFLAG_DONTUSESTATEWORDS = 1 << 27
DGNSRHDRFLAG_DONTUSENOISE = 1 << 28
DGNSRHDRFLAG_USELMSCORE = 1 << 29
DGNSRHDRFLAG_ADDTODICTSTATE = 1 << 30
DGNSRHDRFLAG_LANGUAGEMODELON = 1 << 31

DGNSRCORCONFIDENCE_LMONLY = 0x8001

# ---------------------------------------------------------------------------
# Grammar chunk IDs
# ---------------------------------------------------------------------------
DGNSRCKCFG_HEADER = 0x1014
DGNSRCKCFG_VCMDCOMMAND = 0x1015
DGNSRCKCFG_LISTS = 0x1016
DGNSRHDRTYPE_SELECT = 10
DGNSRCKSELECT_INTROPHRASES = 0x1017
DGNSRCKSELECT_THRUWORD = 0x1018
DGNSRCKSELECT_ENDPHRASES = 0x1019
DGNSRCKSELECT_WORDS = 0x1020

# SRGRMFMT_DRAGONNATIVE* — defined in both dspeech.h and speech.h.
# Canonical definitions live in _speech_constants.py alongside the rest
# of the SRGRMFMT enum.

# ---------------------------------------------------------------------------
# Error codes
#
# DGNSAPIERROR(x) = MAKE_SCODE(SEVERITY_ERROR, FACILITY_ITF, x + 0x1000)
#   → 0x80040000 | (x + 0x1000) → 0x80041000 + x
# VBARCOMERROR(x) = 0x80041100 + x
# HOOKAPIERROR(x) = 0x80042000 + x
# ---------------------------------------------------------------------------
_DGNSAPI_BASE = 0x80041000
_VBARCOM_BASE = 0x80041100
_HOOKAPI_BASE = 0x80042000

# DgnSAPI errors
DGNERR_UNKNOWNWORD = _DGNSAPI_BASE + 1             # 0x80041001
DGNERR_INVALIDFORM = _DGNSAPI_BASE + 2             # 0x80041002
DGNERR_WAVEDEVICEMISSING = _DGNSAPI_BASE + 3       # 0x80041003
DGNERR_WAVEDEVICEERROR = _DGNSAPI_BASE + 4         # 0x80041004
DGNERR_TERMINATING = _DGNSAPI_BASE + 5             # 0x80041005
DGNERR_MICNOTPAUSED = _DGNSAPI_BASE + 6            # 0x80041006
DGNERR_ENGINENOTPAUSED = _DGNSAPI_BASE + 7         # 0x80041007
DGNERR_INVALIDDIRECTORY = _DGNSAPI_BASE + 8        # 0x80041008
DGNERR_ONLYONETRACKER = _DGNSAPI_BASE + 9          # 0x80041009
DGNERR_INVALIDMODE = _DGNSAPI_BASE + 10            # 0x8004100A
DGNERR_ALREADYACTIVE = _DGNSAPI_BASE + 11          # 0x8004100B
DGNERR_MODENOTACTIVE = _DGNSAPI_BASE + 12          # 0x8004100C
DGNERR_TRAININGFAILED = _DGNSAPI_BASE + 13         # 0x8004100D
DGNERR_OUTOFDISK = _DGNSAPI_BASE + 14              # 0x8004100E
DGNERR_INVALIDTOPICNAME = _DGNSAPI_BASE + 15       # 0x8004100F
DGNERR_TOPICALREADYEXISTS = _DGNSAPI_BASE + 16     # 0x80041010
DGNERR_TOPICDOESNOTEXIST = _DGNSAPI_BASE + 17      # 0x80041011
DGNERR_TOPICALREADYOPEN = _DGNSAPI_BASE + 18       # 0x80041012
DGNERR_TOPICNOTOPEN = _DGNSAPI_BASE + 19           # 0x80041013
DGNERR_TOPICINUSE = _DGNSAPI_BASE + 20             # 0x80041014
DGNERR_INVALIDSPEAKER = _DGNSAPI_BASE + 21         # 0x80041015
DGNERR_LMBUILDACTIVE = _DGNSAPI_BASE + 22          # 0x80041016
DGNERR_LMBUILDINACTIVE = _DGNSAPI_BASE + 23        # 0x80041017
DGNERR_LMBUILDABORTED = _DGNSAPI_BASE + 24         # 0x80041018
DGNERR_NOTASELECTGRAMMAR = _DGNSAPI_BASE + 25      # 0x80041019
DGNERR_DOESNOTMATCHGRAMMAR = _DGNSAPI_BASE + 26    # 0x8004101A
DGNERR_OBJECTISLOCKED = _DGNSAPI_BASE + 27         # 0x8004101B
DGNERR_CANTLOCK = _DGNSAPI_BASE + 28               # 0x8004101C
DGNERR_LMWORDSMISSING = _DGNSAPI_BASE + 29         # 0x8004101D
DGNERR_TRANSCRIBING_ON_WITHOUT_OFF = _DGNSAPI_BASE + 30  # 0x8004101E
DGNERR_TRANSCRIBING_OFF_WITHOUT_ON = _DGNSAPI_BASE + 31  # 0x8004101F

# VBarCOM errors
DGNERR_UNKNOWNKEY = _VBARCOM_BASE + 1              # 0x80041101
DGNERR_COMPILER = _VBARCOM_BASE + 2                # 0x80041102
DGNERR_INTERPRETER = _VBARCOM_BASE + 3             # 0x80041103
DGNERR_MENUNOTREGISTERED = _VBARCOM_BASE + 4       # 0x80041104
DGNERR_DVCFILEALREADYLOADED = _VBARCOM_BASE + 5    # 0x80041105
DGNERR_UNKNOWNINTERFACE = _VBARCOM_BASE + 6        # 0x80041106
DGNERR_UNKNOWNOBJECT = _VBARCOM_BASE + 7           # 0x80041107
DGNERR_INITIALIZING = _VBARCOM_BASE + 8            # 0x80041108
DGNERR_CANT_SET_NEWLINE = _VBARCOM_BASE + 9        # 0x80041109
DGNERR_INTERFACE_NOT_REGISTERED = _VBARCOM_BASE + 10  # 0x8004110A
DGNERR_CANTACCESSMEMORYFILE = _VBARCOM_BASE + 11   # 0x8004110B
DGNERR_FAILEDSYNCCHECK = _VBARCOM_BASE + 12        # 0x8004110C

# Hook API errors
HOOKERR_MEMORY = _HOOKAPI_BASE + 1                 # 0x80042001
HOOKERR_MUTEX = _HOOKAPI_BASE + 2                  # 0x80042002
HOOKERR_INJECTIONMUTEX = _HOOKAPI_BASE + 3         # 0x80042003
HOOKERR_GMHDMUTEX = _HOOKAPI_BASE + 4              # 0x80042004
HOOKERR_NOTDAEMON = _HOOKAPI_BASE + 5              # 0x80042005
HOOKERR_UNKNOWNPARAM = _HOOKAPI_BASE + 6           # 0x80042006
HOOKERR_BUFFEROVERFLOW = _HOOKAPI_BASE + 7          # 0x80042007
HOOKERR_CANNOTINJECT = _HOOKAPI_BASE + 8            # 0x80042008
HOOKERR_BADFIXUPOFFSET = _HOOKAPI_BASE + 9          # 0x80042009
HOOKERR_LOCKOVERFLOW = _HOOKAPI_BASE + 10           # 0x8004200A
HOOKERR_DATAMUTEX = _HOOKAPI_BASE + 11              # 0x8004200B
HOOKERR_INJECTFAILED = _HOOKAPI_BASE + 12           # 0x8004200C
HOOKERR_NONOTIFYWINDOW = _HOOKAPI_BASE + 13         # 0x8004200D
HOOKERR_ALL_SLOTS_USED = _HOOKAPI_BASE + 14         # 0x8004200E
HOOKERR_NOSYSKEYS_WITH_SHIFTKEY = _HOOKAPI_BASE + 15  # 0x8004200F

# ---------------------------------------------------------------------------
# SRCentral::ModeGet — dwEngineFeatures flags
# ---------------------------------------------------------------------------
DGN_SRFEATURE_RELEASE = 0x00000001
DGN_SRFEATURE_INHOUSE = 0x00000002
DGN_SRFEATURE_C_AND_CENABLED = 0x00000004
DGN_SRFEATURE_MULTI_SPEAKER = 0x00000008
DGN_SRFEATURE_MULTI_TOPIC = 0x00000010
DGN_SRFEATURE_DESKTOP_UI = 0x00000020
DGN_SRFEATURE_PLAYBACK_SPEECH = 0x00000040
DGN_SRFEATURE_TTS_ENABLED = 0x00000080
DGN_SRFEATURE_TOPICBLD_ADVANCEDUI = 0x00000100
DGN_SRFEATURE_DELUXE = 0x00000200
DGN_SRFEATURE_PERSONALPLUS = 0x00000400
DGN_SRFEATURE_PERSONAL = 0x00000800
DGN_SRFEATURE_POINTSPEAK = 0x00001000
DGN_SRFEATURE_SERVERONLY = 0x00002000
DGN_SRFEATURE_NETADMIN = 0x00004000
DGN_SRFEATURE_NETCLIENT = 0x00008000
DGN_SRFEATURE_NETDELUXE = 0x00010000
DGN_SRFEATURE_OEM = 0x00020000

# ---------------------------------------------------------------------------
# IDgnSSvcAppTrackingNotifySink — key/script prefix chars
# ---------------------------------------------------------------------------
CH_KEY_PREFIX = 'k'
CH_SCRIPT_PREFIX = 's'

# ---------------------------------------------------------------------------
# IDgnExtModSupHooks — keyboard hook flags
# ---------------------------------------------------------------------------
HOOK_F_SHIFT = 0x01
HOOK_F_ALT = 0x02
HOOK_F_CTRL = 0x04
HOOK_F_RIGHTSHIFT = 0x08
HOOK_F_RIGHTALT = 0x10
HOOK_F_RIGHTCTRL = 0x20
HOOK_F_EXTENDED = 0x40              # use extended keypad version
HOOK_F_DEFERTERMINATION = 0x100
HOOK_F_SYSTEMKEYS = 0x200           # use kbd_event/mouse_event instead of JournalPlayback

# ---------------------------------------------------------------------------
# IDgnSSvcOutputEvent — key generation flags
# ---------------------------------------------------------------------------
GENKEYS_F_SCAN_CODE = 0x10000       # use scan code
GENKEYS_F_UPPERCASE = 0x20000       # uppercase whole string
GENKEYS_F_LOWERCASE = 0x40000       # lowercase whole string
GENKEYS_F_CAPITALIZE = 0x80000      # uppercase first char
GENKEYS_F_VIRTKEY = 0x200000        # is virtkey (else ANSI)
GENKEYS_F_USEKEYPAD = 0x400000      # else WM_CHAR for foreign chars

# ---------------------------------------------------------------------------
# Registry entry flags (RGYF_*)
# ---------------------------------------------------------------------------
RGYF_SCOPEMASK = 0x0007
RGYF_GROUPFLAG = 0x0008
RGYF_TYPEMASK = 0x0030
RGYF_EXTENDMASK = 0x07F0
RGYF_LOCALIZED = 0x0800
RGYF_CHECKMASK = 0x3000
RGYF_SOURCEMASK = 0x0F00

# Scope values
RGYF_USERNAMED = 0x0000
RGYF_GLOBNAMED = 0x0001
RGYF_APPNAMED = 0x0002

# Scope + group composites
RGYF_USERGROUP = RGYF_USERNAMED | RGYF_GROUPFLAG   # 0x0008
RGYF_GLOBGROUP = RGYF_GLOBNAMED | RGYF_GROUPFLAG   # 0x0009
RGYF_APPGROUP = RGYF_APPNAMED | RGYF_GROUPFLAG     # 0x000A

# Type values
RGYF_INT = 0x0000
RGYF_RECT = 0x0010
RGYF_STRING = 0x0020
RGYF_CLASS = 0x0030

# Extended type values (OR'd with base type)
RGYF_DIRECTORY = 0x0040 | RGYF_STRING    # 0x0060
RGYF_FILENAME = 0x0080 | RGYF_STRING     # 0x00A0
RGYF_KEYNAME = 0x00C0 | RGYF_STRING      # 0x00E0
RGYF_GUID = 0x01C0 | RGYF_STRING         # 0x01E0

# Source directory values
RGYF_INBASEDIR = 0x0000
RGYF_INCODEDIR = 0x0100
RGYF_INUSERBASE = 0x0200
RGYF_INUSERDIR = 0x0300
RGYF_INUSERCURRENT = 0x0400
RGYF_INVOCABDIR = 0x0500
RGYF_INHELPDIR = 0x0600
RGYF_INTRAINDIR = 0x0700
RGYF_INSHAREDBASEDIR = 0x0800
RGYF_INDATADIR = 0x0900

# Parameter count check values
RGYF_ONEPARAM = 0x1000
RGYF_TWOPARAMS = 0x2000
RGYF_THREEPARAMS = 0x3000

# ---------------------------------------------------------------------------
# IDgnSRBuildLM — additional
# ---------------------------------------------------------------------------
SRBUILDSIZE_NOSUGGESTION = 0xFFFFFFFF   # DWORD(-1)

# ---------------------------------------------------------------------------
# Miscellaneous constants
# ---------------------------------------------------------------------------
K_N_ERROR_BLOCK_SIZE = 300     # k_nErrorBlockSize
K_MAX_CONTEXT_SIZE = 5         # kMaxContextSize — words passed for prior context
