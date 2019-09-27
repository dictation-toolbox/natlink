/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 gramobj.h
	Implementation of the CGrammarObject class which encapulates a SAPI grammar
	and is exposed in Python as a GramObj.
*/

#include "stdafx.h"
#include "DragonCode.h"
#include "GrammarObject.h"
#include "ResultObject.h"
#include "Exceptions.h"
#include <fstream>
#include <vector>

// defined in PythWrap.cpp
CResultObject * resobj_new();

// This macro is used at the top of functions which can not be called
// when no grammar has been loaded
#define NEEDGRAMMAR( func ) \
	if( m_pISRGramCommon == NULL ) \
	{ \
		reportError( errNatError, \
			"Need to call GramObj.load before calling %s", func ); \
		return FALSE; \
	}

/////////////////////////////////////////////////////////////////////////////
//
// This is a grammar notification sink.  This sink detect PhraseFinish and
// pass the information to the parent class.
//

class CSRGramNotifySink :
	public CComObjectRoot,
	public ISRGramNotifySink,
	public IDgnGetSinkFlags
{
public:
	CSRGramNotifySink() { m_pParent = 0; m_bAllResults = FALSE; m_bHypothesis = FALSE; }
	
BEGIN_COM_MAP(CSRGramNotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(ISRGramNotifySink), ISRGramNotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(IDgnGetSinkFlags), IDgnGetSinkFlags)
END_COM_MAP()

public:

	STDMETHOD (BookMark)         (DWORD) { return S_OK; }
	STDMETHOD (Paused)           () { return S_OK; }
	STDMETHOD (PhraseFinish)     (DWORD, QWORD, QWORD, PSRPHRASE, LPUNKNOWN); // not inline
	STDMETHOD (PhraseHypothesis) (DWORD, QWORD, QWORD, PSRPHRASE, LPUNKNOWN); // not inline
	STDMETHOD (PhraseStart)      (QWORD) { return S_OK; }
	STDMETHOD (ReEvaluate)       (LPUNKNOWN) { return S_OK; }
	STDMETHOD (Training)         (DWORD) { return S_OK; }
	STDMETHOD (UnArchive)        (LPUNKNOWN) { return S_OK; }

	STDMETHOD (SinkFlagsGet) (DWORD* );	// not inline

	// this is our parent
	CGrammarObject * m_pParent;

	// this flag is set when we want to receive all PhraseFinish messages,
	// not just ones specific to this grammar.
	BOOL m_bAllResults;

	// this flag is set when we want to receive the PhraseHypothesis messages
	BOOL m_bHypothesis;
};

//---------------------------------------------------------------------------

STDMETHODIMP CSRGramNotifySink::SinkFlagsGet( DWORD * pdwFlags )
{
	// Dragon NaturallySpeaking allows sink object to have a separate
	// interface called IDgnGetSinkFlags.  That interface implements a
	// single function which is call by Drgaon NaturallySpeaking when the
	// sink is first registered.
	//
	// if IDgnGetSinkFlags exists, SinkFlagsGet returns a list of the
	// notifications we want.  This interface is optional.  Without it we
	// return the normal set (PhraseState, PhraseFinish, etc.) but with this
	// interface we can reduce the notification traffic.
	
	if( pdwFlags )
	{
		*pdwFlags =
				// send PhraseFinish for our grammar
			DGNSRGRAMSINKFLAG_SENDPHRASEFINISH;

		if( m_bAllResults )
		{
			*pdwFlags |=
				// send PhraseFinish for all grammars
				DGNSRGRAMSINKFLAG_SENDFOREIGNFINISH;
		}

		if( m_bHypothesis )
		{
			*pdwFlags |=
				// send PhraseHypothesis
				DGNSRGRAMSINKFLAG_SENDPHRASEHYPO;
		}
	}
	
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CSRGramNotifySink::PhraseFinish(
	DWORD dwFlags, QWORD, QWORD, PSRPHRASE pSRPhrase, LPUNKNOWN pIUnknown )
{
	// This is the standard SAPI PhraseFinish call; call our parent with the
	// information and the special parameter
	
	if( m_pParent )
	{
		m_pParent->PhraseFinish( dwFlags, pSRPhrase, pIUnknown );
	}
	
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CSRGramNotifySink::PhraseHypothesis(
	DWORD dwFlags, QWORD, QWORD, PSRPHRASE pSRPhrase, LPUNKNOWN )
{
	// This is the standard SAPI PhraseHypothesis call; call our parent with
	// the information.  Note that a results object is not available.
	
	if( m_pParent )
	{
		m_pParent->PhraseHypothesis( dwFlags, pSRPhrase );
	}
	
	return S_OK;
}

/////////////////////////////////////////////////////////////////////////////
//
// CGrammarObject
//

//---------------------------------------------------------------------------

void CGrammarObject::create(CDragonCode * pDragCode )
{
	m_pBeginCallback = NULL;
	m_pResultsCallback = NULL;
	m_pHypothesisCallback = NULL;
	m_bAllResults = FALSE;
	m_pISRGramCommon = NULL;
	m_pDragCode = pDragCode;
	m_pNextGramObj = NULL;
}

//---------------------------------------------------------------------------

void CGrammarObject::destroy()
{
	setBeginCallback( Py_None );
	setResultsCallback( Py_None );
	unload();
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::unload()
{
	if( m_pISRGramCommon )
	{
		m_pISRGramCommon->Release();
		m_pISRGramCommon = NULL;

		m_pDragCode->removeGramObj( this );
	}

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::load(BYTE * pData, DWORD dwSize, BOOL bAllResults, BOOL bHypothesis )
{

	HRESULT rc;

	TCHAR szMsg[128] = {'\0'};
	/*wsprintf( szMsg, L"dwSize: %d", dwSize );
	MessageBox( 0, szMsg, L"GrammarLoad", MB_OK );*/

	/*for (int a = 8; a < 12; a++ )
	{
		wsprintf( szMsg, L"pChar: %s", pData[a] );
		MessageBox( 0, szMsg, L"GrammarLoad", MB_OK );
	}
*/

//    reportError( errNatError,
//                 "test error call" );
//    return FALSE;

	if( m_pDragCode == NULL || m_pDragCode->pISRCentral() == NULL )
	{
		reportError( errNatError,
			"Calling GramObj.load is not allowed before calling natConnect" );
		return FALSE;
	}

	m_bAllResults = bAllResults;
	
	if( m_pISRGramCommon )
	{
		reportError( errNatError,
			"A grammar is already loaded (calling %s)", "GramObj.load" );
		return FALSE;
	}

	if( pData == NULL || dwSize == 0 )
	{
		reportError( errNatError,
			"The binary data is missing (calling %s)", "GramObj.load" );
		return FALSE;
	}

	// create a grammar sink
	CComObject<CSRGramNotifySink> * pGramSinkObj = 0;
	ISRGramNotifySinkPtr pIGramSink;

	rc = CComObject<CSRGramNotifySink>::CreateInstance( &pGramSinkObj );
	RETURNIFERROR( rc, "CreateInstance(GramNotifySink)" );

	pGramSinkObj->m_pParent = this;
	pGramSinkObj->m_bAllResults = bAllResults;
	pGramSinkObj->m_bHypothesis = bHypothesis;

	rc = pGramSinkObj->QueryInterface(
		__uuidof(ISRGramNotifySink), (void**)&pIGramSink );
	RETURNIFERROR( rc, "QueryInterface(ISRGramNotifySink)" );

	// load the grammar
    std::streampos fileSize;
	SDATA sData;
	sData.pData = pData;
//	sData.pData = &fileData[0];
//	sData.dwSize = (DWORD)fileSize;
    sData.dwSize = (DWORD)dwSize;

	IUnknownPtr pUnknown;

	// The grammar format must match the type of grammar in the binary data
	// block's header.  The grammar type is the first DWORD in the header.
	SRGRMFMT gramType;
	switch( *(DWORD*)pData )
	{
	 case SRHDRTYPE_CFG:
		gramType = SRGRMFMT_CFG;
		break;
	 case SRHDRTYPE_DICTATION:
		gramType = SRGRMFMT_DICTATION;
		break;
	 case DGNSRHDRTYPE_SELECT:
		gramType = (SRGRMFMT)SRGRMFMT_DRAGONNATIVE1;
		break;
	 default:
		reportError( errBadGrammar,
			"The grammar type (%d) is invalid or not supported",
			*(DWORD*)pData );
		return FALSE;
	}

	rc = m_pDragCode->pISRCentral()->GrammarLoad(
		gramType, sData, pGramSinkObj,
		__uuidof(ISRGramNotifySink), &pUnknown );
	onINVALIDCHAR( rc, m_pDragCode->pISRCentral(), "Invalid word in grammar" );
	onGRAMMARERROR( rc, m_pDragCode->pISRCentral(), "The grammar specification is in error" );
	RETURNIFERROR( rc, "ISRCentral::GrammarLoad" );

	rc = pUnknown->QueryInterface(
		__uuidof(ISRGramCommon), (void **)&m_pISRGramCommon );
	RETURNIFERROR( rc, "QueryInterface(ISRGramCommon)" );

	// now we add ourself to the CDragonCode linked list so all the grammars
	// can be freed when we disconnect
	m_pDragCode->addGramObj( this );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::setBeginCallback(PyObject *pCallback )
{
	if( pCallback == Py_None )
	{
		Py_XDECREF( m_pBeginCallback );
		m_pBeginCallback = NULL;
	}
	else
	{
		Py_XINCREF( pCallback );
		Py_XDECREF( m_pBeginCallback );
		m_pBeginCallback = pCallback;
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::setResultsCallback(PyObject *pCallback )
{
	if( pCallback == Py_None )
	{
		Py_XDECREF( m_pResultsCallback );
		m_pResultsCallback = NULL;
	}
	else
	{
		Py_XINCREF( pCallback );
		Py_XDECREF( m_pResultsCallback );
		m_pResultsCallback = pCallback;
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::setHypothesisCallback(PyObject *pCallback )
{
	if( pCallback == Py_None )
	{
		Py_XDECREF( m_pHypothesisCallback );
		m_pHypothesisCallback = NULL;
	}
	else
	{
		Py_XINCREF( pCallback );
		Py_XDECREF( m_pHypothesisCallback );
		m_pHypothesisCallback = pCallback;
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::activate(char * ruleName, HWND hWnd )
{
	HRESULT rc;

	NEEDGRAMMAR( "GramObj.activate" );

	if( hWnd != NULL && !IsWindow( hWnd ) )
	{
		reportError( errBadWindow,
			"The handle %d does not refer to an existing window", hWnd );
		return FALSE;
	}

	// An empty rule name is the same as a NULL rule name for CFG grammars
	// and a NULL rull name is required for dictation grammars.
	if( *ruleName == 0 )
	{
		ruleName = NULL;
	}
	
	#ifdef UNICODE
		if ( ruleName )
		{
			/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, ruleName, -1, NULL, 0 );
			CPointerChar ruleNameW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, ruleName, -1, ruleNameW, size_needed );*/
			CComBSTR bstrRuleName( ruleName );
			rc = m_pISRGramCommon->Activate(
				hWnd,		// window handle, NULL for global command
				FALSE,		// autopause flag
				bstrRuleName );
		}
		else
			rc = m_pISRGramCommon->Activate(
				hWnd,		// window handle, NULL for global command
				FALSE,		// autopause flag
				NULL );
	#else
		rc = m_pISRGramCommon->Activate(
			hWnd,		// window handle, NULL for global command
			FALSE,		// autopause flag
			ruleName );
	#endif
	onINVALIDRULE( rc, "The rule %s is not defined in the grammar", ruleName );
    onGRAMMARTOOCOMPLEX( rc, "The grammar is too complex to be recognized" );
	onRULEALREADYACTIVE( rc, "The rule %s is already active", ruleName );
	RETURNIFERROR( rc, "GramObj.activate" );
		
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::deactivate(char * ruleName )
{
	HRESULT rc;
	
	NEEDGRAMMAR( "GramObj.deactivate" );

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, ruleName, -1, NULL, 0 );
		CPointerChar ruleNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, ruleName, -1, ruleNameW, size_needed );*/
		CComBSTR bstrRuleName( ruleName );
		rc = m_pISRGramCommon->Deactivate( bstrRuleName );
	#else
		rc = m_pISRGramCommon->Deactivate( ruleName );
	#endif

	onRULENOTACTIVE( rc, "The rule %s is not active", ruleName );
	RETURNIFERROR( rc, "GramObj.deactivate" );
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::emptyList(char * listName )
{
	HRESULT rc;
	
	NEEDGRAMMAR( "GramObj.emptyList" );

	// to empty the list, we will set the list to be a set of no words
	SDATA sData;
	sData.pData = "\0";
	sData.dwSize = 0;

	ISRGramCFGPtr pISRGramCFG;
	rc = m_pISRGramCommon->QueryInterface(
		__uuidof(ISRGramCFG), (void **)&pISRGramCFG );
	onINVALIDINTERFACE( rc, "emptyList not support for this type of grammar" )
	RETURNIFERROR( rc, "QueryInterface(ISRGramCFG)" );

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, listName, -1, NULL, 0 );
		CPointerChar listNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, listName, -1, listNameW, size_needed );*/
		CComBSTR bstrListName( listName );
		rc = pISRGramCFG->ListSet( bstrListName, sData );
	#else
		rc = pISRGramCFG->ListSet( listName, sData );
	#endif
	onINVALIDLIST( rc, "The list %s is not defined in the grammar", listName );
	RETURNIFERROR( rc, "GramObj.emptyList" );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::appendList(char * listName, char * word )
{
	HRESULT rc;

	NEEDGRAMMAR( "GramObj.appendList" );

	// we need to create a datablock which contains a single SRWORD

	CPointerChar pData;

	SDATA sData;
	sData.dwSize = ( strlen(word) + 12 ) & ~3;
	sData.pData = pData = new TCHAR[ sData.dwSize ];

	SRWORD * pWord = (SRWORD *)( sData.pData );
	pWord->dwSize = sData.dwSize;
	pWord->dwWordNum = 0;
	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, word, -1, NULL, 0 );
		CPointerChar wordW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, word, -1, wordW, size_needed );*/
		CComBSTR bstrWord( word );
		wcscpy( pWord->szWord, bstrWord );
	#else
		strcpy( pWord->szWord, word );
	#endif

	ISRGramCFGPtr pISRGramCFG;
	rc = m_pISRGramCommon->QueryInterface(
		__uuidof(ISRGramCFG), (void **)&pISRGramCFG );
	onINVALIDINTERFACE( rc, "appendList not support for this type of grammar" )
	RETURNIFERROR( rc, "QueryInterface(ISRGramCFG)" );

	#ifdef UNICODE
		/*size_needed = ::MultiByteToWideChar( CP_ACP, 0, listName, -1, NULL, 0 );
		CPointerChar listNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, listName, -1, listNameW, size_needed );*/
		CComBSTR bstrListName( listName );
		rc = pISRGramCFG->ListAppend( bstrListName, sData );
	#else
		rc = pISRGramCFG->ListAppend( listName, sData );
	#endif
	onINVALIDCHAR( rc, pISRGramCFG, "Invalid word in word list" );
	onINVALIDLIST( rc, "The list %s is not defined in the grammar", listName );
	RETURNIFERROR( rc, "GramObj.appendList" );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::PhraseFinish(
	DWORD dwFlags, PSRPHRASE pSRPhrase, LPUNKNOWN pIUnknown )
{
	// do nothing if there is no results object
	
	if( pIUnknown == NULL )
	{
		return TRUE;
	}
	
	// do nothing if we do not have a callback

	if( m_pResultsCallback == NULL )
	{
		return TRUE;
	}

	// do nothing if the recognition was not for this grammar object and the
	// special allResults flag is not set

	BOOL bReject = ( dwFlags & ISRNOTEFIN_RECOGNIZED ) == 0;
	BOOL bOther  = ( dwFlags & ISRNOTEFIN_THISGRAMMAR ) == 0;

	if( ( bReject || bOther ) && !m_bAllResults )
	{
		return TRUE;
	}

	// here we create a results object which will be returned

	CResultObject * pObj = resobj_new();
	PyObject * pResObj = (PyObject*)pObj;
	
	if( pObj == NULL || !pObj->create( m_pDragCode, pIUnknown ) )
	{
		// can't create results object
		Py_XDECREF( pResObj );
		return TRUE;
	}

	// if this result is a reject or recognition for another grammar then
	// create a string object; otherwise, create a list of words object

	PyObject * pDetails;

	if( bReject )
	{
		pDetails = Py_BuildValue( "s", "reject" );
	}
	else if( bOther )
	{
		pDetails = Py_BuildValue( "s", "other" );
	}
	else
	{
		pDetails = pObj->getResults( 0 );
		if( pDetails == NULL )
		{
			// can't compute the recognition results
			Py_XDECREF( pResObj );
			return TRUE;
		}
	}

	// now make the callback

	m_pDragCode->makeResultsCallback(
		m_pResultsCallback,
		Py_BuildValue( "(OO)", pDetails, pResObj ) );
	Py_XDECREF( pDetails );
	Py_XDECREF( pResObj );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::PhraseHypothesis(DWORD dwFlags, PSRPHRASE pSRPhrase )
{
	// do nothing if we do not have a callback

	if( m_pHypothesisCallback == NULL )
	{
		return TRUE;
	}

	// do nothing if the recognition is being rejected

	BOOL bReject = ( dwFlags & ISRNOTEFIN_RECOGNIZED ) == 0;
	if( bReject )
	{
		return TRUE;
	}

	// now convert the results into a list

	PyObject * pList = PyList_New( 0 );

    SRWORD * pWord = (SRWORD *) pSRPhrase->abWords;
    DWORD dwRemaining = pSRPhrase->dwSize - sizeof( SRPHRASE );

    while( dwRemaining > 0 )
    {
		// add the word to the list
		#ifdef UNICODE
			int size_needed = ::WideCharToMultiByte( CP_ACP, 0, pWord->szWord, -1, NULL, 0,  NULL, NULL);
			char * szWordA = new char[ size_needed ];
			::WideCharToMultiByte( CP_ACP, 0, pWord->szWord, -1, szWordA, size_needed, NULL, NULL );

			PyObject * pyWord = Py_BuildValue( "s", szWordA );

			if ( szWordA )
				delete [] szWordA;
		#else
			PyObject * pyWord = Py_BuildValue( "s", pWord->szWord );
		#endif
		PyList_Append( pList, pyWord );
		Py_DECREF( pyWord );

        // move to the next word
        dwRemaining -= pWord->dwSize;
        pWord = (PSRWORD) ((BYTE*) pWord + pWord->dwSize);
    }

	// now make the callback

	m_pDragCode->makeResultsCallback(
		m_pHypothesisCallback, Py_BuildValue( "(O)", pList ) );
	Py_XDECREF( pList );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::setExclusive(BOOL bState )
{
	HRESULT rc;

	NEEDGRAMMAR( "GramObj.setExclusive" );
	
	IDgnSRGramCommonPtr pIDgnSRGramCommon;
	rc = m_pISRGramCommon->QueryInterface(
		__uuidof(IDgnSRGramCommon), (void **)&pIDgnSRGramCommon );
	RETURNIFERROR( rc, "QueryInterface(IDgnSRGramCommon)" );

	rc = pIDgnSRGramCommon->SpecialGrammar( bState != 0 );
	RETURNIFERROR( rc, "GramObj.setExclusive" );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::setContext(char * beforeText, char * afterText )
{
	HRESULT rc;

	NEEDGRAMMAR( "GramObj.setContext" );

	ISRGramDictationPtr pISRGramDictation;
	rc = m_pISRGramCommon->QueryInterface(
		__uuidof(ISRGramDictation), (void **)&pISRGramDictation );
	onINVALIDINTERFACE( rc, "setContext not support for this type of grammar" )
	RETURNIFERROR( rc, "QueryInterface(ISRGramDictation)" );

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, beforeText, -1, NULL, 0 );
		CPointerChar beforeTextW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, beforeText, -1, beforeTextW, size_needed );

		size_needed = ::MultiByteToWideChar( CP_ACP, 0, afterText, -1, NULL, 0 );
		CPointerChar afterTextW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, afterText, -1, afterTextW, size_needed );*/
		CComBSTR bstrBeforeText( beforeText );
		CComBSTR bstrAfterText( afterText );
		rc = pISRGramDictation->Context( bstrBeforeText, bstrAfterText );
	#else
		rc = pISRGramDictation->Context( beforeText, afterText );
	#endif
	RETURNIFERROR( rc, "ISRGramDictation::Context" );
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::setSelectText(char * text )
{
	HRESULT rc;

	NEEDGRAMMAR( "GramObj.setSelectText" );

	IDgnSRGramSelectPtr pIDgnSRGramSelect;
	rc = m_pISRGramCommon->QueryInterface(
		__uuidof(IDgnSRGramSelect), (void **)&pIDgnSRGramSelect );
	onINVALIDINTERFACE( rc, "setSelectText not support for this type of grammar" )
	RETURNIFERROR( rc, "QueryInterface(IDgnSRGramSelect)" );

    SDATA sData;
	sData.dwSize = ( strlen(text) + 4 ) & ~3;
	#ifdef UNICODE
		sData.dwSize = sData.dwSize * 2;
	#endif
	sData.pData = new TCHAR[ sData.dwSize ];
	#ifdef UNICODE
		int size_needed = ::MultiByteToWideChar( CP_ACP, 0, text, -1, NULL, 0 );
		CPointerChar textW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, text, -1, textW, size_needed );
		
		memcpy( sData.pData, textW, wcslen(textW)+1 );

		if ( textW )
			delete [] textW;
	#else
		memcpy( sData.pData, text, strlen(text)+1 );
	#endif

	rc = pIDgnSRGramSelect->WordsSet( sData );
	delete sData.pData;
	RETURNIFERROR( rc, "IDgnSRGramSelect::WordsSet" );
	
	return TRUE;
}

//---------------------------------------------------------------------------

PyObject * CGrammarObject::getSelectText()
{
	HRESULT rc;

	NEEDGRAMMAR( "GramObj.getSelectText" );

	IDgnSRGramSelectPtr pIDgnSRGramSelect;
	rc = m_pISRGramCommon->QueryInterface(
		__uuidof(IDgnSRGramSelect), (void **)&pIDgnSRGramSelect );
	onINVALIDINTERFACE( rc, "setSelectText not support for this type of grammar" )
	RETURNIFERROR( rc, "QueryInterface(IDgnSRGramSelect)" );
	
	SDATA sData;

	rc = pIDgnSRGramSelect->WordsGet( &sData );
	RETURNIFERROR( rc, "IDgnSRGramSelect::WordsGet" );

	#ifdef UNICODE
		int size_needed = ::WideCharToMultiByte( CP_ACP, 0, (const wchar_t*)sData.pData, -1, NULL, 0,  NULL, NULL);
		char * pDataA = new char[ size_needed ];
		::WideCharToMultiByte( CP_ACP, 0, (const wchar_t*)sData.pData, -1, pDataA, size_needed, NULL, NULL );

		PyObject * pRetn = Py_BuildValue( "s", pDataA );

		if ( pDataA )
			delete [] pDataA;
	#else	
		PyObject * pRetn = Py_BuildValue( "s", sData.pData );
	#endif

	CoTaskMemFree( sData.pData );
		
	return pRetn;
}

//---------------------------------------------------------------------------

BOOL CGrammarObject::getGrammarGuid(GUID * pGrammarGuid )
{
	HRESULT rc;

	// Note this is not called from Python directly but as a side effect of
	// calling getSelectText from CResultObject.
	NEEDGRAMMAR( "ResObj.getSelectInfo" );

	IDgnSRGramCommonPtr pIDgnSRGramCommon;
	rc = m_pISRGramCommon->QueryInterface(
		__uuidof(IDgnSRGramCommon), (void **)&pIDgnSRGramCommon );
	RETURNIFERROR( rc, "QueryInterface(IDgnSRGramCommon)" );
	
	rc = pIDgnSRGramCommon->Identify( pGrammarGuid );
	RETURNIFERROR( rc, "IDgnSRGramCommon::Identify" );

	return TRUE;
}
