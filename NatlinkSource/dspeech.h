//
// DSpeech.h : Dragon extensions to the Microsoft SAPI spec.
//
// This file contains the declarations for the interfaces which are
// supported by Dragon NaturallySpeaking but which are not part of
// Microsoft standard SAPI.
//
// (c) Copyright Dragon Systems, Inc. 1998
//

#ifndef DSPEECH_H
#define DSPEECH_H

#include <servprov.h>

// For IDgnSSvcActionNotifySink
#define ACTIONSTATUS_F_ALLOWHEARDWORD 0x2
#define ACTIONSTATUS_F_ALLOWUSERINPUT 0x4

// For IDgnSREngineControl
#define DGNMIC_DISABLED	0
#define DGNMIC_OFF 		1
#define DGNMIC_ON		2
#define DGNMIC_SLEEPING	3
#define DGNMIC_PAUSE	4
#define DGNMIC_RESUME	5

// For IDgnSREngineNotifySink
#define DGNSRAC_BASE 1000
#define DGNSRAC_MICSTATE DGNSRAC_BASE+1
#define DGNSRAC_REGISTRY DGNSRAC_BASE+2
#define DGNSRAC_PLAYBACKDONE DGNSRAC_BASE+3
#define DGNSRAC_TOPIC DGNSRAC_BASE+4
#define DGNSRAC_LEXADD DGNSRAC_BASE+5
#define DGNSRAC_LEXREMOVE DGNSRAC_BASE+6
#define DGNSRSINKFLAG_SENDBEGINUTT 			0x01
#define DGNSRSINKFLAG_SENDENDUTT 			0x02
#define DGNSRSINKFLAG_SENDVUMETER 			0x04
#define DGNSRSINKFLAG_SENDATTRIB 			0x08
#define DGNSRSINKFLAG_SENDINTERFERENCE 		0x10
#define DGNSRSINKFLAG_SENDSOUND 				0x20
#define DGNSRSINKFLAG_SENDJITPAUSED 			0x40
#define DGNSRSINKFLAG_SENDERROR 				0x80
#define DGNSRSINKFLAG_SENDPROGRESS			0x100
#define DGNSRSINKFLAG_SENDMIMICDONE			0x200
#define DGNSRSINKFLAG_SENDALL                0x3FF
#define DGNSRSINKFLAG_DEFAULT (DGNSRSINKFLAG_SENDBEGINUTT|DGNSRSINKFLAG_SENDENDUTT|DGNSRSINKFLAG_SENDATTRIB)
#define DGNSRGRAMSINKFLAG_SENDPHRASESTART	0x1000
#define DGNSRGRAMSINKFLAG_SENDPHRASEHYPO 	0x2000
#define DGNSRGRAMSINKFLAG_SENDPHRASEFINISH 	0x4000
#define DGNSRGRAMSINKFLAG_SENDFOREIGNFINISH	0x8000
#define DGNSRGRAMSINKFLAG_SENDALL            0xF1FF
#define DGNSRGRAMSINKFLAG_DEFAULT (DGNSRGRAMSINKFLAG_SENDPHRASESTART|DGNSRGRAMSINKFLAG_SENDPHRASEFINISH)
#define DGNDICTSINKFLAG_SENDPHRASEFINISH		DGNSRGRAMSINKFLAG_SENDPHRASEFINISH
#define DGNDICTSINKFLAG_SENDFOREIGNFINISH	DGNSRGRAMSINKFLAG_SENDFOREIGNFINISH
#define DGNDICTSINKFLAG_SENDPHRASEHYPO		DGNSRGRAMSINKFLAG_SENDPHRASEHYPO
#define DGNDICTSINKFLAG_SENDPHRASESTART		DGNSRGRAMSINKFLAG_SENDPHRASESTART
#define DGNDICTSINKFLAG_SENDATTRIB			DGNSRSINKFLAG_SENDATTRIB
#define DGNDICTSINKFLAG_SENDINTERFERENCE		DGNSRSINKFLAG_SENDINTERFERENCE
#define DGNDICTSINKFLAG_SENDBEGINUTT			DGNSRSINKFLAG_SENDBEGINUTT
#define DGNDICTSINKFLAG_SENDENDUTT			DGNSRSINKFLAG_SENDENDUTT
#define DGNDICTSINKFLAG_SENDVUMETER			DGNSRSINKFLAG_SENDVUMETER
#define DGNDICTSINKFLAG_SENDERROR			DGNSRSINKFLAG_SENDERROR
#define DGNDICTSINKFLAG_SENDTEXTCHANGED		0x00010000
#define DGNDICTSINKFLAG_SENDTEXTSELCHANGED	0x00020000
#define DGNDICTSINKFLAG_SENDTRAINING		0x00040000
#define DGNDICTSINKFLAG_SENDWARNING			0x00080000
#define DGNDICTSINKFLAG_SENDJITPAUSE		0x00100000
#define DGNDICTSINKFLAG_SENDCORRECTIONHOTKEY 0x00200000
#define DGNDICTSINKFLAG_SENDALL    			0x003F01FF
#define DGNDICTSINKFLAG_DEFAULT (DGNDICTSINKFLAG_SENDTEXTCHANGED|DGNDICTSINKFLAG_SENDTEXTSELCHANGED)

// For IDgnSRParmEnum
#define CBMAX_SUBDIRNAME 9
#define DGNNOTIFICATION_ATTRIB	0x0001
#define DGNNOTIFICATION_UTTBEG	0x0002
#define DGNNOTIFICATION_UTTEND	0x0003
#define DGNNOTIFICATION_VUMETER	0x0004
#define DGNNOTIFICATION_DGNATTRIB 0x0005
#define DGNNOTIFICATION_JITPAUSE	0x0006
#define DGNPAR_BOOL   (1)
#define DGNPAR_INT    (2)
#define DGNPAR_STRING (3)
#define DGNPAR_FLOAT  (4)

// For IDgnSRGramDictation
#define DGNWORDSFLAG_DOIMMED		0x0001

// For IDgnSSvcGUI
#define DGNGUI_SHOWMINIMAL      0x1
#define DGNGUI_SHOWFULL         0x2
#define DGNGUI_SHOWPERMANENT    0x4

// For IDgnSRAudioFileSource
#define DGN_SM_F_MENUACTIVE 1
#define DGN_SM_F_MOVEWINDOW	2
#define DGNUTTFLG_USELABEL 0x0001
#define DGNUTTFLG_DETECTUTT 0x0002
#define DGNUTTFLG_REALTIME 0x0004
#define DGNUTTTYP_COMBINED   0x0000	// .UTD
#define DGNUTTTYP_UTT        0x0001	// .UTT
#define DGNUTTTYP_MSWAV      0x0002	// .WAV
#define DGNUTTTYP_NISTWAV	0x0003	// .NWV

// For IDgnSRWordEnum
#define DGNWORDFLAG_USERADDED		0x00000001
#define DGNWORDFLAG_VARADDED 		0x00000002
#define DGNWORDFLAG_CUSTOMPRON 		0x00000004
#define DGNWORDFLAG_NODELETE 		0x00000008
#define DGNWORDFLAG_PASSIVE_CAP_NEXT	0x00000010
#define DGNWORDFLAG_ACTIVE_CAP_NEXT	0x00000020
#define DGNWORDFLAG_UPPERCASE_NEXT	0x00000040
#define DGNWORDFLAG_LOWERCASE_NEXT	0x00000080
#define DGNWORDFLAG_NO_SPACE_NEXT	0x00000100
#define DGNWORDFLAG_TWO_SPACES_NEXT	0x00000200
#define DGNWORDFLAG_COND_NO_SPACE	0x00000400
#define DGNWORDFLAG_CAP_ALL			0x00000800
#define DGNWORDFLAG_UPPERCASE_ALL	0x00001000
#define DGNWORDFLAG_LOWERCASE_ALL	0x00002000
#define DGNWORDFLAG_NO_SPACE_ALL		0x00004000
#define DGNWORDFLAG_RESET_NO_SPACE	0x00008000
#define DGNWORDFLAG_SWALLOW_PERIOD  	0x00010000
#define DGNWORDFLAG_IS_PERIOD  		0x00020000
#define DGNWORDFLAG_NO_FORMATTING 	0x00040000
#define DGNWORDFLAG_NO_SPACE_CHANGE 	0x00080000
#define DGNWORDFLAG_NO_CAP_CHANGE 	0x00100000
#define DGNWORDFLAG_NO_SPACE_BEFORE 	0x00200000
#define DGNWORDFLAG_RESET_UC_LC_CAPS	0x00400000
#define DGNWORDFLAG_NEW_LINE			0x00800000
#define DGNWORDFLAG_NEW_PARAGRAPH	0x01000000
#define DGNWORDFLAG_TITLE_MODE		0x02000000
#define DGNWORDFLAG_BEGINNING_TITLE_MODE		0x04000000
#define DGNWORDFLAG_SPACE_BAR		0x08000000
#define DGNWORDFLAG_NOT_IN_DICTATION	0x10000000
#define DGNWORDFLAG_GUESSEDPRON         0x20000000
#define DGNWORDFLAG_TOPICADDED		0x40000000
#define DGNWORDTESTFLAG_CASESENSITIVE		0x0001
#define DGNWORDTESTFLAG_DICTONLY				0x0002
#define DGNWORDTESTFLAG_ACTIVEVOCONLY		0x0004
#define DGNTEXTPARSEFLAG_CASESENSITIVE		0x0001
#define DGNTEXTPARSEFLAG_COMMANDS			0x0002
#define DGNTEXTPARSEFLAG_ALLPATHS			0x0004
#define DGNTEXTPARSEFLAG_DONTUSEBDFILTER		0x0008
#define DGNTEXTPARSEFLAG_EXACTMATCH			0x0010
#define DGNTEXTPARSEFLAG_NONCAPMATCH			0x0020

#define TKNFLAG_DEFAULT         0x0000
#define TKNFLAG_BEGINALT        0x0001
#define TKNFLAG_ENDALT          0x0002
#define TKNFLAG_BEGINSEQ        0x0004
#define TKNFLAG_ENDSEQ          0x0008
#define TKNFLAG_JUNK            0x0010
#define TKNFLAG_SENTSTART       0x0020
#define TKNFLAG_INACTIVEVOC     0x0040
#define TKNFLAG_INBACKUPDICT    0x0080

typedef struct
{
	DWORD dwFlags;
	DWORD dwWordNum;
} DgnEngineInfo;
typedef struct
{
	DgnEngineInfo engineInfo;
	DWORD dwSize;
} DgnWordInfo;

// For IDgnSRTraining
#define DGNTRNMODE_NORMAL		0x00000000
#define DGNTRNMODE_CALIBRATE 	0x00000001
#define DGNTRNMODE_CROSSWORD		0x00000002
#define DGNTRNMODE_BATCHWORD		0x00000003
#define DGNTRNMODE_SINGLESET		0x00000004
#define DGNTRNMODE_SHORTBATCH	0x00000005

// For IDgnVCmd
#define DGNVCMDF_STOPONERROR 1
#define DGNVCMDF_REPORTERRORS 2
#define DGNVCMDF_JUSTPARSE 4
#define DGNVCMDF_NOAUTOACTIVATE 8
#define DGNVCMDF_REFCOUNT 0x10
#define DGNVCMDF_GLOBALCMDFILE 0x80000000

// For IDgnVDctOpt
#define VDCTOPT_SELECT_XYZ_ENABLED        0x00000001
#define VDCTOPT_LINE_TERMINATOR        0x00000002
#define VDCTOPT_DICTATION_ONLY        0x00000003

// For IDgnVDctText
#define VDCT_CORRECTIONDIALOG_DEFAULT 0x00000000
#define VDCT_CORRECTIONDIALOG_DBLCLK 0x00000001

// For IDgnSRTopicLM
typedef struct {
DWORD    dwSize;
   WCHAR    szWord[1];
} DGNTOPLMWORDW, * PDGNTOPLMWORDW;
typedef struct {
   DWORD    dwSize;
   CHAR     szWord[1];
} DGNTOPLMWORDA, * PDGNTOPLMWORDA;

// For IDgnSSvcAppTrackingNotifySink
#define CH_KEY_PREFIX _T('k')
#define CH_SCRIPT_PREFIX _T('s')

// For IVDct0TextObsolete
typedef struct {
    DWORD   dwID;
    DWORD   dwStartChar;
    DWORD   dwNumChars;
} VDCTBOOKMARK_OBSOLETE, *PVDCTBOOKMARK_OBSOLETE;

typedef enum 
{
	SAPI_POSTYPE = 1,
} POSTYPE;

typedef struct 
{
	POSTYPE POS_Type;
    VOICEPARTOFSPEECH SAPI_POS;
    unsigned char Dgn_POS[16];
} POSINFO;

// for IDgnVDctNotifySink
#define VDCTNOTIFY_CORRECTION_HOTKEY 1

// for IDgnVDctTranscribe
#define TRANSCRIBEFLAG_ALL_COMMANDS 0
#define TRANSCRIBEFLAG_RESTRICTED_COMMANDS 1
#define TRANSCRIBEFLAG_DICTATION_ONLY 2

// for IDgnSSvcOutputEvent
#define HOOK_F_SHIFT		0x01
#define HOOK_F_ALT			0x02
#define HOOK_F_CTRL			0x04
#define HOOK_F_RIGHTSHIFT	0x08
#define HOOK_F_RIGHTALT		0x10
#define HOOK_F_RIGHTCTRL	0x20
#define HOOK_F_EXTENDED		0x40	// use extended keypad version
#define HOOK_F_DEFERTERMINATION  0x100
#define HOOK_F_SYSTEMKEYS	0x200   // use kbd_event/mouse_event instead of JournalPlayback

#define GENKEYS_F_SCAN_CODE		0x10000L	// use scan code
#define GENKEYS_F_UPPERCASE		0x20000L	// uppercase whole string
#define GENKEYS_F_LOWERCASE		0x40000L	// lowercase whole string
#define GENKEYS_F_CAPITALIZE	0x80000L	// uppercase first char
#define GENKEYS_F_VIRTKEY		0x200000L	// is virtkey (else ANSI)
#define GENKEYS_F_USEKEYPAD		0x400000L	// else WM_CHAR for foreign chars

// for IDgnExtModSupRegistry
#define RGYF_SCOPEMASK  ((WORD)0x0007)
#define RGYF_GROUPFLAG  ((WORD)0x0008)
#define RGYF_TYPEMASK   ((WORD)0x0030)
#define RGYF_EXTENDMASK ((WORD)0x07F0)
#define RGYF_LOCALIZED  ((WORD)0x0800)
#define RGYF_CHECKMASK  ((WORD)0x3000)
#define RGYF_SOURCEMASK ((WORD)0x0F00)

#define RGYF_USERNAMED ((WORD)0x0000)
#define RGYF_GLOBNAMED ((WORD)0x0001)
#define RGYF_APPNAMED  ((WORD)0x0002)

#define RGYF_USERGROUP ( ((WORD)RGYF_USERNAMED | RGYF_GROUPFLAG ))
#define RGYF_GLOBGROUP ( ((WORD)RGYF_GLOBNAMED | RGYF_GROUPFLAG ))
#define RGYF_APPGROUP  ( ((WORD)RGYF_APPNAMED  | RGYF_GROUPFLAG ))

#define RGYF_INT    ((WORD)0x0000)
#define RGYF_RECT   ((WORD)0x0010)
#define RGYF_STRING ((WORD)0x0020)
#define RGYF_CLASS  ((WORD)0x0030)

#define RGYF_DIRECTORY ( ((WORD)0x0040 | RGYF_STRING ))
#define RGYF_FILENAME  ( ((WORD)0x0080 | RGYF_STRING ))
#define RGYF_KEYNAME   ( ((WORD)0x00C0 | RGYF_STRING ))
#define RGYF_GUID      ( ((WORD)0x01C0 | RGYF_STRING ))

#define RGYF_INBASEDIR	  ((WORD)0x0000)
#define RGYF_INCODEDIR	  ((WORD)0x0100)
#define RGYF_INUSERBASE	  ((WORD)0x0200)
#define RGYF_INUSERDIR	  ((WORD)0x0300)
#define RGYF_INUSERCURRENT ((WORD)0x0400)
#define RGYF_INVOCABDIR	  ((WORD)0x0500)
#define RGYF_INHELPDIR	  ((WORD)0x0600)
#define RGYF_INTRAINDIR	  ((WORD)0x0700)
#define RGYF_INSHAREDBASEDIR ((WORD)0x0800)
#define RGYF_INDATADIR ((WORD)0x0900)

#define RGYF_ONEPARAM    ((WORD)0x1000)
#define RGYF_TWOPARAMS   ((WORD)0x2000)
#define RGYF_THREEPARAMS ((WORD)0x3000)


// for IDgnSRResGraph
typedef struct {
	DWORD   dwNextWordNode;
	DWORD   dwUpAlternateWordNode;
	DWORD   dwDownAlternateWordNode;
	DWORD   dwPreviousWordNode;
	DWORD   dwPhonemeNode;
	QWORD   qwStartTime;
	QWORD   qwEndTime;
    QWORD   qwSilenceDuration;
	DWORD   dwWordScore;
	WORD      wVolume;
	WORD      wPitch;
	VOICEPARTOFSPEECH   pos;
	DWORD   dwCFGParse;
	DWORD   dwCue;
	} DGNSRRESWORDNODE, * PDGNSRRESWORDNODE;

// for IDgnSRBuildLM
#define   SRBUILDSLOT_USER			1
#define   SRBUILDSLOT_VAR			2
#define   SRBUILDTYPE_NEW			1
#define   SRBUILDTYPE_INCREMENTAL	2
#define   SRBUILDSIZE_NOSUGGESTION	DWORD(-1)

// for IVoiceDictation0
#define DGNVDCTRF_IGNOREHOTKEYS ((DWORD)0x4)

///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////

#define   DGNSRHDRFLAG_STATICXYZGRAMMAR      SETBIT(26)
    
#define   DGNSRHDRFLAG_DONTUSESTATEWORDS    	SETBIT(27)
#define   DGNSRHDRFLAG_DONTUSENOISE        	SETBIT(28)
#define   DGNSRHDRFLAG_USELMSCORE        	SETBIT(29)
#define   DGNSRHDRFLAG_ADDTODICTSTATE        SETBIT(30)
    
#define   DGNSRHDRFLAG_LANGUAGEMODELON       SETBIT(31)

#define  DGNSRCORCONFIDENCE_LMONLY          (0x8001)
		
typedef struct {
	DWORD    message;
 	DWORD    paramL;
	DWORD    paramH;
} HOOK_EVENTMSG;

typedef HOOK_EVENTMSG *PHOOK_EVENTMSG;

#define k_nErrorBlockSize 300

typedef struct {
	int m_nCode; // The message code.
	char m_szParms[ k_nErrorBlockSize ];
} DGN_ERROR_A;
	
typedef struct { // same as DGN_ERROR_A but unicode
	int m_nCode;
	WCHAR m_szParms[ k_nErrorBlockSize ];
} DGN_ERROR_W;

typedef struct {
	DWORD dwState;
} FORMATSTATE, * PFORMATSTATE;

typedef struct {
	DWORD dwSetState;
	DWORD dwResetState;
	DWORD dwFlags;
} FORMATCODES, * PFORMATCODES;

typedef struct {
    DWORD   dwStart;		// absolute offset of the word/phrase
    DWORD   dwNumChars;		// number of characters in the word/phrase
    QWORD   qDuration;		// duration in milliseconds for this 
							// word/phrase
} NOWPLAYINGINFO;

#ifdef _S_UNICODE
#define DGN_ERROR DGN_ERROR_W
#else
#define DGN_ERROR DGN_ERROR_A
#endif

// IDgnSSvcActionNotifySink

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcActionNotifySink

DEFINE_GUID(IID_IDgnSSvcActionNotifySink,
	0xdd108202, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcActionNotifySink , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (PlaybackDone) (THIS_ DWORD ) PURE;
	STDMETHOD (PlaybackAborted) (THIS_ DWORD, HRESULT ) PURE;
	STDMETHOD (ExecutionDone) (THIS_ DWORD ) PURE;
	STDMETHOD (ExecutionStatus) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (ExecutionAborted) (THIS_ DWORD, HRESULT, DWORD ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSSvcOutputEvent	IDgnSSvcOutputEventW
 #define IID_IDgnSSvcOutputEvent	IID_IDgnSSvcOutputEventW
#else
 #define IDgnSSvcOutputEvent	IDgnSSvcOutputEventA
 #define IID_IDgnSSvcOutputEvent	IID_IDgnSSvcOutputEventA
#endif // _S_UNICODE

// IDgnSSvcOutputEventA

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcOutputEventA

DEFINE_GUID( IID_IDgnSSvcOutputEventA, 
	0xdd108201, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcOutputEventA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IDgnSSvcActionNotifySink* ) PURE;
	STDMETHOD (PlayString) (THIS_ const char*, DWORD, DWORD, DWORD, 
		DWORD* ) PURE;
	STDMETHOD (NameFromKey) (THIS_ DWORD, DWORD, DWORD, DWORD, 
		char*, DWORD* ) PURE;
	STDMETHOD (PlayEvents) (THIS_ DWORD, const HOOK_EVENTMSG [], DWORD,
		DWORD) PURE;
};

// IDgnSSvcOutputEventW

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcOutputEventW

DEFINE_GUID( IID_IDgnSSvcOutputEventW, 
	0xdd109201, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcOutputEventW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IDgnSSvcActionNotifySink* ) PURE;
	STDMETHOD (PlayString) (THIS_ const wchar_t*, DWORD, DWORD, DWORD, 
		DWORD* ) PURE;
	STDMETHOD (NameFromKey) (THIS_ DWORD, DWORD, DWORD, DWORD, 
		wchar_t*, DWORD* ) PURE;
	STDMETHOD (PlayEvents) (THIS_ DWORD, const HOOK_EVENTMSG [], DWORD,
		DWORD) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSSvcInterpreter	IDgnSSvcInterpreterW
 #define IID_IDgnSSvcInterpreter	IID_IDgnSSvcInterpreterW
#else
 #define IDgnSSvcInterpreter	IDgnSSvcInterpreterA
 #define IID_IDgnSSvcInterpreter	IID_IDgnSSvcInterpreterA
#endif // _S_UNICODE

// IDgnSSvcInterpreterA

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcInterpreterA

DEFINE_GUID( IID_IDgnSSvcInterpreterA, 
	0xdd108203, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcInterpreterA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IDgnSSvcActionNotifySink* ) PURE;
	STDMETHOD (CheckScript) (THIS_ const char*, DWORD*, DWORD* ) PURE;
	STDMETHOD (ExecuteScript) (THIS_  const char*, DWORD*, DWORD*,
		const char*, DWORD ) PURE;
	STDMETHOD (ExecuteScriptWithListResults) (THIS_ const char*, DWORD, 
		const char*, DWORD*, DWORD*, const char *, DWORD ) PURE;
};

// IDgnSSvcInterpreterW

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcInterpreterW

DEFINE_GUID( IID_IDgnSSvcInterpreterW, 
	0xdd109203, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcInterpreterW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IDgnSSvcActionNotifySink* ) PURE;
	STDMETHOD (CheckScript) (THIS_ const wchar_t*, DWORD*, DWORD* ) PURE;
	STDMETHOD (ExecuteScript) (THIS_  const wchar_t*, DWORD*, DWORD*,
		const wchar_t*, DWORD ) PURE;
	STDMETHOD (ExecuteScriptWithListResults) (THIS_ const wchar_t*, DWORD, 
		const wchar_t*, DWORD*, DWORD*, const wchar_t*, DWORD ) PURE;
};

// IDgnAppSupportA

#undef   INTERFACE
#define  INTERFACE   IDgnAppSupportA

DEFINE_GUID( IID_IDgnAppSupportA,
	0xdd108300, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);


DECLARE_INTERFACE_ (IDgnAppSupportA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IServiceProvider* ) PURE;
	STDMETHOD (AddProcess) (THIS_ DWORD, const char*, const char*, 
		DWORD ) PURE;
	STDMETHOD (EndProcess) (THIS_ DWORD ) PURE;
	STDMETHOD (UnRegister) (THIS) PURE;
};

// IDgnAppSupportW

#undef   INTERFACE
#define  INTERFACE   IDgnAppSupportW

DEFINE_GUID( IID_IDgnAppSupportW,
	0xdd109300, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnAppSupportW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IServiceProvider* ) PURE;
	STDMETHOD (AddProcess) (THIS_ DWORD, const wchar_t*, const wchar_t*, 
		DWORD ) PURE;
	STDMETHOD (EndProcess) (THIS_ DWORD ) PURE;
	STDMETHOD (UnRegister) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IDgnAppSupport	  IDgnAppSupportW
 #define IID_IDgnAppSupport  IID_IDgnAppSupportW
#else
 #define IDgnAppSupport	  IDgnAppSupportA
 #define IID_IDgnAppSupport  IID_IDgnAppSupportA
#endif // _S_UNICODE

// IDgnSREngineControlA

#undef   INTERFACE
#define  INTERFACE   IDgnSREngineControlA

DEFINE_GUID( IID_IDgnSREngineControlA, 
	0xdd108000, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSREngineControlA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (GetVersion) (THIS_ WORD*, WORD*, WORD* ) PURE;
	STDMETHOD (GetMicState) (THIS_ WORD* ) PURE;
	STDMETHOD (SetMicState) (THIS_ WORD, BOOL ) PURE;
	STDMETHOD (SaveSpeaker) (THIS_ BOOL ) PURE;
	STDMETHOD (GetChangedInfo) (THIS_ BOOL*, DWORD* ) PURE;
	STDMETHOD (Resume) (THIS_ QWORD ) PURE;
	STDMETHOD (RecognitionMimic) (THIS_ DWORD, SDATA, DWORD ) PURE;
	STDMETHOD (Preinitialize) (THIS) PURE;
	STDMETHOD (SpeakerRename) (THIS_ const char*, const char* ) PURE;
};

// IDgnSREngineControlW

#undef   INTERFACE
#define  INTERFACE   IDgnSREngineControlW

DEFINE_GUID( IID_IDgnSREngineControlW, 
	0xdd109000, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSREngineControlW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (GetVersion) (THIS_ WORD*, WORD*, WORD* ) PURE;
	STDMETHOD (GetMicState) (THIS_ WORD* ) PURE;
	STDMETHOD (SetMicState) (THIS_ WORD, BOOL ) PURE;
	STDMETHOD (SaveSpeaker) (THIS_ BOOL ) PURE;
	STDMETHOD (GetChangedInfo) (THIS_ BOOL*, DWORD* ) PURE;
	STDMETHOD (Resume) (THIS_ QWORD ) PURE;
	STDMETHOD (RecognitionMimic) (THIS_ DWORD, SDATA, DWORD ) PURE;
	STDMETHOD (Preinitialize) (THIS) PURE;
	STDMETHOD (SpeakerRename) (THIS_ const wchar_t*, const wchar_t* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSREngineControl	IDgnSREngineControlW
 #define IID_IDgnSREngineControl	IID_IDgnSREngineControlW
#else
 #define IDgnSREngineControl	IDgnSREngineControlA
 #define IID_IDgnSREngineControl	IID_IDgnSREngineControlA
#endif // _S_UNICODE

// IDgnErrorA

#undef   INTERFACE
#define  INTERFACE   IDgnErrorA

DEFINE_GUID( IID_IDgnErrorA, 
	0xdd108005, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnErrorA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (LastErrorGet) (THIS_ DGN_ERROR_A* ) PURE;
	STDMETHOD (ErrorMessageGet) (THIS_ char*, DWORD, DWORD* ) PURE;
};

// IDgnErrorW

#undef   INTERFACE
#define  INTERFACE   IDgnErrorW

DEFINE_GUID( IID_IDgnErrorW, 
	0xdd109005, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnErrorW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (LastErrorGet) (THIS_ DGN_ERROR_W* ) PURE;
	STDMETHOD (ErrorMessageGet) (THIS_ wchar_t*, DWORD, DWORD* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnError IDgnErrorW
 #define IID_IDgnError IID_IDgnErrorW
#else
 #define IDgnError IDgnErrorA
 #define IID_IDgnError IID_IDgnErrorA
#endif // _S_UNICODE


// RW added ANSI/UNICODE versions of the interface
// IDgnSREngineNotifySinkA

#undef   INTERFACE
#define  INTERFACE   IDgnSREngineNotifySinkA

DEFINE_GUID( IID_IDgnSREngineNotifySinkA,
	0xdd108001, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSREngineNotifySinkA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (AttribChanged2) (THIS_ DWORD ) PURE;
	STDMETHOD (Paused) (THIS_ QWORD ) PURE;
	STDMETHOD (MimicDone) (THIS_ DWORD, LPUNKNOWN ) PURE;
	STDMETHOD (ErrorHappened) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (Progress) (THIS_ int, const char* ) PURE;
};

// IDgnSREngineNotifySinkW

#undef   INTERFACE
#define  INTERFACE   IDgnSREngineNotifySinkW

DEFINE_GUID( IID_IDgnSREngineNotifySinkW,
	0xdd109001, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSREngineNotifySinkW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (AttribChanged2) (THIS_ DWORD ) PURE;
	STDMETHOD (Paused) (THIS_ QWORD ) PURE;
	STDMETHOD (MimicDone) (THIS_ DWORD, LPUNKNOWN ) PURE;
	STDMETHOD (ErrorHappened) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (Progress) (THIS_ int, const wchar_t* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSREngineNotifySink IDgnSREngineNotifySinkW
 #define IID_IDgnSREngineNotifySink IID_IDgnSREngineNotifySinkW
#else
 #define IDgnSREngineNotifySink IDgnSREngineNotifySinkA
 #define IID_IDgnSREngineNotifySink IID_IDgnSREngineNotifySinkA
#endif // _S_UNICODE


// IDgnGetSinkFlags

#undef   INTERFACE
#define  INTERFACE   IDgnGetSinkFlags

DEFINE_GUID( IID_IDgnGetSinkFlags,
	0xdd108010, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnGetSinkFlags , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (SinkFlagsGet) (THIS_ DWORD* ) PURE;
};

// Just in case anyone uses the wide/ansi versions
#define IDgnGetSinkFlagsW       IDgnGetSinkFlags
#define IID_IDgnGetSinkFlagsW   IID_IDgnGetSinkFlags
#define IDgnGetSinkFlagskA      IDgnGetSinkFlags
#define IID_IDgnGetSinkFlagsA   IID_IDgnGetSinkFlags

// IDgnSpeechSite

#undef   INTERFACE
#define  INTERFACE   IDgnSpeechSite

DEFINE_GUID( IID_IDgnSpeechSite, 
	// TODO _ GUID is bogus
	0xdd108202, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSpeechSite , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (QuerySiteInterface) (THIS_ CLSID*, IID*, IUnknown** ) PURE;
};

// IDgnSRGramCommon

#undef   INTERFACE
#define  INTERFACE   IDgnSRGramCommon

DEFINE_GUID(IID_IDgnSRGramCommon,
	0xdd108006, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRGramCommon , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (SpecialGrammar) (THIS_ BOOL ) PURE;
	STDMETHOD (Identify) (THIS_ GUID* ) PURE;
};

// IDgnSRGramDictationA

#undef   INTERFACE
#define  INTERFACE   IDgnSRGramDictationA

DEFINE_GUID(IID_IDgnSRGramDictationA,
	0xdd108015, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRGramDictationA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (RecentBufferFlush) (THIS) PURE;
	STDMETHOD (RecentBufferCommit) (THIS) PURE;
	STDMETHOD (CommittedFlush) (THIS) PURE;
	STDMETHOD (Words) (THIS_ SDATA, DWORD ) PURE;
};

// IDgnSRGramDictationW

#undef   INTERFACE
#define  INTERFACE   IDgnSRGramDictationW

DEFINE_GUID(IID_IDgnSRGramDictationW,
	0xdd109015, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRGramDictationW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (RecentBufferFlush) (THIS) PURE;
	STDMETHOD (RecentBufferCommit) (THIS) PURE;
	STDMETHOD (CommittedFlush) (THIS) PURE;
	STDMETHOD (Words) (THIS_ SDATA, DWORD ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRGramDictation	IDgnSRGramDictationW
 #define IID_IDgnSRGramDictation IID_IDgnSRGramDictationW
#else
 #define IDgnSRGramDictation	IDgnSRGramDictationA
 #define IID_IDgnSRGramDictation	IID_IDgnSRGramDictationA
#endif // _S_UNICODE

// IDgnSRResRerecognizeA

#undef   INTERFACE
#define  INTERFACE   IDgnSRResRerecognizeA

DEFINE_GUID(IID_IDgnSRResRerecognizeA,
	0xdd108007, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRResRerecognizeA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Rerecognize) (THIS_ GUID, LPUNKNOWN* ) PURE;
	STDMETHOD (RerecognizeGrammars) (THIS_ GUID*, DWORD, DWORD, 
		LPUNKNOWN* ) PURE;
	STDMETHOD (StopRerecognize) (THIS) PURE;
};

// IDgnSRResRerecognizeW

#undef   INTERFACE
#define  INTERFACE   IDgnSRResRerecognizeW

DEFINE_GUID(IID_IDgnSRResRerecognizeW,
	0xdd109007, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRResRerecognizeW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Rerecognize) (THIS_ GUID, LPUNKNOWN* ) PURE;
	STDMETHOD (RerecognizeGrammars) (THIS_ GUID*, DWORD, DWORD,
		LPUNKNOWN* ) PURE;
	STDMETHOD (StopRerecognize) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRResRerecognize IDgnSRResRerecognizeW
 #define IID_IDgnSRResRerecognize IID_IDgnSRResRerecognizeW
#else
 #define IDgnSRResRerecognize IDgnSRResRerecognizeA
 #define IID_IDgnSRResRerecognize IID_IDgnSRResRerecognizeA
#endif // _S_UNICODE

// IDgnSRResGraphA

#undef   INTERFACE
#define  INTERFACE   IDgnSRResGraphA

DEFINE_GUID(IID_IDgnSRResGraphA,
	0xdd108020, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRResGraphA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (GetWordNode) (THIS_ DWORD, PDGNSRRESWORDNODE, BYTE *, DWORD, DWORD * ) PURE;
};

// IDgnSRResGraphW

#undef   INTERFACE
#define  INTERFACE   IDgnSRResGraphW

DEFINE_GUID(IID_IDgnSRResGraphW,
	0xdd109020, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRResGraphW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (GetWordNode) (THIS_ DWORD, PDGNSRRESWORDNODE, BYTE *, DWORD, DWORD * ) PURE;
};	

#ifdef _S_UNICODE
 #define IDgnSRResGraph	IDgnSRResGraphW
 #define IID_IDgnSRResGraph IID_IDgnSRResGraphW
#else
 #define IDgnSRResGraph	IDgnSRResGraphA
 #define IID_IDgnSRResGraph	IID_IDgnSRResGraphA
#endif // _S_UNICODE

// IDgnSSvcDialogs

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcDialogs

DEFINE_GUID( IID_IDgnSSvcDialogs, 
	0xdd108209, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcDialogs , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (UserNew) (THIS_ HWND ) PURE;
	STDMETHOD (UserOpen) (THIS_ HWND ) PURE;
	STDMETHOD (UserSave) (THIS_ HWND ) PURE;
	STDMETHOD (TopicNew) (THIS_ HWND ) PURE;
	STDMETHOD (TopicOpen) (THIS_ HWND ) PURE;
	STDMETHOD (TopicEdit) (THIS_ HWND ) PURE;
	STDMETHOD (TopicBuild) (THIS_ HWND ) PURE;
    STDMETHOD (ToolsNewCommandWizard) (THIS_ HWND, DWORD,
		const char*, BOOL) PURE;
    STDMETHOD (ToolsEditCommandWizard) (THIS_ HWND, const char*,
		const char*, const char*, BOOL ) PURE;
    STDMETHOD (ToolsTrainWords) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsFindNewWords) (THIS_ HWND, const char* ) PURE;
	STDMETHOD (ToolsAudioSetupWizard) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsGeneralTraining) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsSettings) (THIS_ HWND ) PURE;
	STDMETHOD (HelpTopics) (THIS_ HWND ) PURE;
	STDMETHOD (HelpAbout) (THIS_ HWND ) PURE;
};

// IDgnSSvcDialogsObsolete

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcDialogsObsolete

DEFINE_GUID( IID_IDgnSSvcDialogsObsolete, 
	0xdd108208, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcDialogsObsolete , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (UserNew) (THIS_ HWND ) PURE;
	STDMETHOD (UserOpen) (THIS_ HWND ) PURE;
	STDMETHOD (UserSave) (THIS_ HWND ) PURE;
	STDMETHOD (TopicNew) (THIS_ HWND ) PURE;
	STDMETHOD (TopicOpen) (THIS_ HWND ) PURE;
	STDMETHOD (TopicEdit) (THIS_ HWND ) PURE;
	STDMETHOD (TopicBuild) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsNewCommandWizard) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsEditCommandWizard) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsTrainWords) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsFindNewWords) (THIS_ HWND, const char* ) PURE;
	STDMETHOD (ToolsAudioSetupWizard) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsGeneralTraining) (THIS_ HWND ) PURE;
	STDMETHOD (ToolsSettings) (THIS_ HWND ) PURE;
	STDMETHOD (HelpTopics) (THIS_ HWND ) PURE;
	STDMETHOD (HelpAbout) (THIS_ HWND ) PURE;
};

// IDgnSSvcGUI

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcGUI

DEFINE_GUID( IID_IDgnSSvcGUI, 
	0xdd10820a, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcGUI , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

    STDMETHOD (Lock) (THIS_ DWORD ) PURE;
    STDMETHOD (Unlock) (THIS_ DWORD ) PURE;
};

// IDGnSSvcMiscSystem

#undef   INTERFACE
#define  INTERFACE   IDGnSSvcMiscSystem

DEFINE_GUID( IID_IDgnSSvcMiscSystem, 
	0xdd108205, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcMiscSystem , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;


	STDMETHOD (QuerySystemMode) (THIS_ DWORD* ) PURE;
	STDMETHOD (CancelMode) (THIS) PURE;
	STDMETHOD (SendMessageI) (THIS_ HWND, DWORD, BOOL, DWORD,
		DWORD, const unsigned char*, DWORD, DWORD* ) PURE;
	STDMETHOD (SendMessageO) (THIS_ HWND, DWORD, BOOL, DWORD, DWORD,
		unsigned char*, DWORD, DWORD* ) PURE;
	STDMETHOD (SendMessageIO) (THIS_ HWND, DWORD, BOOL, DWORD, DWORD,
		unsigned char *, DWORD, DWORD* ) PURE;
	STDMETHOD (DictationWindow) (THIS_ const char* ) PURE;
	STDMETHOD (CompatibilityModulesLoad) (THIS_ BOOL ) PURE;
};

// IDgnSRAudioFileSourceA

#undef   INTERFACE
#define  INTERFACE   IDgnSRAudioFileSourceA

DEFINE_GUID(IID_IDgnSRAudioFileSourceA,
	0xdd108008, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRAudioFileSourceA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (FileNameSet) (THIS_ DWORD, const char* ) PURE;
	STDMETHOD (EnableSet) (THIS_ BOOL ) PURE;
	STDMETHOD (PlayListSet) (THIS_ DWORD*, DWORD ) PURE;
	STDMETHOD (FileClose) (THIS) PURE;
};

// IDgnSRAudioFileSourceW

#undef   INTERFACE
#define  INTERFACE   IDgnSRAudioFileSourceW

DEFINE_GUID(IID_IDgnSRAudioFileSourceW,
	0xdd109008, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRAudioFileSourceW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (FileNameSet) (THIS_ DWORD, const wchar_t* ) PURE;
	STDMETHOD (EnableSet) (THIS_ BOOL ) PURE;
	STDMETHOD (PlayListSet) (THIS_ DWORD*, DWORD ) PURE;
	STDMETHOD (FileClose) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRAudioFileSource IDgnSRAudioFileSourceW
 #define IID_IDgnSRAudioFileSource IID_IDgnSRAudioFileSourceW
#else
 #define IDgnSRAudioFileSource IDgnSRAudioFileSourceA
 #define IID_IDgnSRAudioFileSource IID_IDgnSRAudioFileSourceA
#endif // _S_UNICODE

// IDgnSRAudioFileSinkA

#undef   INTERFACE
#define  INTERFACE   IDgnSRAudioFileSinkA

DEFINE_GUID(IID_IDgnSRAudioFileSinkA,
	0xdd108016, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRAudioFileSinkA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (FileNameSet) (THIS_ DWORD, DWORD, const char* ) PURE;
	STDMETHOD (EnableSet) (THIS_ BOOL ) PURE;
	STDMETHOD (FileClose) (THIS) PURE;
};

// IDgnSRAudioFileSinkW

#undef   INTERFACE
#define  INTERFACE   IDgnSRAudioFileSinkW

DEFINE_GUID(IID_IDgnSRAudioFileSinkW,
	0xdd109016, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRAudioFileSinkW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (FileNameSet) (THIS_ DWORD, DWORD, const wchar_t* ) PURE;
	STDMETHOD (EnableSet) (THIS_ BOOL ) PURE;
	STDMETHOD (FileClose) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRAudioFileSink IDgnSRAudioFileSinkW
 #define IID_IDgnSRAudioFileSink IID_IDgnSRAudioFileSinkW
#else
 #define IDgnSRAudioFileSink IDgnSRAudioFileSinkA
 #define IID_IDgnSRAudioFileSink IID_IDgnSRAudioFileSinkA
#endif // _S_UNICODE

// IDgnSRWordEnumA

#undef   INTERFACE
#define  INTERFACE   IDgnSRWordEnumA

DEFINE_GUID(IID_IDgnSRWordEnumA,
	0xdd108009, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRWordEnumA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

    STDMETHOD (Next) (THIS_ DWORD, BYTE*, DWORD*, DWORD, DWORD* ) PURE;
    STDMETHOD (Skip) (THIS_ DWORD ) PURE;
    STDMETHOD (Reset) (THIS) PURE;
    STDMETHOD (Clone) (THIS_ IDgnSRWordEnumA **) PURE;
	STDMETHOD (GetCount) (THIS_ DWORD* ) PURE;
};

// IDgnSRWordEnumW

#undef   INTERFACE
#define  INTERFACE   IDgnSRWordEnumW

DEFINE_GUID(IID_IDgnSRWordEnumW,
	0xdd109009, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRWordEnumW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

    STDMETHOD (Next) (THIS_ DWORD, BYTE*, DWORD*, DWORD, DWORD* ) PURE;
    STDMETHOD (Skip) (THIS_ DWORD ) PURE;
    STDMETHOD (Reset) (THIS) PURE;
    STDMETHOD (Clone) (THIS_ IDgnSRWordEnumW** ) PURE;
	STDMETHOD (GetCount) (THIS_ DWORD* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRWordEnum	  IDgnSRWordEnumW
 #define IID_IDgnSRWordEnum  IID_IDgnSRWordEnumW
#else
 #define IDgnSRWordEnum	  IDgnSRWordEnumA
 #define IID_IDgnSRWordEnum  IID_IDgnSRWordEnumA
#endif // _S_UNICODE

// IDgnSRWordPrefixEnumA

#undef   INTERFACE
#define  INTERFACE   IDgnSRWordPrefixEnumA

DEFINE_GUID(IID_IDgnSRWordPrefixEnumA,
	0xdd108017, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRWordPrefixEnumA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

    STDMETHOD (Next) (THIS_ DWORD, BYTE*, DWORD*, DWORD, DWORD* ) PURE;
    STDMETHOD (Skip) (THIS_ DWORD ) PURE;
    STDMETHOD (Reset) (THIS_ const char* ) PURE;
    STDMETHOD (Clone) (THIS_ IDgnSRWordPrefixEnumA** ) PURE;
	STDMETHOD (GetCount) (THIS_ DWORD* ) PURE;
};

// IDgnSRWordPrefixEnumW

#undef   INTERFACE
#define  INTERFACE   IDgnSRWordPrefixEnumW

DEFINE_GUID(IID_IDgnSRWordPrefixEnumW,
	0xdd109017, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRWordPrefixEnumW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

    STDMETHOD (Next) (THIS_ DWORD, BYTE*, DWORD*, DWORD, DWORD* ) PURE;
    STDMETHOD (Skip) (THIS_ DWORD ) PURE;
    STDMETHOD (Reset) (THIS_ const wchar_t* ) PURE;
    STDMETHOD (Clone) (THIS_ IDgnSRWordPrefixEnumW** ) PURE;
	STDMETHOD (GetCount) (THIS_ DWORD* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRWordPrefixEnum	  IDgnSRWordPrefixEnumW
 #define IID_IDgnSRWordPrefixEnum  IID_IDgnSRWordPrefixEnumW
#else
 #define IDgnSRWordPrefixEnum	  IDgnSRWordPrefixEnumA
 #define IID_IDgnSRWordPrefixEnum  IID_IDgnSRWordPrefixEnumA
#endif // _S_UNICODE

// IDgnSRTokenizerA

#undef   INTERFACE
#define  INTERFACE   IDgnSRTokenizerA

DEFINE_GUID(IID_IDgnSRTokenizerA,
	0xdd108004, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTokenizerA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (TextParse) (THIS_ DWORD, const char*, DWORD,
		SDATA*, DWORD* ) PURE;
	STDMETHOD (TextParseWithContext) (THIS_ DWORD,
		const char*, const char*, const char*, DWORD,
		SDATA*, DWORD* ) PURE;
};

// IDgnSRTokenizerW

#undef   INTERFACE
#define  INTERFACE   IDgnSRTokenizerW

DEFINE_GUID(IID_IDgnSRTokenizerW,
	0xdd109004, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTokenizerW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (TextParse) (THIS_ DWORD, const wchar_t*,
		DWORD, SDATA*, DWORD* ) PURE;
	STDMETHOD (TextParseWithContext) (THIS_ DWORD,
		const wchar_t*, const wchar_t*, const wchar_t*,
		DWORD, SDATA*, DWORD* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRTokenizer	  IDgnSRTokenizerW
 #define IID_IDgnSRTokenizer  IID_IDgnSRTokenizerW
#else
 #define IDgnSRTokenizer	  IDgnSRTokenizerA
 #define IID_IDgnSRTokenizer  IID_IDgnSRTokenizerA
#endif // _S_UNICODE

// IDgnSRLexiconA

#undef   INTERFACE
#define  INTERFACE   IDgnSRLexiconA

DEFINE_GUID(IID_IDgnSRLexiconA,
	0xdd108011, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRLexiconA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (WordEnum) (THIS_ IDgnSRWordEnumA** ) PURE;
	STDMETHOD (WordPrefixEnum) (THIS_ IDgnSRWordPrefixEnumA** ) PURE;
	STDMETHOD (WordTest) (THIS_ DWORD, const char*, BOOL* ) PURE;
	STDMETHOD (WordFromPrefix) (THIS_ const char*, DWORD, DWORD,
		char*, DWORD* ) PURE;
	STDMETHOD (WordFromPron) (THIS_ const char*, DWORD, DWORD,
		char*, DWORD* ) PURE;
};

// IDgnSRLexiconW

#undef   INTERFACE
#define  INTERFACE   IDgnSRLexiconW

DEFINE_GUID(IID_IDgnSRLexiconW,
	0xdd109011, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRLexiconW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (WordEnum) (THIS_ IDgnSRWordEnumW** ) PURE;
	STDMETHOD (WordPrefixEnum) (THIS_ IDgnSRWordPrefixEnumW** ) PURE;
	STDMETHOD (WordTest) (THIS_ DWORD, const wchar_t*, BOOL* ) PURE;
	STDMETHOD (WordFromPrefix) (THIS_ const wchar_t*,
		DWORD, DWORD, wchar_t*, DWORD* ) PURE;
	STDMETHOD (WordFromPron) (THIS_ const wchar_t*, DWORD, DWORD,
		wchar_t*, DWORD* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRLexicon	  IDgnSRLexiconW
 #define IID_IDgnSRLexicon  IID_IDgnSRLexiconW
#else
 #define IDgnSRLexicon	  IDgnSRLexiconA
 #define IID_IDgnSRLexicon  IID_IDgnSRLexiconA
#endif // _S_UNICODE

// IDgnSRTopicControlA

#undef   INTERFACE
#define  INTERFACE   IDgnSRTopicControlA

DEFINE_GUID(IID_IDgnSRTopicControlA,
	0xdd108012, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTopicControlA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (New) (THIS_ const char*, const char* ) PURE;
	STDMETHOD (Delete) (THIS_ const char* ) PURE;
	STDMETHOD (Enum) (THIS_ const char*, char**, DWORD* ) PURE;
	STDMETHOD (Copy) (THIS_ const char*, const char* ) PURE;
	STDMETHOD (Query) (THIS_ char*, DWORD, DWORD* ) PURE;
	STDMETHOD (Select) (THIS_ const char * ) PURE;
	STDMETHOD (Rename) (THIS_ const char*, const char* ) PURE;
};

// IDgnSRTopicControlW

#undef   INTERFACE
#define  INTERFACE   IDgnSRTopicControlW

DEFINE_GUID(IID_IDgnSRTopicControlW,
	0xdd109012, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTopicControlW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (New) (THIS_ const wchar_t*, const wchar_t* ) PURE;
	STDMETHOD (Delete) (THIS_ const wchar_t* ) PURE;
	STDMETHOD (Enum) (THIS_ const wchar_t*, wchar_t**, DWORD* ) PURE;
	STDMETHOD (Copy) (THIS_ const wchar_t*, const wchar_t* ) PURE;
	STDMETHOD (Query) (THIS_ wchar_t*, DWORD, DWORD* ) PURE;
	STDMETHOD (Select) (THIS_ const wchar_t* ) PURE;
	STDMETHOD (Rename) (THIS_ const wchar_t*, const wchar_t* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRTopicControl	  IDgnSRTopicControlW
 #define IID_IDgnSRTopicControl  IID_IDgnSRTopicControlW
#else
 #define IDgnSRTopicControl	  IDgnSRTopicControlA
 #define IID_IDgnSRTopicControl  IID_IDgnSRTopicControlA
#endif // _S_UNICODE

// IDgnSRTopicLMA

#undef   INTERFACE
#define  INTERFACE   IDgnSRTopicLMA

DEFINE_GUID(IID_IDgnSRTopicLMA,
	0xdd108013, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTopicLMA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (LMCreate) (THIS_ DWORD, SDATA, SDATA ) PURE;
	STDMETHOD (LMGetMaxWords) (THIS_ DWORD* ) PURE;
};

// IDgnSRTopicLMW

#undef   INTERFACE
#define  INTERFACE   IDgnSRTopicLMW

DEFINE_GUID(IID_IDgnSRTopicLMW,
	0xdd109013, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTopicLMW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (LMCreate) (THIS_ DWORD, SDATA, SDATA ) PURE;
	STDMETHOD (LMGetMaxWords) (THIS_ DWORD* ) PURE;
};

#ifdef  _S_UNICODE
#define  DGNTOPLMWORD      DGNTOPLMWORDW
#define  PDGNTOPLMWORD     PDGNTOPLMWORDW
#else
#define  DGNTOPLMWORD      DGNTOPLMWORDA
#define  PDGNTOPLMWORD     PDGNTOPLMWORDA
#endif  // _S_UNICODE

#ifdef _S_UNICODE
 #define IDgnSRTopicLM	  IDgnSRTopicLMW
 #define IID_IDgnSRTopicLM  IID_IDgnSRTopicLMW
#else
 #define IDgnSRTopicLM	  IDgnSRTopicLMA
 #define IID_IDgnSRTopicLM  IID_IDgnSRTopicLMA
#endif // _S_UNICODE

// IDgnSRBuildLMA

#undef   INTERFACE
#define  INTERFACE   IDgnSRBuildLMA

DEFINE_GUID(IID_IDgnSRBuildLMA,
	0xdd10801e, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRBuildLMA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (MaxUniqueWordsGet) (THIS_ DWORD* ) PURE;
	STDMETHOD (BuildStart) (THIS_ DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (BuildEnd) (THIS_ DWORD * ) PURE;
	STDMETHOD (BuildCancel) (THIS) PURE;
	STDMETHOD (IsBuildActive) (THIS_ BOOL* ) PURE;
	STDMETHOD (UniqueWordsAdd) (THIS_ DWORD, SDATA ) PURE;
	STDMETHOD (WordStreamAdd) (THIS_ SDATA, BOOL ) PURE;
};

// IDgnSRBuildLMW

#undef   INTERFACE
#define  INTERFACE   IDgnSRBuildLMW

DEFINE_GUID(IID_IDgnSRBuildLMW,
	0xdd10901e, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRBuildLMW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (MaxUniqueWordsGet) (THIS_ DWORD* ) PURE;
	STDMETHOD (BuildStart) (THIS_ DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (BuildEnd) (THIS_ DWORD * ) PURE;
	STDMETHOD (BuildCancel) (THIS) PURE;
	STDMETHOD (IsBuildActive) (THIS_ BOOL* ) PURE;
	STDMETHOD (UniqueWordsAdd) (THIS_ DWORD, SDATA ) PURE;
	STDMETHOD (WordStreamAdd) (THIS_ SDATA, BOOL ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRBuildLM	  IDgnSRBuildLMW
 #define IID_IDgnSRBuildLM  IID_IDgnSRBuildLMW
#else
 #define IDgnSRBuildLM	  IDgnSRBuildLMA
 #define IID_IDgnSRBuildLM  IID_IDgnSRBuildLMA
#endif // _S_UNICODE

// IDgnSRTopic2A

#undef   INTERFACE
#define  INTERFACE   IDgnSRTopic2A

DEFINE_GUID(IID_IDgnSRTopic2A,
	0xdd108021, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTopic2A , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (New) (THIS_ const char *, const char *, const char * ) PURE;
	STDMETHOD (Select) (THIS_ const char *, const char * ) PURE;
	STDMETHOD (SpeakerCopy) (THIS_ const char *, const char * ) PURE;
};

// IDgnSRTopic2W

#undef   INTERFACE
#define  INTERFACE   IDgnSRTopic2W

DEFINE_GUID(IID_IDgnSRTopic2W,
	0xdd109021, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTopic2W , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (New) (THIS_ const wchar_t *, const wchar_t *, const wchar_t * ) PURE;
	STDMETHOD (Select) (THIS_ const wchar_t *, const wchar_t * ) PURE;
	STDMETHOD (SpeakerCopy) (THIS_ const wchar_t *, const wchar_t * ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRTopic2	  IDgnSRTopic2W
 #define IID_IDgnSRTopic2  IID_IDgnSRTopic2W
#else
 #define IDgnSRTopic2	  IDgnSRTopic2A
 #define IID_IDgnSRTopic2  IID_IDgnSRTopic2A
#endif // _S_UNICODE

// IDgnSRLargeTopicLMObsoleteA

#undef   INTERFACE
#define  INTERFACE   IDgnSRLargeTopicLMObsoleteA

DEFINE_GUID(IID_IDgnSRLargeTopicLMObsoleteA,
	0xdd108018, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRLargeTopicLMObsoleteA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (MaxUniqueWordsGet) (THIS_ DWORD* ) PURE;
	STDMETHOD (BuildStart) (THIS_ DWORD ) PURE;
	STDMETHOD (BuildEnd) (THIS) PURE;
	STDMETHOD (BuildCancel) (THIS) PURE;
	STDMETHOD (IsBuildActive) (THIS_ BOOL* ) PURE;
	STDMETHOD (BuildTopicModeGet) (THIS_ DWORD* ) PURE;
	STDMETHOD (UniqueWordsAdd) (THIS_ DWORD, SDATA ) PURE;
	STDMETHOD (WordStreamAdd) (THIS_ SDATA, BOOL ) PURE;
};

// IDgnSRLargeTopicLMObsoleteW

#undef   INTERFACE
#define  INTERFACE   IDgnSRLargeTopicLMObsoleteW

DEFINE_GUID(IID_IDgnSRLargeTopicLMObsoleteW,
	0xdd109017, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRLargeTopicLMObsoleteW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (MaxUniqueWordsGet) (THIS_ DWORD* ) PURE;
	STDMETHOD (BuildStart) (THIS_ DWORD ) PURE;
	STDMETHOD (BuildEnd) (THIS) PURE;
	STDMETHOD (BuildCancel) (THIS) PURE;
	STDMETHOD (IsBuildActive) (THIS_ BOOL* ) PURE;
	STDMETHOD (BuildTopicModeGet) (THIS_ DWORD* ) PURE;
	STDMETHOD (UniqueWordsAdd) (THIS_ DWORD, SDATA ) PURE;
	STDMETHOD (WordStreamAdd) (THIS_ SDATA, BOOL ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRLargeTopicLMObsolete	  IDgnSRLargeTopicLMObsoleteW
 #define IID_IDgnSRLargeTopicLMObsolete  IID_IDgnSRLargeTopicLMObsoleteW
#else
 #define IDgnSRLargeTopicLMObsolete	  IDgnSRLargeTopicLMObsoleteA
 #define IID_IDgnSRLargeTopicLMObsolete  IID_IDgnSRLargeTopicLMObsoleteA
#endif // _S_UNICODE

// IDgnSSvcAppTrackingNotifySinkA

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcAppTrackingNotifySinkA

DEFINE_GUID( IID_IDgnSSvcAppTrackingNotifySinkA, 
	0xdd108207, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcAppTrackingNotifySinkA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (AppLoaded) (THIS_ DWORD, const char*, const char* ) PURE;
	STDMETHOD (AppTerminated) (THIS_ DWORD, const char*, const char* ) PURE;
};

// IDgnSSvcAppTrackingNotifySinkW

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcAppTrackingNotifySinkW

DEFINE_GUID( IID_IDgnSSvcAppTrackingNotifySinkW, 
	0xdd109207, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcAppTrackingNotifySinkW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (AppLoaded) (THIS_ DWORD, const wchar_t*,
		const wchar_t* ) PURE;
	STDMETHOD (AppTerminated) (THIS_ DWORD, const wchar_t*,
		const wchar_t* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSSvcAppTrackingNotifySink	IDgnSSvcAppTrackingNotifySinkW
 #define IID_IDgnSSvcAppTrackingNotifySink	IID_IDgnSSvcAppTrackingNotifySinkW
#else
 #define IDgnSSvcAppTrackingNotifySink	IDgnSSvcAppTrackingNotifySinkA
 #define IID_IDgnSSvcAppTrackingNotifySink	IID_IDgnSSvcAppTrackingNotifySinkA
#endif // _S_UNICODE

// IDgnSSvcTrackingA

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcTrackingA

DEFINE_GUID( IID_IDgnSSvcTrackingA, 
	0xdd108204, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcTrackingA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IDgnSSvcActionNotifySink*,
		IUnknown*, IDgnSSvcAppTrackingNotifySinkA* ) PURE;
	STDMETHOD (DoTracking) (THIS_ DWORD ) PURE;
	STDMETHOD (DoAction) (THIS_ const char*, DWORD, const char*,
		DWORD, const BYTE*, DWORD ) PURE;
};

// IDgnSSvcTrackingW

#undef   INTERFACE
#define  INTERFACE   IDgnSSvcTrackingW

DEFINE_GUID( IID_IDgnSSvcTrackingW, 
	0xdd109204, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcTrackingW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IDgnSSvcActionNotifySink*,
		IUnknown*, IDgnSSvcAppTrackingNotifySinkW* ) PURE;
	STDMETHOD (DoTracking) (THIS_ DWORD ) PURE;
	STDMETHOD (DoAction) (THIS_ const wchar_t*, DWORD,
		const wchar_t*, DWORD, const BYTE*, DWORD ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSSvcTracking	IDgnSSvcTrackingW
 #define IID_IDgnSSvcTracking	IID_IDgnSSvcTrackingW
#else
 #define IDgnSSvcTracking	IDgnSSvcTrackingA
 #define IID_IDgnSSvcTracking	IID_IDgnSSvcTrackingA
#endif // _S_UNICODE

// IDgnSRTrainingA

#undef   INTERFACE
#define  INTERFACE   IDgnSRTrainingA

DEFINE_GUID(IID_IDgnSRTrainingA,
	0xdd108014, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTrainingA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (TrainingModeSet) (THIS_ DWORD ) PURE;
	STDMETHOD (TrainingModeGet) (THIS_ DWORD*, DWORD*, DWORD* ) PURE;
	STDMETHOD (TrainingPerform) (THIS) PURE;
	STDMETHOD (TrainingCancel) (THIS) PURE;
	STDMETHOD (TotalCountGet) (THIS_ BOOL*, DWORD*, DWORD* ) PURE;
};

#define IDgnSRTraining	  IDgnSRTrainingA
#define IID_IDgnSRTraining  IID_IDgnSRTrainingA

// IDgnSpeechServices

#undef   INTERFACE
#define  INTERFACE   IDgnSpeechServices

DEFINE_GUID( IID_IDgnSpeechServices,
	0xdd108200, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSpeechServices , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Dummy) (THIS) PURE;
};

// IDgnVCmdFileA

#undef   INTERFACE
#define  INTERFACE   IDgnVCmdFileA

DEFINE_GUID( IID_IDgnVCmdFileA, 
	0xdd108500, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVCmdFileA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ LPUNKNOWN, LPUNKNOWN ) PURE;
	STDMETHOD (CreateMenus) (THIS_ const char*, DWORD,
		DWORD*, DWORD*, DWORD ) PURE;
	STDMETHOD (DestroyMenus) (THIS_ const char* ) PURE;
	STDMETHOD (IsFileLoaded) (THIS_ const char*, DWORD* ) PURE;
	STDMETHOD (GetErrorInfo) (THIS_ DWORD, DWORD*, DWORD*, DWORD* ) PURE;
	STDMETHOD (DoAction) (THIS_ const char*, DWORD, const char*,
		DWORD, const BYTE*, const char*, DWORD ) PURE;
	STDMETHOD (AutoActivate) (THIS) PURE;
};

// IDgnVCmdFileW

#undef   INTERFACE
#define  INTERFACE   IDgnVCmdFileW

DEFINE_GUID( IID_IDgnVCmdFileW, 
	0xdd109500, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVCmdFileW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ LPUNKNOWN, LPUNKNOWN ) PURE;
	STDMETHOD (CreateMenus) (THIS_ const wchar_t*, DWORD,
		DWORD*, DWORD*, DWORD ) PURE;
	STDMETHOD (DestroyMenus) (THIS_ const wchar_t* ) PURE;
	STDMETHOD (IsFileLoaded) (THIS_ const wchar_t*, DWORD* ) PURE;
	STDMETHOD (GetErrorInfo) (THIS_ DWORD, DWORD*, DWORD*, DWORD* ) PURE;
	STDMETHOD (DoAction) (THIS_ const wchar_t*, DWORD,
		const wchar_t*, DWORD, const BYTE*, const wchar_t*, DWORD ) PURE;
	STDMETHOD (AutoActivate) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IDgnVCmdFile IDgnVCmdFileW
 #define IID_IDgnVCmdFile IID_IDgnVCmdFileW
#else
 #define IDgnVCmdFile IDgnVCmdFileA
 #define IID_IDgnVCmdFile IID_IDgnVCmdFileA
#endif // _S_UNICODE

// IDgnVDctGUI

#undef   INTERFACE
#define  INTERFACE   IDgnVDctGUI

DEFINE_GUID( IID_IDgnVDctGUI, 
	0xdd108403, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctGUI , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Show) (THIS_ HWND ) PURE;
	STDMETHOD (Hide) (THIS) PURE;
	STDMETHOD (Move) (THIS_ RECT ) PURE;
};

// IDgnVDctOptionsA

#undef   INTERFACE
#define  INTERFACE   IDgnVDctOptionsA

DEFINE_GUID( IID_IDgnVDctOptionsA, 
	0xdd108406, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctOptionsA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ DWORD* ) PURE;
	STDMETHOD (UnRegister) (THIS_ DWORD ) PURE;
    STDMETHOD (DWordOptionSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (DWordOptionGet) (THIS_ DWORD, DWORD* ) PURE;
	STDMETHOD (StringOptionSet) (THIS_ DWORD, const char* ) PURE;
	STDMETHOD (StringOptionGet) (THIS_ DWORD, char*, DWORD, DWORD* ) PURE;
};

// IDgnVDctOptionsW

#undef   INTERFACE
#define  INTERFACE   IDgnVDctOptionsW

DEFINE_GUID( IID_IDgnVDctOptionsW, 
	0xdd109406, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctOptionsW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ DWORD* ) PURE;
	STDMETHOD (UnRegister) (THIS_ DWORD ) PURE;
	STDMETHOD (DWordOptionSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (DWordOptionGet) (THIS_ DWORD, DWORD* ) PURE;
	STDMETHOD (StringOptionSet) (THIS_ DWORD, const wchar_t* ) PURE;
	STDMETHOD (StringOptionGet) (THIS_ DWORD, wchar_t*, DWORD, 
		DWORD* ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnVDctOptions	  IDgnVDctOptionsW
 #define IID_IDgnVDctOptions  IID_IDgnVDctOptionsW
#else
 #define IDgnVDctOptions	  IDgnVDctOptionsA
 #define IID_IDgnVDctOptions  IID_IDgnVDctOptionsA
#endif // _S_UNICODE

// IDgnVDctTextA

#undef   INTERFACE
#define  INTERFACE   IDgnVDctTextA

DEFINE_GUID(IID_IDgnVDctTextA,
	0xdd10840b, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctTextA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (VisibleTextSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (VisibleTextGet) (THIS_ DWORD*, DWORD* ) PURE;
    STDMETHOD (ThatGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (CorrectionDialog) (THIS_ HWND, DWORD ) PURE;
	STDMETHOD (RecentBufferCommit) (THIS) PURE;
};

// IDgnVDctTextW

#undef   INTERFACE
#define  INTERFACE   IDgnVDctTextW

DEFINE_GUID(IID_IDgnVDctTextW,
	0xdd10940b, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctTextW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (VisibleTextSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (VisibleTextGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (ThatGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (CorrectionDialog) (THIS_ HWND, DWORD ) PURE;
	STDMETHOD (RecentBufferCommit) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IDgnVDctText	  IDgnVDctTextW
 #define IID_IDgnVDctText  IID_IDgnVDctTextW
#else
 #define IDgnVDctText	  IDgnVDctTextA
 #define IID_IDgnVDctText  IID_IDgnVDctTextA
#endif // _S_UNICODE

// IDgnVDctTextObsolete2A

#undef   INTERFACE
#define  INTERFACE   IDgnVDctTextObsolete2A

DEFINE_GUID(IID_IDgnVDctTextObsolete2A,
	0xdd108409, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctTextObsolete2A , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (VisibleTextSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (VisibleTextGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (CorrectionDialog) (THIS_ HWND, DWORD ) PURE;
	STDMETHOD (RecentBufferCommit) (THIS) PURE;
};

// IDgnVDctTextObsolete2W

#undef   INTERFACE
#define  INTERFACE   IDgnVDctTextObsolete2W

DEFINE_GUID(IID_IDgnVDctTextObsolete2W,
	0xdd109409, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctTextObsolete2W , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (VisibleTextSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (VisibleTextGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (CorrectionDialog) (THIS_ HWND, DWORD ) PURE;
	STDMETHOD (RecentBufferCommit) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IDgnVDctTextObsolete2   IDgnVDctTextObsolete2W
 #define IID_IDgnVDctTextObsolete2  IID_IDgnVDctTextObsolete2W
#else
 #define IDgnVDctTextObsolete2	  IDgnVDctTextObsolete2A
 #define IID_IDgnVDctTextObsolete2  IID_IDgnVDctTextObsolete2A
#endif // _S_UNICODE

// IDgnVDctTextObsoleteA

#undef   INTERFACE
#define  INTERFACE   IDgnVDctTextObsoleteA

DEFINE_GUID(IID_IDgnVDctTextObsoleteA,
	0xdd108404, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctTextObsoleteA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (VisibleTextSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (VisibleTextGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (CorrectionDialog) (THIS_ HWND ) PURE;
	STDMETHOD (RecentBufferCommit) (THIS) PURE;
};

// IDgnVDctTextObsoleteW

#undef   INTERFACE
#define  INTERFACE   IDgnVDctTextObsoleteW

DEFINE_GUID(IID_IDgnVDctTextObsoleteW,
	0xdd109404, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctTextObsoleteW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (VisibleTextSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (VisibleTextGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (CorrectionDialog) (THIS_ HWND ) PURE;
	STDMETHOD (RecentBufferCommit) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IDgnVDctTextObsolete	  IDgnVDctTextObsoleteW
 #define IID_IDgnVDctTextObsolete  IID_IDgnVDctTextObsoleteW
#else
 #define IDgnVDctTextObsolete	  IDgnVDctTextObsoleteA
 #define IID_IDgnVDctTextObsolete  IID_IDgnVDctTextObsoleteA
#endif // _S_UNICODE

// IDgnVDctNotifySinkObsolete

#undef   INTERFACE
#define  INTERFACE   IDgnVDctNotifySinkObsolete

DEFINE_GUID(IID_IDgnVDctNotifySinkObsolete,
	0xdd108405, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctNotifySinkObsolete , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (ErrorHappened) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (WarningHappened) (THIS_ LPUNKNOWN ) PURE;
};

// IDgnVDctNotifySink

#undef   INTERFACE
#define  INTERFACE   IDgnVDctNotifySink

DEFINE_GUID(IID_IDgnVDctNotifySink,
	0xdd10840c, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctNotifySink , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (ErrorHappened) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (WarningHappened) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (JITPause) (THIS) PURE;
	STDMETHOD (HotKeyHappened) (THIS_ DWORD ) PURE;

};

// IDgnVDctPlaybackNotifySink

#undef   INTERFACE
#define  INTERFACE   IDgnVDctPlaybackNotifySink

DEFINE_GUID(IID_IDgnVDctPlaybackNotifySink,
	0xdd108408, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctPlaybackNotifySink , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Beginning) (THIS) PURE;
	STDMETHOD (Stopped) (THIS) PURE;
	STDMETHOD (NowPlaying) (THIS_ DWORD, NOWPLAYINGINFO* ) PURE;
	STDMETHOD (NoSpeech) (THIS_ DWORD, DWORD, DWORD ) PURE;
};

// IDgnVDctPlayback

#undef   INTERFACE
#define  INTERFACE   IDgnVDctPlayback

DEFINE_GUID( IID_IDgnVDctPlayback, 
	0xdd108407, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctPlayback , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ IDgnVDctPlaybackNotifySink*,
		DWORD* ) PURE;
	STDMETHOD (UnRegister) (THIS_ DWORD ) PURE;
	STDMETHOD (Begin) (THIS_ DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (Stop) (THIS) PURE;
	STDMETHOD (BrakePlayback) (THIS) PURE;
	STDMETHOD (AccelPlayback) (THIS) PURE;
	STDMETHOD (SettingSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (SettingGet) (THIS_ DWORD, DWORD* ) PURE;
};

// IDgnWordStuffW

#undef   INTERFACE
#define  INTERFACE   IDgnWordStuffW

DEFINE_GUID( IID_IDgnWordStuffW, 
	0xdd109019, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnWordStuffW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (AddPron) (THIS_ VOICECHARSET, const WCHAR*,
		const WCHAR*, VOICEPARTOFSPEECH, BYTE*, DWORD ) PURE;
	STDMETHOD (GetPron) (THIS_ VOICECHARSET, const WCHAR*,
		WORD, WCHAR*, DWORD, DWORD*, VOICEPARTOFSPEECH*, BYTE*,
		DWORD, DWORD* ) PURE;
	STDMETHOD (RemovePron) (THIS_ const WCHAR*, WORD ) PURE;
};

// IDgnWordStuffA

#undef   INTERFACE
#define  INTERFACE   IDgnWordStuffA

DEFINE_GUID( IID_IDgnWordStuffA, 
	0xdd108019, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnWordStuffA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (AddPron) (THIS_ VOICECHARSET, const char*,
		const char*, VOICEPARTOFSPEECH, BYTE*, DWORD ) PURE;
	STDMETHOD (GetPron) (THIS_ VOICECHARSET, const char*,
		WORD, char*, DWORD, DWORD*, VOICEPARTOFSPEECH*, BYTE*,
		DWORD, DWORD* ) PURE;
	STDMETHOD (RemovePron) (THIS_ const char*, WORD ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnWordStuff	  IDgnWordStuffW
 #define IID_IDgnWordStuff IID_IDgnWordStuffW
#else
 #define IDgnWordStuff	  IDgnWordStuffA
 #define IID_IDgnWordStuff IID_IDgnWordStuffA
#endif // _S_UNICODE

// IDgnSRGramSelectA

#undef   INTERFACE
#define  INTERFACE   IDgnSRGramSelectA

DEFINE_GUID(IID_IDgnSRGramSelectA,
	0xdd10801a, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRGramSelectA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (WordsSet) (THIS_ SDATA ) PURE;
	STDMETHOD (WordsChange) (THIS_ DWORD, DWORD, SDATA ) PURE;
	STDMETHOD (WordsDelete) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (WordsInsert) (THIS_ DWORD, SDATA ) PURE;
	STDMETHOD (WordsGet) (THIS_ PSDATA ) PURE;
};

// IDgnSRGramSelectW

#undef   INTERFACE
#define  INTERFACE   IDgnSRGramSelectW

DEFINE_GUID(IID_IDgnSRGramSelectW,
	0xdd10901a, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRGramSelectW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (WordsSet) (THIS_ SDATA ) PURE;
	STDMETHOD (WordsChange) (THIS_ DWORD, DWORD, SDATA ) PURE;
	STDMETHOD (WordsDelete) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (WordsInsert) (THIS_ DWORD, SDATA ) PURE;
	STDMETHOD (WordsGet) (THIS_ PSDATA ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRGramSelect	IDgnSRGramSelectW
 #define IID_IDgnSRGramSelect IID_IDgnSRGramSelectW
#else
 #define IDgnSRGramSelect	IDgnSRGramSelectA
 #define IID_IDgnSRGramSelect	IID_IDgnSRGramSelectA
#endif // _S_UNICODE

// IDgnSRResSelect

#undef   INTERFACE
#define  INTERFACE   IDgnSRResSelect

DEFINE_GUID(IID_IDgnSRResSelect,
	0xdd10801b, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRResSelect , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (GetInfo) (THIS_ GUID, DWORD, DWORD*, DWORD*, DWORD* ) PURE;
};

// IVDct0NotifySinkA

#undef   INTERFACE
#define  INTERFACE   IVDct0NotifySinkA

DEFINE_GUID( IID_IVDct0NotifySinkA, 
	0xdd108401, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IVDct0NotifySinkA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Command) (THIS_ DWORD ) PURE;
	STDMETHOD (TextSelChanged) (THIS) PURE;
	STDMETHOD (TextChanged) (THIS_ DWORD ) PURE;
	STDMETHOD (TextBookmarkChanged) (THIS_ DWORD ) PURE;
	STDMETHOD (PhraseStart) (THIS) PURE;
	STDMETHOD (PhraseFinish) (THIS_ DWORD, PSRPHRASEA ) PURE;
	STDMETHOD (PhraseHypothesis) (THIS_ DWORD, PSRPHRASEA ) PURE;
	STDMETHOD (UtteranceBegin) (THIS) PURE;
	STDMETHOD (UtteranceEnd) (THIS) PURE;
	STDMETHOD (VUMeter) (THIS_ WORD ) PURE;
	STDMETHOD (AttribChanged) (THIS_ DWORD ) PURE;
	STDMETHOD (Interference) (THIS_ DWORD ) PURE;
	STDMETHOD (Training) (THIS_ DWORD ) PURE;
	STDMETHOD (Dictating) (THIS_ const char*, BOOL ) PURE;
};

// IVDct0NotifySinkW

#undef   INTERFACE
#define  INTERFACE   IVDct0NotifySinkW

DEFINE_GUID( IID_IVDct0NotifySinkW, 
	0xdd109401, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IVDct0NotifySinkW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Command) (THIS_ DWORD ) PURE;
	STDMETHOD (TextSelChanged) (THIS) PURE;
	STDMETHOD (TextChanged) (THIS_ DWORD ) PURE;
	STDMETHOD (TextBookmarkChanged) (THIS_ DWORD ) PURE;
	STDMETHOD (PhraseStart) (THIS) PURE;
	STDMETHOD (PhraseFinish) (THIS_ DWORD, PSRPHRASEW ) PURE;
	STDMETHOD (PhraseHypothesis) (THIS_ DWORD, PSRPHRASEW ) PURE;
	STDMETHOD (UtteranceBegin) (THIS) PURE;
	STDMETHOD (UtteranceEnd) (THIS) PURE;
	STDMETHOD (VUMeter) (THIS_ WORD ) PURE;
	STDMETHOD (AttribChanged) (THIS_ DWORD ) PURE;
	STDMETHOD (Interference) (THIS_ DWORD ) PURE;
	STDMETHOD (Training) (THIS_ DWORD ) PURE;
	STDMETHOD (Dictating) (THIS_ const WCHAR*, BOOL ) PURE;
};

#ifdef _S_UNICODE
 #define IVDct0NotifySink	IVDct0NotifySinkW
 #define IID_IVDct0NotifySink	IID_IVDct0NotifySinkW
#else
 #define IVDct0NotifySink	IVDct0NotifySinkA
 #define IID_IVDct0NotifySink	IID_IVDct0NotifySinkA
#endif // _S_UNICODE

// IVoiceDictation0A

#undef   INTERFACE
#define  INTERFACE   IVoiceDictation0A

DEFINE_GUID(IID_IVoiceDictation0A,
	0xdd108400, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IVoiceDictation0A , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ const char*, const char*, LPUNKNOWN,
		const char*, IUnknown*, GUID, DWORD ) PURE;
	STDMETHOD (SiteInfoGet) (THIS_ const char*, PVDSITEINFOA ) PURE;
	STDMETHOD (SiteInfoSet) (THIS_ const char*, PVDSITEINFOA ) PURE;
	STDMETHOD (SessionSerialize) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (TopicEnum) (THIS_ PVDCTTOPICA*, DWORD* ) PURE;
	STDMETHOD (TopicAddString) (THIS_ const char*, LANGUAGEA*, 
		const char** ) PURE;
	STDMETHOD (TopicAddGrammar) (THIS_ const char*, SDATA ) PURE;
	STDMETHOD (TopicRemove) (THIS_ const char* ) PURE;
	STDMETHOD (TopicSerialize) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (TopicDeserialize) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (Activate) (THIS_ HWND ) PURE;
	STDMETHOD (Deactivate) (THIS) PURE;
};

// IVoiceDictation0W

#undef   INTERFACE
#define  INTERFACE   IVoiceDictation0W

DEFINE_GUID(IID_IVoiceDictation0W,
	0xdd109400, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IVoiceDictation0W , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Register) (THIS_ const WCHAR*, const WCHAR*, LPUNKNOWN,
		const WCHAR*, IUnknown*, GUID, DWORD ) PURE;
	STDMETHOD (SiteInfoGet) (THIS_ const WCHAR*, PVDSITEINFOA ) PURE;
	STDMETHOD (SiteInfoSet) (THIS_ const WCHAR*, PVDSITEINFOA ) PURE;
	STDMETHOD (SessionSerialize) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (TopicEnum) (THIS_ PVDCTTOPICA*, DWORD* ) PURE;
	STDMETHOD (TopicAddString) (THIS_ const WCHAR*, LANGUAGEA*, 
		const WCHAR** ) PURE;
	STDMETHOD (TopicAddGrammar) (THIS_ const WCHAR*, SDATA ) PURE;
	STDMETHOD (TopicRemove) (THIS_ const WCHAR* ) PURE;
	STDMETHOD (TopicSerialize) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (TopicDeserialize) (THIS_ LPUNKNOWN ) PURE;
	STDMETHOD (Activate) (THIS_ HWND ) PURE;
	STDMETHOD (Deactivate) (THIS) PURE;
};

#ifdef _S_UNICODE
 #define IVoiceDictation0 IVoiceDictation0W
 #define IID_IVoiceDictation0 IID_IVoiceDictation0W
#else
 #define IVoiceDictation0 IVoiceDictation0A
 #define IID_IVoiceDictation0 IID_IVoiceDictation0A
#endif // _S_UNICODE

// IVDct0TextA

#undef   INTERFACE
#define  INTERFACE   IVDct0TextA

DEFINE_GUID(IID_IVDct0TextA,
	0xdd10840a, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IVDct0TextA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Lock) (THIS) PURE;
	STDMETHOD (UnLock) (THIS) PURE;
	STDMETHOD (TextGet) (THIS_ DWORD, DWORD, PSDATA ) PURE;
	STDMETHOD (TextSet) (THIS_ DWORD, DWORD, const char*, DWORD ) PURE;
	STDMETHOD (TextMove) (THIS_ DWORD, DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (TextRemove) (THIS_ DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (TextSelSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (TextSelGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (GetChanges) (THIS_ DWORD*, DWORD*, DWORD*, DWORD* ) PURE;
	STDMETHOD (BookmarkAdd) (THIS_ PVDCTBOOKMARK ) PURE;
	STDMETHOD (BookmarkRemove) (THIS_ DWORD ) PURE;
	STDMETHOD (BookmarkMove) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (BookmarkQuery) (THIS_ DWORD, PVDCTBOOKMARK ) PURE;
	STDMETHOD (BookmarkEnum) (THIS_ DWORD, DWORD, PVDCTBOOKMARK*, 
		DWORD* ) PURE;
	STDMETHOD (Hint) (THIS_ const char* ) PURE;
	STDMETHOD (Words) (THIS_ const char* ) PURE;
	STDMETHOD (ResultsGet) (THIS_ DWORD, DWORD, DWORD*, DWORD*, 
		LPUNKNOWN* ) PURE;
	STDMETHOD (AutoLockSet) (THIS_ BOOL ) PURE;
	STDMETHOD (AutoLockGet) (THIS_ BOOL* ) PURE;
};

// IVDct0TextW

#undef   INTERFACE
#define  INTERFACE   IVDct0TextW

DEFINE_GUID(IID_IVDct0TextW,
	0xdd10940a, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IVDct0TextW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Lock) (THIS) PURE;
	STDMETHOD (UnLock) (THIS) PURE;
	STDMETHOD (TextGet) (THIS_ DWORD, DWORD, PSDATA ) PURE;
	STDMETHOD (TextSet) (THIS_ DWORD, DWORD, const WCHAR*, DWORD ) PURE;
	STDMETHOD (TextMove) (THIS_ DWORD, DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (TextRemove) (THIS_ DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (TextSelSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (TextSelGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (GetChanges) (THIS_ DWORD*, DWORD*, DWORD*, DWORD* ) PURE;
	STDMETHOD (BookmarkAdd) (THIS_ PVDCTBOOKMARK ) PURE;
	STDMETHOD (BookmarkRemove) (THIS_ DWORD ) PURE;
	STDMETHOD (BookmarkMove) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (BookmarkQuery) (THIS_ DWORD, PVDCTBOOKMARK ) PURE;
	STDMETHOD (BookmarkEnum) (THIS_ DWORD, DWORD, PVDCTBOOKMARK*, 
		DWORD* ) PURE;
	STDMETHOD (Hint) (THIS_ const WCHAR* ) PURE;
	STDMETHOD (Words) (THIS_ const WCHAR* ) PURE;
	STDMETHOD (ResultsGet) (THIS_ DWORD, DWORD, DWORD*, DWORD*, 
		LPUNKNOWN* ) PURE;
	STDMETHOD (AutoLockSet) (THIS_ BOOL ) PURE;
	STDMETHOD (AutoLockGet) (THIS_ BOOL* ) PURE;
};

#ifdef _S_UNICODE
 #define IVDct0Text IVDct0TextW
 #define IID_IVDct0Text IID_IVDct0TextW
#else
 #define IVDct0Text IVDct0TextA
 #define IID_IVDct0Text IID_IVDct0TextA
#endif // _S_UNICODE

// IVDct0TextObsoleteA

#undef   INTERFACE
#define  INTERFACE   IVDct0TextObsoleteA

DEFINE_GUID(IID_IVDct0TextObsoleteA,
	0xdd108402, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IVDct0TextObsoleteA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Lock) (THIS) PURE;
	STDMETHOD (UnLock) (THIS) PURE;
	STDMETHOD (TextGet) (THIS_ DWORD, DWORD, PSDATA ) PURE;
	STDMETHOD (TextSet) (THIS_ DWORD, DWORD, const char*, DWORD ) PURE;
	STDMETHOD (TextMove) (THIS_ DWORD, DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (TextRemove) (THIS_ DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (TextSelSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (TextSelGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (GetChanges) (THIS_ DWORD*, DWORD*, DWORD*, DWORD* ) PURE;
	STDMETHOD (BookmarkAdd) (THIS_ PVDCTBOOKMARK_OBSOLETE ) PURE;
	STDMETHOD (BookmarkRemove) (THIS_ DWORD ) PURE;
	STDMETHOD (BookmarkMove) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (BookmarkQuery) (THIS_ DWORD, PVDCTBOOKMARK_OBSOLETE ) PURE;
	STDMETHOD (BookmarkEnum) (THIS_ DWORD, DWORD, 
		PVDCTBOOKMARK_OBSOLETE*, DWORD* ) PURE;
	STDMETHOD (Hint) (THIS_ const char* ) PURE;
	STDMETHOD (Words) (THIS_ const char* ) PURE;
	STDMETHOD (ResultsGet) (THIS_ DWORD, DWORD, DWORD*, DWORD*, 
		LPUNKNOWN* ) PURE;
	STDMETHOD (AutoLockSet) (THIS_ BOOL ) PURE;
	STDMETHOD (AutoLockGet) (THIS_ BOOL* ) PURE;
};

// IVDct0TextObsoleteW

#undef   INTERFACE
#define  INTERFACE   IVDct0TextObsoleteW

DEFINE_GUID(IID_IVDct0TextObsoleteW,
	0xdd109402, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IVDct0TextObsoleteW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (Lock) (THIS) PURE;
	STDMETHOD (UnLock) (THIS) PURE;
	STDMETHOD (TextGet) (THIS_ DWORD, DWORD, PSDATA ) PURE;
	STDMETHOD (TextSet) (THIS_ DWORD, DWORD, const WCHAR*, DWORD ) PURE;
	STDMETHOD (TextMove) (THIS_ DWORD, DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (TextRemove) (THIS_ DWORD, DWORD, DWORD ) PURE;
	STDMETHOD (TextSelSet) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (TextSelGet) (THIS_ DWORD*, DWORD* ) PURE;
	STDMETHOD (GetChanges) (THIS_ DWORD*, DWORD*, DWORD*, DWORD* ) PURE;
	STDMETHOD (BookmarkAdd) (THIS_ PVDCTBOOKMARK_OBSOLETE ) PURE;
	STDMETHOD (BookmarkRemove) (THIS_ DWORD ) PURE;
	STDMETHOD (BookmarkMove) (THIS_ DWORD, DWORD ) PURE;
	STDMETHOD (BookmarkQuery) (THIS_ DWORD, PVDCTBOOKMARK_OBSOLETE ) PURE;
	STDMETHOD (BookmarkEnum) (THIS_ DWORD, DWORD, 
		PVDCTBOOKMARK_OBSOLETE*, DWORD* ) PURE;
	STDMETHOD (Hint) (THIS_ const WCHAR* ) PURE;
	STDMETHOD (Words) (THIS_ const WCHAR* ) PURE;
	STDMETHOD (ResultsGet) (THIS_ DWORD, DWORD, DWORD*, DWORD*, 
		LPUNKNOWN* ) PURE;
	STDMETHOD (AutoLockSet) (THIS_ BOOL ) PURE;
	STDMETHOD (AutoLockGet) (THIS_ BOOL* ) PURE;
};

#ifdef _S_UNICODE
 #define IVDct0TextObsolete IVDct0TextObsoleteW
 #define IID_IVDct0TextObsolete IID_IVDct0TextObsoleteW
#else
 #define IVDct0TextObsolete IVDct0TextObsoleteA
 #define IID_IVDct0TextObsolete IID_IVDct0TextObsoleteA
#endif // _S_UNICODE

#ifdef _S_UNICODE
#define PVDSITEINFO PVDSITEINFOW
#define VDSITEINFO VDSITEINFOW
#else
#define PVDSITEINFO PVDSITEINFOA
#define VDSITEINFO VDSITEINFOA
#endif

#ifdef _S_UNICODE
#define PVDCTTOPIC PVDCTTOPICW
#define VDCTTOPIC VDCTTOPICW
#else
#define PVDCTTOPIC PVDCTTOPICA
#define VDCTTOPIC VDCTTOPICA
#endif

// IDgnSRSpeakerA

#undef   INTERFACE
#define  INTERFACE   IDgnSRSpeakerA

DEFINE_GUID(IID_IDgnSRSpeakerA,
	0xdd10801c, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRSpeakerA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (EnumBaseModels) (THIS_ char**, DWORD* ) PURE;
	STDMETHOD (New) (THIS_ const char*, const char* ) PURE;
	STDMETHOD (GetSpeakerDirectory) (THIS_ const char *, char *, DWORD, DWORD * ) PURE;
};

// IDgnSRSpeakerW

#undef   INTERFACE
#define  INTERFACE   IDgnSRSpeakerW

DEFINE_GUID(IID_IDgnSRSpeakerW,
	0xdd10901c, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRSpeakerW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (EnumBaseModels) (THIS_ wchar_t**, DWORD* ) PURE;
	STDMETHOD (New) (THIS_ const wchar_t*, const wchar_t* ) PURE;
	STDMETHOD (GetSpeakerDirectory) (THIS_ const wchar_t *, wchar_t *, DWORD, DWORD * ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRSpeaker	IDgnSRSpeakerW
 #define IID_IDgnSRSpeaker IID_IDgnSRSpeakerW
#else
 #define IDgnSRSpeaker	IDgnSRSpeakerA
 #define IID_IDgnSRSpeaker	IID_IDgnSRSpeakerA
#endif // _S_UNICODE

// IDgnSRTopicEnumA

#undef   INTERFACE
#define  INTERFACE   IDgnSRTopicEnumA

DEFINE_GUID(IID_IDgnSRTopicEnumA,
	0xdd10801d, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTopicEnumA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (EnumBaseModels) (THIS_ char**, DWORD* ) PURE;
	STDMETHOD (GetTopicDirectory) (THIS_ const char *, const char *, char *, DWORD, DWORD * ) PURE;
};

// IDgnSRTopicEnumW

#undef   INTERFACE
#define  INTERFACE   IDgnSRTopicEnumW

DEFINE_GUID(IID_IDgnSRTopicEnumW,
	0xdd10901d, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRTopicEnumW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)  (THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)   (THIS) PURE;
	STDMETHOD_(ULONG,Release)  (THIS) PURE;

	STDMETHOD (EnumBaseModels) (THIS_ wchar_t**, DWORD* ) PURE;
	STDMETHOD (GetTopicDirectory) (THIS_ const wchar_t *, const wchar_t *, wchar_t *, DWORD, DWORD * ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSRTopicEnum	IDgnSRTopicEnumW
 #define IID_IDgnSRTopicEnum IID_IDgnSRTopicEnumW
#else
 #define IDgnSRTopicEnum	IDgnSRTopicEnumA
 #define IID_IDgnSRTopicEnum	IID_IDgnSRTopicEnumA
#endif // _S_UNICODE

// IDgnSRUtil

#undef	INTERFACE
#define	INTERFACE	IDgnSRUtil

DEFINE_GUID(IID_IDgnSRUtil,
	0xdd10801f, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSRUtil , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

	STDMETHOD (SetActiveWindow) (THIS_ HWND, BOOL ) PURE;
	STDMETHOD (GetSpeakerLastSaveTime) (THIS_ FILETIME * ) PURE;
};

// IDgnSSvcDialogsEx

#undef	INTERFACE
#define	INTERFACE	IDgnSSvcDialogsEx

DEFINE_GUID(IID_IDgnSSvcDialogsEx,
	0xdd10820b, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcDialogsEx , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

	STDMETHOD(ToolsTrainWords)	(THIS_ HWND, const char *, DWORD ) PURE;
	STDMETHOD(ToolsFindNewWords) (THIS_ HWND, const char *, BOOL ) PURE;
	STDMETHOD(IsAudioSetupComplete) (THIS_ BOOL * ) PURE;
};

// IDgnSSvcEditSupportA

#undef	INTERFACE
#define	INTERFACE	IDgnSSvcEditSupportA

DEFINE_GUID(IID_IDgnSSvcEditSupportA,
	0xdd10820c, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcEditSupportA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

	STDMETHOD(EditStateGet)		(THIS_ HWND, DWORD, DWORD *, const char * ) PURE;
	STDMETHOD(EditChangePut)	(THIS_ HWND, DWORD, DWORD, const char * ) PURE;
};

// IDgnSSvcEditSupportW

#undef	INTERFACE
#define	INTERFACE	IDgnSSvcEditSupportW

DEFINE_GUID(IID_IDgnSSvcEditSupportW,
	0xdd10920c, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnSSvcEditSupportW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

	STDMETHOD(EditStateGet)		(THIS_ HWND, DWORD, DWORD *, const wchar_t * ) PURE;
	STDMETHOD(EditChangePut)	(THIS_ HWND, DWORD, DWORD, const wchar_t * ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnSSvcEditSupport	IDgnSSvcEditSupportW
 #define IID_IDgnSSvcEditSupport IID_IDgnSSvcEditSupportW
#else
 #define IDgnSSvcEditSupport	IDgnSSvcEditSupportA
 #define IID_IDgnSSvcEditSupport	IID_IDgnSSvcEditSupportA
#endif // _S_UNICODE

// IDgnVDctTranscribe

#undef	INTERFACE
#define	INTERFACE	IDgnVDctTranscribe

DEFINE_GUID(IID_IDgnVDctTranscribe,
	0xdd10840d, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnVDctTranscribe , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

	STDMETHOD(Transcribe)		(THIS_ BOOL, BOOL ) PURE;
	STDMETHOD(AdditionGrammar)	(THIS_ LPUNKNOWN ) PURE;
	STDMETHOD(AllowedCommandsSet) (THIS_ DWORD ) PURE;
	STDMETHOD(AllowedCommandsGet) (THIS_ DWORD * ) PURE;
};

// IDgnLexWordA

#undef	INTERFACE
#define	INTERFACE	IDgnLexWordA

DEFINE_GUID(IID_IDgnLexWordA,
	0xdd108501, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnLexWordA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

	STDMETHOD(Add)				(THIS_ const char *, const POSINFO *, byte *, DWORD ) PURE;
	STDMETHOD(GuessPartOfSpeechandAdd) (THIS_ const char *, const char *, const char *, byte *, DWORD ) PURE;
	STDMETHOD(GuessPartOfSpeech) (THIS_ const char *, const char *, const char *, POSINFO * ) PURE;
	STDMETHOD(Get)				(THIS_ const char *, POSINFO *, byte *, DWORD, DWORD * ) PURE;
	STDMETHOD(Remove)			(THIS_ const char * ) PURE;
};

// IDgnLexWordW

#undef	INTERFACE
#define	INTERFACE	IDgnLexWordW

DEFINE_GUID(IID_IDgnLexWordW,
	0xdd109501, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnLexWordW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

	STDMETHOD(Add)				(THIS_ const wchar_t *, const POSINFO *, byte *, DWORD ) PURE;
	STDMETHOD(GuessPartOfSpeechandAdd) (THIS_ const wchar_t *, const wchar_t *, const wchar_t *, byte *, DWORD ) PURE;
	STDMETHOD(GuessPartOfSpeech) (THIS_ const wchar_t *, const wchar_t *, const wchar_t *, POSINFO * ) PURE;
	STDMETHOD(Get)				(THIS_ const wchar_t *, POSINFO *, byte *, DWORD, DWORD * ) PURE;
	STDMETHOD(Remove)			(THIS_ const wchar_t * ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnLexWord	IDgnLexWordW
 #define IID_IDgnLexWord IID_IDgnLexWordW
#else
 #define IDgnLexWord	IDgnLexWordA
 #define IID_IDgnLexWord	IID_IDgnLexWordA
#endif // _S_UNICODE

// IDgnExtModSupRegistryA

#undef	INTERFACE
#define	INTERFACE	IDgnExtModSupRegistryA

DEFINE_GUID(IID_IDgnExtModSupRegistryA,
	0xdd108600, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnExtModSupRegistryA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

    STDMETHOD(DefineEntry)		(THIS_ const char *, DWORD, const char *, const char *, const char *, const char * ) PURE;
    STDMETHOD(ReadDataInt)		(THIS_ const char *, const char *, const char *, DWORD * ) PURE;
    STDMETHOD(ReadDataRect)	(THIS_ const char *, const char *, const char *, RECT * ) PURE;
    STDMETHOD(ReadDataString)	(THIS_ const char *, const char *, const char *, char *, DWORD, DWORD * ) PURE;
    STDMETHOD(ReadFileName)	(THIS_ const char *, const char *, const char *, char *, DWORD , DWORD * ) PURE;
    STDMETHOD(ReadValues)		(THIS_ const char *, const char *, char *, DWORD , DWORD * ) PURE;
    STDMETHOD(GetMinimum)		(THIS_ const char *, DWORD * ) PURE;
    STDMETHOD(GetMaximum)		(THIS_ const char *, DWORD * ) PURE;
    STDMETHOD(GetDefaultInt)	(THIS_ const char *, DWORD * ) PURE;
    STDMETHOD(GetDefaultRect)	(THIS_ const char *, RECT * ) PURE;
    STDMETHOD(GetDefaultString) (THIS_ const char *, char *, DWORD , DWORD * ) PURE;
    STDMETHOD(WriteDataInt)	(THIS_ const char *, const char *, const char *, DWORD  ) PURE;
    STDMETHOD(WriteDataRect)	(THIS_ const char *, const char *, const char *, const RECT * ) PURE;
    STDMETHOD(WriteDataString)	(THIS_ const char *, const char *, const char *, const char * ) PURE;
    STDMETHOD(GetAppRegistryKey) (THIS_ DWORD , char *, DWORD , DWORD * ) PURE;
};

// IDgnExtModSupRegistryW

#undef	INTERFACE
#define	INTERFACE	IDgnExtModSupRegistryW

DEFINE_GUID(IID_IDgnExtModSupRegistryW,
	0xdd109600, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnExtModSupRegistryW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

    STDMETHOD(DefineEntry)		(THIS_ const wchar_t *, DWORD, const wchar_t *, const wchar_t *, const wchar_t *, const wchar_t * ) PURE;
    STDMETHOD(ReadDataInt)		(THIS_ const wchar_t *, const wchar_t *, const wchar_t *, DWORD * ) PURE;
    STDMETHOD(ReadDataRect)	(THIS_ const wchar_t *, const wchar_t *, const wchar_t *, RECT * ) PURE;
    STDMETHOD(ReadDataString)	(THIS_ const wchar_t *, const wchar_t *, const wchar_t *, wchar_t *, DWORD, DWORD * ) PURE;
    STDMETHOD(ReadFileName)	(THIS_ const wchar_t *, const wchar_t *, const wchar_t *, wchar_t *, DWORD , DWORD * ) PURE;
    STDMETHOD(ReadValues)		(THIS_ const wchar_t *, const wchar_t *, wchar_t *, DWORD , DWORD * ) PURE;
    STDMETHOD(GetMinimum)		(THIS_ const wchar_t *, DWORD * ) PURE;
    STDMETHOD(GetMaximum)		(THIS_ const wchar_t *, DWORD * ) PURE;
    STDMETHOD(GetDefaultInt)	(THIS_ const wchar_t *, DWORD * ) PURE;
    STDMETHOD(GetDefaultRect)	(THIS_ const wchar_t *, RECT * ) PURE;
    STDMETHOD(GetDefaultString) (THIS_ const wchar_t *, wchar_t *, DWORD , DWORD * ) PURE;
    STDMETHOD(WriteDataInt)	(THIS_ const wchar_t *, const wchar_t *, const wchar_t *, DWORD  ) PURE;
    STDMETHOD(WriteDataRect)	(THIS_ const wchar_t *, const wchar_t *, const wchar_t *, const RECT * ) PURE;
    STDMETHOD(WriteDataString)	(THIS_ const wchar_t *, const wchar_t *, const wchar_t *, const wchar_t * ) PURE;
    STDMETHOD(GetAppRegistryKey) (THIS_ DWORD , wchar_t *, DWORD , DWORD * ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnExtModSupRegistry	IDgnExtModSupRegistryW
 #define IID_IDgnExtModSupRegistry IID_IDgnExtModSupRegistryW
#else
 #define IDgnExtModSupRegistry	IDgnExtModSupRegistryA
 #define IID_IDgnExtModSupRegistry	IID_IDgnExtModSupRegistryA
#endif // _S_UNICODE

// IDgnExtModSupStringsA

#undef	INTERFACE
#define	INTERFACE	IDgnExtModSupStringsA

DEFINE_GUID(IID_IDgnExtModSupStringsA,
	0xdd108601, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnExtModSupStringsA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

    STDMETHOD(GetSpecialString) (THIS_ DWORD , DWORD , char *, DWORD , DWORD * ) PURE;
    STDMETHOD(SetSpecialString) (THIS_ DWORD , DWORD , const char * ) PURE;
    STDMETHOD(GetResourceString) (THIS_ DWORD , char *, DWORD , DWORD * ) PURE;
    STDMETHOD(GetStringParameter) (THIS_ DWORD , DWORD , DWORD * ) PURE;
    STDMETHOD(GetWindowModuleFileName) (THIS_ HWND , char *, DWORD , DWORD *  ) PURE;
};

// IDgnExtModSupStringsW

#undef	INTERFACE
#define	INTERFACE	IDgnExtModSupStringsW

DEFINE_GUID(IID_IDgnExtModSupStringsW,
	0xdd109601, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnExtModSupStringsW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

    STDMETHOD(GetSpecialString) (THIS_ DWORD , DWORD , wchar_t *, DWORD , DWORD * ) PURE;
    STDMETHOD(SetSpecialString) (THIS_ DWORD , DWORD , const wchar_t * ) PURE;
    STDMETHOD(GetResourceString) (THIS_ DWORD , wchar_t *, DWORD , DWORD * ) PURE;
    STDMETHOD(GetStringParameter) (THIS_ DWORD , DWORD , DWORD * ) PURE;
    STDMETHOD(GetWindowModuleFileName) (THIS_ HWND , wchar_t *, DWORD , DWORD *  ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnExtModSupStrings	IDgnExtModSupStringsW
 #define IID_IDgnExtModSupStrings IID_IDgnExtModSupStringsW
#else
 #define IDgnExtModSupStrings	IDgnExtModSupStringsA
 #define IID_IDgnExtModSupStrings	IID_IDgnExtModSupStringsA
#endif // _S_UNICODE

// IDgnExtModSupHooks

#undef	INTERFACE
#define	INTERFACE	IDgnExtModSupHooks

DEFINE_GUID(IID_IDgnExtModSupHooks,
	0xdd108602, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnExtModSupHooks , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

    STDMETHOD(InstallAppSpecificKeyHook) (THIS_ DWORD *, DWORD , DWORD  ) PURE;
    STDMETHOD(UninstallAppSpecificKeyHook) (THIS_ DWORD  ) PURE;
    STDMETHOD(InstallAppSpecificMouseHook) (THIS_ DWORD *, DWORD , DWORD , DWORD  ) PURE;
    STDMETHOD(UninstallAppSpecificMouseHook) (THIS_ DWORD  ) PURE;
	STDMETHOD(InstallNotifyRequest) (THIS_ DWORD *, DWORD , DWORD  ) PURE;
	STDMETHOD(GetNotifierChanges) (THIS_ DWORD , DWORD * ) PURE;
    STDMETHOD(UninstallNotifyRequest) (THIS_ DWORD  ) PURE;
};

// IDgnExtModSupErrorsA

#undef	INTERFACE
#define	INTERFACE	IDgnExtModSupErrorsA

DEFINE_GUID(IID_IDgnExtModSupErrorsA,
	0xdd108603, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnExtModSupErrorsA , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

    STDMETHOD(GetErrorThreadBaseWindow) (THIS_ DWORD *, DWORD * ) PURE;
    STDMETHOD(ReportError)		(THIS_ DWORD , DWORD , DWORD , const char *, const char *, const char *, const char *, const char *, DWORD , DWORD  ) PURE;
    STDMETHOD(RegisterHelpFile) (THIS_ const char *, DWORD , DWORD , DWORD * ) PURE;
    STDMETHOD(GetLogFileName)	(THIS_ char *, DWORD , DWORD * ) PURE;
};

// IDgnExtModSupErrorsW

#undef	INTERFACE
#define	INTERFACE	IDgnExtModSupErrorsW

DEFINE_GUID(IID_IDgnExtModSupErrorsW,
	0xdd109603, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47);

DECLARE_INTERFACE_ (IDgnExtModSupErrorsW , IUnknown )
{
	// IUnknown members
	STDMETHOD(QueryInterface)	(THIS_ REFIID riid, LPVOID FAR* ppvObj) PURE;
	STDMETHOD_(ULONG,AddRef)	(THIS) PURE;
	STDMETHOD_(ULONG,Release)	(THIS) PURE;

    STDMETHOD(GetErrorThreadBaseWindow) (THIS_ DWORD *, DWORD * ) PURE;
    STDMETHOD(ReportError)		(THIS_ DWORD , DWORD , DWORD , const wchar_t *, const wchar_t *, const wchar_t *, const wchar_t *, const wchar_t *, DWORD , DWORD  ) PURE;
    STDMETHOD(RegisterHelpFile) (THIS_ const wchar_t *, DWORD , DWORD , DWORD * ) PURE;
    STDMETHOD(GetLogFileName)	(THIS_ wchar_t *, DWORD , DWORD * ) PURE;
};

#ifdef _S_UNICODE
 #define IDgnExtModSupErrors	IDgnExtModSupErrorsW
 #define IID_IDgnExtModSupErrors IID_IDgnExtModSupErrorsW
#else
 #define IDgnExtModSupErrors	IDgnExtModSupErrorsA
 #define IID_IDgnExtModSupErrors	IID_IDgnExtModSupErrorsA
#endif // _S_UNICODE

//---------------------------------------------------------------------------
// Server GUIDs

DEFINE_GUID(
	CLSID_DgnSREnum,
	0xdd100000, 0x6205, 0x11cf, 0xae, 0x61,
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// Voicebar GUIDs for SREnum
	
DEFINE_GUID(
	CLSID_DgnDictate,
	0xdd100001, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// VBarCOM GUIDs

DEFINE_GUID(
	CLSID_SpchServices,
	0xdd100002, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// VoiceDictate GUIDs

DEFINE_GUID(
	CLSID_VoiceDictate,
	0xdd100003, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// IVoiceDictate GUIDs

DEFINE_GUID(
	CLSID_DgnVDct,
	0xdd100004, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// IDgnVCmdFile GUIDs

DEFINE_GUID(
	CLSID_DgnVCmdFile,
	0xdd100005, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// IDgnSite GUID

DEFINE_GUID(
	CLSID_DgnSite,
	0xdd100006, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// IDgnVCmd GUIDs

DEFINE_GUID(
	CLSID_DgnVCmd,
	0xdd100007, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// IDgnVCmdMenu GUIDs

DEFINE_GUID(
	CLSID_DgnVCmdMenu,
	0xdd100008, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// IDgnVCmdEnum GUIDs

DEFINE_GUID(
	CLSID_DgnVCmdEnum,
	0xdd100009, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

//---------------------------------------------------------------------------
// IDgnExtModSupport GUIDs

DEFINE_GUID(
	CLSID_DgnExtModSupport,
	0xdd10000a, 0x6205, 0x11cf, 0xae, 0x61, 
	0x00, 0x00, 0xe8, 0xa2, 0x86, 0x47 );

///////////////////////////////////////////////////////////////////////
// Error codes
//
// These are errors returned by DgnSAPI or VBarCOM which are not defined
// elsewhere.
//

#define DGNSAPIERROR(x) MAKE_SCODE( SEVERITY_ERROR, FACILITY_ITF, (x)+0x1000 )
#define VBARCOMERROR(x) MAKE_SCODE( SEVERITY_ERROR, FACILITY_ITF, (x)+0x1100 )
#define WRDERROR(x) MAKE_SCODE( SEVERITY_ERROR, FACILITY_ITF, (x)+0x1200 )
#define HOOKAPIERROR(x) MAKE_SCODE( SEVERITY_ERROR, FACILITY_ITF, (x)+0x2000 )

#define DGNERR_UNKNOWNWORD			DGNSAPIERROR(1)
#define DGNERR_INVALIDFORM			DGNSAPIERROR(2)
#define DGNERR_WAVEDEVICEMISSING	DGNSAPIERROR(3)
#define DGNERR_WAVEDEVICEERROR		DGNSAPIERROR(4)
#define DGNERR_TERMINATING			DGNSAPIERROR(5)
#define DGNERR_MICNOTPAUSED			DGNSAPIERROR(6)
#define DGNERR_ENGINENOTPAUSED		DGNSAPIERROR(7)
#define DGNERR_INVALIDDIRECTORY		DGNSAPIERROR(8)
#define DGNERR_ONLYONETRACKER		DGNSAPIERROR(9)
#define DGNERR_INVALIDMODE			DGNSAPIERROR(10)
#define DGNERR_ALREADYACTIVE		DGNSAPIERROR(11)
#define DGNERR_MODENOTACTIVE		DGNSAPIERROR(12)
#define DGNERR_TRAININGFAILED		DGNSAPIERROR(13)
#define DGNERR_OUTOFDISK			DGNSAPIERROR(14)
#define DGNERR_INVALIDTOPICNAME		DGNSAPIERROR(15)
#define DGNERR_TOPICALREADYEXISTS	DGNSAPIERROR(16)
#define DGNERR_TOPICDOESNOTEXIST	DGNSAPIERROR(17)
#define DGNERR_TOPICALREADYOPEN		DGNSAPIERROR(18)
#define DGNERR_TOPICNOTOPEN			DGNSAPIERROR(19)
#define DGNERR_TOPICINUSE			DGNSAPIERROR(20)
#define DGNERR_INVALIDSPEAKER		DGNSAPIERROR(21)
#define DGNERR_LMBUILDACTIVE		DGNSAPIERROR(22)
#define DGNERR_LMBUILDINACTIVE		DGNSAPIERROR(23)
#define DGNERR_LMBUILDABORTED		DGNSAPIERROR(24)
#define DGNERR_NOTASELECTGRAMMAR	DGNSAPIERROR(25)
#define DGNERR_DOESNOTMATCHGRAMMAR	DGNSAPIERROR(26)
#define DGNERR_OBJECTISLOCKED		DGNSAPIERROR(27)
#define DGNERR_CANTLOCK				DGNSAPIERROR(28)
#define DGNERR_LMWORDSMISSING		DGNSAPIERROR(29)
#define DGNERR_TRANSCRIBING_ON_WITHOUT_OFF DGNSAPIERROR( 30 )
#define DGNERR_TRANSCRIBING_OFF_WITHOUT_ON DGNSAPIERROR( 31 )

#define DGNERR_UNKNOWNKEY			VBARCOMERROR(1)
#define DGNERR_COMPILER				VBARCOMERROR(2)
#define DGNERR_INTERPRETER			VBARCOMERROR(3)
#define DGNERR_MENUNOTREGISTERED	VBARCOMERROR(4)
#define DGNERR_DVCFILEALREADYLOADED VBARCOMERROR(5)
#define DGNERR_UNKNOWNINTERFACE		VBARCOMERROR(6)
#define DGNERR_UNKNOWNOBJECT		VBARCOMERROR(7)
#define DGNERR_INITIALIZING			VBARCOMERROR(8)
#define DGNERR_CANT_SET_NEWLINE     VBARCOMERROR(9)
#define DGNERR_INTERFACE_NOT_REGISTERED VBARCOMERROR(10)
#define DGNERR_CANTACCESSMEMORYFILE	VBARCOMERROR(11)
#define DGNERR_FAILEDSYNCCHECK		VBARCOMERROR(12)

#define HOOKERR_MEMORY        		HOOKAPIERROR(1)
#define HOOKERR_MUTEX         		HOOKAPIERROR(2)
#define HOOKERR_INJECTIONMUTEX 		HOOKAPIERROR(3)
#define HOOKERR_GMHDMUTEX   		HOOKAPIERROR(4)
#define HOOKERR_NOTDAEMON   		HOOKAPIERROR(5)
#define HOOKERR_UNKNOWNPARAM 		HOOKAPIERROR(6)
#define HOOKERR_BUFFEROVERFLOW 		HOOKAPIERROR(7)
#define HOOKERR_CANNOTINJECT 		HOOKAPIERROR(8)
#define HOOKERR_BADFIXUPOFFSET 		HOOKAPIERROR(9)
#define HOOKERR_LOCKOVERFLOW 		HOOKAPIERROR(10)
#define HOOKERR_DATAMUTEX     		HOOKAPIERROR(11)
#define HOOKERR_INJECTFAILED 		HOOKAPIERROR(12)
#define HOOKERR_NONOTIFYWINDOW 		HOOKAPIERROR(13)
#define HOOKERR_ALL_SLOTS_USED 		HOOKAPIERROR(14)
#define HOOKERR_NOSYSKEYS_WITH_SHIFTKEY HOOKAPIERROR(15)

///////////////////////////////////////////////////////////////////////
// Data Structures

// this data structure is used to fetch parameters (see description of
// IDgnSRParmEnum in mrecinh.idl)

typedef struct tagDGNPARMBLOCK
{
	DWORD dwSize;		// size of the entire block
	DWORD dwType;		// parameter type
	TCHAR pszData[];	// two sequential strings, one is the parameter name
						// and the other is the parameter value.
} DGNPARMBLOCK, *LPDGNPARMBLOCK;

// This data block is used in the DGNSRCKCFG_HEADER chunk in CFG grammars.
// It should not be repeated more than once in that chunk or in the grammar.
// The data block should always be padded out to a multiple of four bytes.

typedef struct tagDGNSRCFGHEADER
{
	DWORD		dwSize;			// size of the block
	VCMDNAME	vcName;			// application and window name
	BYTE		abData[];		// arbitraty data block
} DGNSRCFGHEADER, * PDGNSRCFGHEADER;


typedef struct {
	DWORD dwSize;               // size of the block
	DWORD dwListNum;			// list num of the list
	BYTE abData[];				// array of SRWords of the words in the list
} DGNSRCFGLIST, *PDGNSRCFGLIST;

// This data structure is used by IDgnSSvcEditSupport::EditStateGet

typedef struct tagDGNEDITSTATE
{
	DWORD	dwVersion;
	DWORD	dwSelStart;
	DWORD	dwSelEnd;
	DWORD	dwVisStart;
	DWORD	dwVisEnd;
	RECT	rectSel;
	DWORD	dwNumBytes;
	BYTE 	abData[];
} DGNEDITSTATE, *PDGNEDITSTATE;

// This data structure is used by IDgnSSvcEditSupport::EditChangePut

typedef struct tagDGNEDITCHANGE
{
	DWORD	dwVersion;
	DWORD	dwSelStart;
	DWORD	dwSelEnd;
	DWORD	dwRepStart;
	DWORD	dwRepEnd;
	DWORD	dwCheckCount;
	BYTE	abCheck[16];
	DWORD	dwNumBytes;
	BYTE 	abData[];
} DGNEDITCHANGE, *PDGNEDITCHANGE;

///////////////////////////////////////////////////////////////////////
// Miscelleanous constants

// DGNSAPI-specific chunk ID for grammar load:
//		name of grammar for CFG grammar plus flags.
#define DGNSRCKCFG_HEADER		0x1014

// DGNSAPI-specific chunk ID for grammar load:
//		rule specific description and action
#define DGNSRCKCFG_VCMDCOMMAND	0x1015

// DGNSAPI-specific chunk ID for grammar load:
// for saving words in a list
#define DGNSRCKCFG_LISTS	0x1016

#define DGNSRHDRTYPE_SELECT  10

#define DGNSRCKSELECT_INTROPHRASES	0x1017
#define DGNSRCKSELECT_THRUWORD		0x1018
#define DGNSRCKSELECT_ENDPHRASES	0x1019
#define DGNSRCKSELECT_WORDS			0x1020

// Drgaon additions to SRGRMFMT types
#define SRGRMFMT_DRAGONNATIVE1 0x8101    /* SELECT grammar */
#define SRGRMFMT_DRAGONNATIVE2 0x8102
#define SRGRMFMT_DRAGONNATIVE3 0x8103

// For Kodiak, the maximum number of server (DLL) instances is 1
// Change this constant to a large number if the server is
// released as a general purpose engine.  If the voicebar is
// the engine, leave this constant as it is.
const int k_nMaximumServerInstances = 1;

// The number of words to be passed in to the recognizer for prior context
#define kMaxContextSize 5

// flags returned in SRMODEINFO.dwEngineFeatures (SRCentral::ModeGet)
// TODO: Should RELEASE / DEBUG should be overloaded to use a single flag?
#define DGN_SRFEATURE_RELEASE               0x00000001
#define DGN_SRFEATURE_INHOUSE               0x00000002
#define DGN_SRFEATURE_C_AND_CENABLED        0x00000004
#define DGN_SRFEATURE_MULTI_SPEAKER         0x00000008
#define DGN_SRFEATURE_MULTI_TOPIC           0x00000010
#define DGN_SRFEATURE_DESKTOP_UI            0x00000020
#define DGN_SRFEATURE_PLAYBACK_SPEECH       0x00000040
#define DGN_SRFEATURE_TTS_ENABLED           0x00000080
#define DGN_SRFEATURE_TOPICBLD_ADVANCEDUI   0x00000100
#define DGN_SRFEATURE_DELUXE                0x00000200
#define DGN_SRFEATURE_PERSONALPLUS          0x00000400
#define DGN_SRFEATURE_PERSONAL              0x00000800
#define DGN_SRFEATURE_POINTSPEAK            0x00001000
#define DGN_SRFEATURE_SERVERONLY            0x00002000
#define DGN_SRFEATURE_NETADMIN              0x00004000
#define DGN_SRFEATURE_NETCLIENT             0x00008000
#define DGN_SRFEATURE_NETDELUXE             0x00010000
#define DGN_SRFEATURE_OEM                   0x00020000

#endif DSPEECH_H

