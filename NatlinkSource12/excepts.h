/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 Excepts.h
	Header file for excepts.cpp
*/

// call this to initialize the exceptions
void initExceptions( PyObject * pModule );

// this is the list of possible exception classes which we return
enum
{
	errNatError,
	errInvalidWord,
	errUnknownName,
	errBadGrammar,
	errUserExists,
	errWrongState,
	errOutOfRange,
	errMimicFailed,
	errBadWindow,
	errSyntaxError,
	errValueError,
	errDataMissing,
	errWrongType,

	// Important: when adding an error to this enum, modify the error
	// creation code in initExceptions in Excepts.cpp
	ERROR_COUNT
};

//--------------------
// these are the error reporting functions

// this is the normal error reporting function.  Pass in an error type and
// an error message (using printf formatting)
void reportError(
	int errorType, const char * pszFormat, ... );

// use this error reporting function for unexpected COM errors.
void reportComError(
	HRESULT rc, const char * pszFunc, const char * pszFile, int lineNum );

// use this error reporting function when you have a COM object from which
// we need to extract extended error information.
void reportError(
	int errorType, LPUNKNOWN pIUnknown, const char * pszMessage );

//--------------------
// these are common error macros

// This macro is used to report errors following COM calls
#define RETURNIFERROR(rc,func) \
	if( FAILED(rc) ) \
	{ \
		reportComError( rc, func, __FILE__, __LINE__ ); \
		return FALSE; \
	}

// These macros handle specific error codes	
#define onINVALIDCHAR( rc, interface, message ) \
	if( rc == SRERR_INVALIDCHAR ) \
	{ \
		reportError( errInvalidWord, interface, message ); \
		return FALSE; \
	}

#define onINVALIDRULE( rc, message, param ) \
	if( rc == SRERR_INVALIDRULE ) \
	{ \
		reportError( errUnknownName, message, param ); \
		return FALSE; \
	}

#define onINVALIDLIST( rc, message, param ) \
	if( rc == SRERR_INVALIDLIST ) \
	{ \
		reportError( errUnknownName, message, param ); \
		return FALSE; \
	}
	
#define onVALUEOUTOFRANGE( rc, message, param ) \
	if( rc == SRERR_VALUEOUTOFRANGE ) \
	{ \
		reportError( errOutOfRange, message, param ); \
		return FALSE; \
	}

#define onGRAMMARERROR( rc, interface, message ) \
	if( rc == SRERR_GRAMMARERROR ) \
	{ \
		reportError( errBadGrammar, interface, message ); \
		return FALSE; \
	}
	
#define onGRAMMARTOOCOMPLEX( rc, message ) \
	if( rc == SRERR_GRAMMARTOOCOMPLEX ) \
	{ \
		reportError( errBadGrammar, message ); \
		return FALSE; \
	}

#define onRULEALREADYACTIVE( rc, message, param ) \
	if( rc == SRERR_RULEALREADYACTIVE ) \
	{ \
		reportError( errWrongState, message, param ); \
		return FALSE; \
	}

#define onRULENOTACTIVE( rc, message, param ) \
	if( rc == SRERR_RULENOTACTIVE ) \
	{ \
		reportError( errWrongState, message, param ); \
		return FALSE; \
	}

#define onINVALIDMODE( rc, message, param ) \
	if( rc == DGNERR_INVALIDMODE ) \
	{ \
		reportError( errWrongState, message, param ); \
		return FALSE; \
	}
#define onALREADYACTIVE( rc, message ) \
	if( rc == DGNERR_ALREADYACTIVE) \
	{ \
		reportError( errWrongState, message ); \
		return FALSE; \
	}

#define onINVALIDARG( rc, message, param ) \
	if( rc == E_INVALIDARG ) \
	{ \
		reportError( errInvalidWord, message, param ); \
		return FALSE; \
	}

#define onSPEAKEREXISTS( rc, message, param ) \
	if( rc == SRERR_SPEAKEREXISTS ) \
	{ \
		reportError( errUserExists, message, param ); \
		return FALSE; \
	}

#define onNOTENOUGHDATA( rc, message ) \
	if( rc == SRERR_NOTENOUGHDATA ) \
	{ \
		reportError( errDataMissing, message ); \
		return FALSE; \
	}

#define onINVALIDINTERFACE( rc, message ) \
	if( rc == SRERR_INVALIDINTERFACE ) \
	{ \
		reportError( errWrongType, message ); \
		return FALSE; \
	}

#define onINVALIDTEXTCHAR( rc, message, param ) \
	if( rc == LEXERR_INVALIDTEXTCHAR ) \
	{ \
		reportError( errInvalidWord, message, param ); \
		return FALSE; \
	}

#define onNOTASELECTGRAMMAR( rc, message, param ) \
	if( rc == DGNERR_NOTASELECTGRAMMAR ) \
	{ \
		reportError( errWrongType, message, param ); \
		return FALSE; \
	}

#define onDOESNOTMATCHGRAMMAR( rc, message, param ) \
	if( rc == DGNERR_DOESNOTMATCHGRAMMAR ) \
	{ \
		reportError( errBadGrammar, message, param ); \
		return FALSE; \
	}

//---------------------------------------------------------------------------
// I use this class to handle the case that a pointer is allocated locally
// within a subroutine and it needs to be cleaned up in the case that an
// exception is thrown.
//
// Use this code in the following case:
//		type * pType = (type*) new type;
//		...
//		delete pType;
//
// Instead, simple code:
//		CPointer<type> pType = (type*) new type;
//		...
//
// This will ensure that delete is called on the pointer when the variable
// goes out of scope including when an exception is thrown.  Be careful not
// to return a CPointer or assigned it to another variable and except it to
// be preserved.
//
// Use CPointerChar instead of CPointer<char> to avoid compiler warnings.

template<class T> class CPointer
{
 public:
	CPointer() { m_ptr = 0; }
	~CPointer() { if( m_ptr ) delete m_ptr; }
	CPointer(T* ptr) { m_ptr = ptr; }
	operator T*() { return (T*)m_ptr; }
	T* operator->() { return m_ptr; }
	T* operator=(T* ptr) { if( m_ptr ) delete m_ptr; return m_ptr = ptr; }
	
 private:
	T * m_ptr;
};

class CPointerChar
{
 public:
	CPointerChar() { m_ptr = 0; }
	~CPointerChar() { if( m_ptr ) delete m_ptr; }
	CPointerChar(TCHAR* ptr) { m_ptr = ptr; }
	operator TCHAR*() { return (TCHAR*)m_ptr; }
	TCHAR* operator=(TCHAR* ptr) { if( m_ptr ) delete m_ptr; return m_ptr = ptr; }
	
 private:
	TCHAR * m_ptr;
};

// copy TCHAR string to char string...
inline void Unicode2Char( char *to, PTCHAR from, int tosize )
{
#ifdef _UNICODE
	WideCharToMultiByte(CP_ACP, 0, from, -1, to, tosize, NULL, NULL );
#else
	strcpy( to, from );
#endif
}

// copy char string to TCHAR string...
inline void Char2Unicode( PTCHAR to, char *from, int tosize )
{
#ifdef _UNICODE
	MultiByteToWideChar(CP_ACP, 0, from, -1, to, tosize );
#else
	strcpy( to, from );
#endif
}