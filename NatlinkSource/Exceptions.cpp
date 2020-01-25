/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 Excepts.cpp
	This file contains the code which creates Python exceptions as necessary.
*/

#include "stdafx.h"
#include <stdarg.h>
#include "DragonCode.h"
#include "GrammarObject.h"
#include "ResultObject.h"
#include "Exceptions.h"

// This is our set of error objects, one for each error listed in Excepts.h
PyObject * ErrObjects[ ERROR_COUNT ];

//---------------------------------------------------------------------------

void createException( PyObject * pDict, int errorType, char * errorName )
{
	char * fullName = new char[ 10+strlen(errorName) ];
	strcpy( fullName, "natlink." );
	strcat( fullName, errorName );

    ErrObjects[errorType] = PyErr_NewException( fullName, ErrObjects[0], NULL );
    PyDict_SetItemString( pDict, errorName, ErrObjects[errorType] );
}

//---------------------------------------------------------------------------

void initExceptions( PyObject * pModule )
{
	PyObject * pDict = PyModule_GetDict( pModule );

	// Here we create the base exception class
    ErrObjects[0] = PyErr_NewException( "natlink.NatError", NULL, NULL );
    PyDict_SetItemString( pDict, "NatError", ErrObjects[0] );

	// Here we create all the other errors
	createException( pDict, errInvalidWord, "InvalidWord" );
	createException( pDict, errUnknownName, "UnknownName" );
	createException( pDict, errBadGrammar, "BadGrammar" );
	createException( pDict, errUserExists, "UserExists" );
	createException( pDict, errWrongState, "WrongState" );
	createException( pDict, errOutOfRange, "OutOfRange" );
	createException( pDict, errMimicFailed, "MimicFailed" );
	createException( pDict, errBadWindow, "BadWindow" );
	createException( pDict, errSyntaxError, "SyntaxError" );
	createException( pDict, errValueError, "ValueError" );
	createException( pDict, errDataMissing, "DataMissing" );
	createException( pDict, errWrongType, "WrongType" );
	// Important: added new exceptions above this line
}

//---------------------------------------------------------------------------

void reportComError(
	HRESULT rc, const char * pszFunc, const char * pszFile, int lineNum )
{
	// if the file name includes a path, strip the path
	const char * pSlash = strrchr( pszFile, '\\' );
	if( pSlash )
	{
		pszFile = pSlash+1;
	}

	// get the text form of the common errors
	char *pszName = NULL;
	switch( rc )
	{
	 case SRERR_INVALIDLIST: pszName = "SRERR_INVALIDLIST"; break;
	 case SRERR_INVALIDCHAR: pszName = "SRERR_INVALIDCHAR"; break;
	 case SRERR_GRAMMARERROR: pszName = "SRERR_GRAMMARERROR"; break;
	 case SRERR_INVALIDRULE: pszName = "SRERR_INVALIDRULE"; break;
	 case SRERR_GRAMMARTOOCOMPLEX: pszName = "SRERR_GRAMMARTOOCOMPLEX"; break;
	 case SRERR_RULENOTACTIVE: pszName = "SRERR_RULENOTACTIVE"; break;
	 case SRERR_OUTOFDISK: pszName = "SRERR_OUTOFDISK"; break;
	 case SRERR_NOTSUPPORTED: pszName = "SRERR_NOTSUPPORTED"; break;
	 case SRERR_NOTENOUGHDATA: pszName = "SRERR_NOTENOUGHDATA"; break;
	 case SRERR_VALUEOUTOFRANGE: pszName = "SRERR_VALUEOUTOFRANGE"; break;
	 case SRERR_GRAMMARWRONGTYPE: pszName = "SRERR_GRAMMARWRONGTYPE"; break;
	 case SRERR_INVALIDWINDOW: pszName = "SRERR_INVALIDWINDOW"; break;
	 case SRERR_INVALIDPARAM: pszName = "SRERR_INVALIDPARAM"; break;
	 case SRERR_INVALIDMODE: pszName = "SRERR_INVALIDMODE"; break;
	 case SRERR_TOOMANYGRAMMARS: pszName = "SRERR_TOOMANYGRAMMARS"; break;
	 case SRERR_WAVEDEVICEBUSY: pszName = "SRERR_WAVEDEVICEBUSY"; break;
	 case SRERR_WAVEFORMATNOTSUPPORTED: pszName = "SRERR_WAVEFORMATNOTSUPPORTED"; break;
	 case SRERR_GRAMTOOLARGE: pszName = "SRERR_GRAMTOOLARGE"; break;
	 case SRERR_INVALIDINTERFACE: pszName = "SRERR_INVALIDINTERFACE"; break;
	 case SRERR_INVALIDKEY: pszName = "SRERR_INVALIDKEY"; break;
	 case SRERR_INVALIDFLAG: pszName = "SRERR_INVALIDFLAG"; break;
	 case SRERR_RULEALREADYACTIVE: pszName = "SRERR_RULEALREADYACTIVE"; break;
	 case SRERR_NOUSERSELECTED: pszName = "SRERR_NOUSERSELECTED"; break;
	 case SRERR_BAD_PRONUNCIATION: pszName = "SRERR_BAD_PRONUNCIATION"; break;
	 case SRERR_DATAFILEERROR: pszName = "SRERR_DATAFILEERROR"; break;
	 case SRERR_GRAMMARALREADYACTIVE: pszName = "SRERR_GRAMMARALREADYACTIVE"; break;
	 case SRERR_GRAMMARNOTACTIVE: pszName = "SRERR_GRAMMARNOTACTIVE"; break;
	 case SRERR_GLOBALGRAMMARALREADYACTIVE: pszName = "SRERR_GLOBALGRAMMARALREADYACTIVE"; break;
	 case SRERR_LANGUAGEMISMATCH: pszName = "SRERR_LANGUAGEMISMATCH"; break;
	 case SRERR_MULTIPLELANG: pszName = "SRERR_MULTIPLELANG"; break;
	 case SRERR_LDGRAMMARNOWORDS: pszName = "SRERR_LDGRAMMARNOWORDS"; break;
	 case SRERR_NOLEXICON: pszName = "SRERR_NOLEXICON"; break;
	 case SRERR_SPEAKEREXISTS: pszName = "SRERR_SPEAKEREXISTS"; break;
	 case SRERR_GRAMMARENGINEMISMATCH: pszName = "SRERR_GRAMMARENGINEMISMATCH"; break;
	 case SRERR_BOOKMARKEXISTS: pszName = "SRERR_BOOKMARKEXISTS"; break;
	 case SRERR_BOOKMARKDOESNOTEXIST: pszName = "SRERR_BOOKMARKDOESNOTEXIST"; break;
	 case SRERR_MICWIZARDCANCELED: pszName = "SRERR_MICWIZARDCANCELED"; break;
	 case SRERR_WORDTOOLONG: pszName = "SRERR_WORDTOOLONG"; break;
	 case SRERR_BAD_WORD: pszName = "SRERR_BAD_WORD"; break;
	 case DGNERR_UNKNOWNWORD: pszName = "DGNERR_UNKNOWNWORD"; break;
	 case DGNERR_INVALIDFORM: pszName = "DGNERR_INVALIDFORM"; break;
	 case DGNERR_WAVEDEVICEMISSING: pszName = "DGNERR_WAVEDEVICEMISSING"; break;
	 case DGNERR_WAVEDEVICEERROR: pszName = "DGNERR_WAVEDEVICEERROR"; break;
	 case DGNERR_TERMINATING: pszName = "DGNERR_TERMINATING"; break;
	 case DGNERR_MICNOTPAUSED: pszName = "DGNERR_MICNOTPAUSED"; break;
	 case DGNERR_ENGINENOTPAUSED: pszName = "DGNERR_ENGINENOTPAUSED"; break;
	 case DGNERR_INVALIDDIRECTORY: pszName = "DGNERR_INVALIDDIRECTORY"; break;
	 case DGNERR_ONLYONETRACKER: pszName = "DGNERR_ONLYONETRACKER"; break;
	 case DGNERR_INVALIDMODE: pszName = "DGNERR_INVALIDMODE"; break;
	 case DGNERR_ALREADYACTIVE: pszName = "DGNERR_ALREADYACTIVE"; break;
	 case DGNERR_MODENOTACTIVE: pszName = "DGNERR_MODENOTACTIVE"; break;
	 case DGNERR_TRAININGFAILED: pszName = "DGNERR_TRAININGFAILED"; break;
	 case DGNERR_OUTOFDISK: pszName = "DGNERR_OUTOFDISK"; break;
	 case DGNERR_INVALIDTOPICNAME: pszName = "DGNERR_INVALIDTOPICNAME"; break;
	 case DGNERR_TOPICALREADYEXISTS: pszName = "DGNERR_TOPICALREADYEXISTS"; break;
	 case DGNERR_TOPICDOESNOTEXIST: pszName = "DGNERR_TOPICDOESNOTEXIST"; break;
	 case DGNERR_TOPICALREADYOPEN: pszName = "DGNERR_TOPICALREADYOPEN"; break;
	 case DGNERR_TOPICNOTOPEN: pszName = "DGNERR_TOPICNOTOPEN"; break;
	 case DGNERR_TOPICINUSE: pszName = "DGNERR_TOPICINUSE"; break;
	 case DGNERR_INVALIDSPEAKER: pszName = "DGNERR_INVALIDSPEAKER"; break;
	 case DGNERR_LMBUILDACTIVE: pszName = "DGNERR_LMBUILDACTIVE"; break;
	 case DGNERR_LMBUILDINACTIVE: pszName = "DGNERR_LMBUILDINACTIVE"; break;
	 case DGNERR_LMBUILDABORTED: pszName = "DGNERR_LMBUILDABORTED"; break;
	 case DGNERR_NOTASELECTGRAMMAR: pszName = "DGNERR_NOTASELECTGRAMMAR"; break;
	 case DGNERR_DOESNOTMATCHGRAMMAR: pszName = "DGNERR_DOESNOTMATCHGRAMMAR"; break;
	 case DGNERR_OBJECTISLOCKED: pszName = "DGNERR_OBJECTISLOCKED"; break;
	 case DGNERR_CANTLOCK: pszName = "DGNERR_CANTLOCK"; break;
	 case DGNERR_LMWORDSMISSING: pszName = "DGNERR_LMWORDSMISSING"; break;
	 case DGNERR_TRANSCRIBING_ON_WITHOUT_OFF: pszName = "DGNERR_TRANSCRIBING_ON_WITHOUT_OFF"; break;
	 case DGNERR_TRANSCRIBING_OFF_WITHOUT_ON: pszName = "DGNERR_TRANSCRIBING_OFF_WITHOUT_ON"; break;
	 case E_OUTOFMEMORY: pszName = "E_OUTOFMEMORY"; break;
	 case E_POINTER: pszName = "E_POINTER"; break;
	 case E_HANDLE: pszName = "E_HANDLE"; break;
	 case E_ABORT: pszName = "E_ABORT"; break;
	 case E_FAIL: pszName = "E_FAIL"; break;
	 case E_ACCESSDENIED: pszName = "E_ACCESSDENIED"; break;
	 case E_WRONGTYPE: pszName = "E_WRONGTYPE"; break;
	 case E_BUFFERTOOSMALL: pszName = "E_BUFFERTOOSMALL"; break;
	}

	// format an error message
	if( pszName == NULL )
	{
		reportError( errNatError,
			"An error occurred calling %s from %s %d.  "
			"The error code was 0x%x (%d).",
			pszFunc, pszFile, lineNum, rc, rc );
	}
	else
	{
		reportError( errNatError,
			"A %s error occurred calling %s from %s %d.",
			pszName, pszFunc, pszFile, lineNum );
	}
}

//---------------------------------------------------------------------------

void reportError( int errorType, const char * pszFormat, ... )
{
	assert( errorType >= 0 && errorType < ERROR_COUNT );

	char szErrorMsg[ 512 ];

	va_list pArgs;
	va_start( pArgs, pszFormat );
	vsprintf( szErrorMsg, pszFormat, pArgs );
	va_end( pArgs );

	PyErr_SetString( ErrObjects[errorType], szErrorMsg );
}

//---------------------------------------------------------------------------
// In the event that there is a COM error which we expect, it is possible to
// get extended error information for NatSpeak using the IDgnError
// interface.  In this function, we try to get that extended error
// information, and if available we format a more comprehensive error
// message.

void reportError(
	int errorType, LPUNKNOWN pIUnknown, const char * pszMessage )
{
	HRESULT rc;
	assert( pIUnknown != NULL );

	IDgnErrorPtr pIDgnError;
	rc = pIUnknown->QueryInterface(
		__uuidof(IDgnError), (void**)&pIDgnError );
	if( FAILED(rc) )
	{
		reportError( errorType, pszMessage );
		return;
	}

	TCHAR szNatSpeakErr[ 512 ];
	DWORD dwSizeNeeded;
	rc = pIDgnError->ErrorMessageGet( szNatSpeakErr, 512, &dwSizeNeeded );

	if( rc != E_BUFFERTOOSMALL && FAILED(rc) )
	{
		reportError( errorType, pszMessage );
		return;
	}

	char szErrorMsg[ 1024 ];

	#ifdef UNICODE
		int size_needed = ::WideCharToMultiByte( CP_UTF8, 0, szNatSpeakErr, -1, NULL, 0,  NULL, NULL);
		char * szNatSpeakErrA = new char[ size_needed ];
		::WideCharToMultiByte( CP_UTF8, 0, szNatSpeakErr, -1, szNatSpeakErrA, size_needed, NULL, NULL );

		sprintf( szErrorMsg, "%s (%s)", pszMessage, szNatSpeakErrA );
		if ( szNatSpeakErrA )
			delete [] szNatSpeakErrA;

	#else
		sprintf( szErrorMsg, "%s (%s)", pszMessage, szNatSpeakErr );
	#endif

	PyErr_SetString( ErrObjects[errorType], szErrorMsg );
}
