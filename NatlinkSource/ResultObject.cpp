/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 resobj.cpp
 	Contains the code which implements the results object functions.
*/

#include "stdafx.h"
#include "DragCode.h"
#include "ResultObject.h"
#include "Exceptions.h"
#include "GrammarObject.h"

// This macro is used at the top of functions which can not be called
// when no grammar has been loaded
#define MUSTBETINITED( func ) \
	if( m_pISRResBasic == NULL ) \
	{ \
		reportError( errNatError, \
			"This results object is no longer usable (calling %s)", func ); \
		return FALSE; \
	}

//---------------------------------------------------------------------------
// Utility subroutine.  Takes an array of words and returns a newly
// allocated SRPHRASE structure.

SRPHRASE * makePhrase( PCCHAR * ppWords )
{
	// first we count the words and measure their total size; remember to
	// account for the terminator and to round the total length needed to a
	// multiple of four

	int nLength = 0;
	int nCount = 0;

	for( nCount = 0; ppWords[nCount]; nCount++ )
	{
		int length = strlen( ppWords[nCount] ) + 1;
		#ifdef UNICODE
			length = length * 2;
		#endif
		length = ( length + 3 ) & ~3;
		nLength += length;
	}

	// now we can build the SRPHRASE
	
	DWORD dwSize = nLength + nCount * sizeof(SRWORD) + sizeof(SRPHRASE);

	SRPHRASE * pSRPhrase = (SRPHRASE *) new BYTE[ dwSize ];
	pSRPhrase->dwSize = dwSize;
	SRWORD * pWord = (SRWORD *)( pSRPhrase->abWords );

	for( int i = 0; i < nCount; i++ )
	{
		#ifdef UNICODE
			/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, ppWords[i], -1, NULL, 0 );
			CPointerChar ppWordsW = new TCHAR[ size_needed ];*/
			CComBSTR bstrWord( ppWords[i] );
			//::MultiByteToWideChar( CP_ACP, 0, ppWords[i], -1, ppWordsW, size_needed );

			wcscpy( pWord->szWord, bstrWord );
		#else
			strcpy( pWord->szWord, ppWords[i] );
		#endif
		
		int length = strlen( ppWords[i] ) + 1;
		#ifdef UNICODE
			length = length * 2;
		#endif
		length = ( length + 3 ) & ~3;

		pWord->dwSize = sizeof(SRWORD) + length;
		pWord->dwWordNum = 0;

		pWord = (SRWORD *)( (BYTE *)pWord + pWord->dwSize );
	}
	assert( (DWORD)pWord - (DWORD)pSRPhrase == dwSize );

	return pSRPhrase;

	
}

/////////////////////////////////////////////////////////////////////////////
//
// CResObj
//

//---------------------------------------------------------------------------

BOOL CResObj::create( CDragonCode * pDragCode, LPUNKNOWN pIUnknown )
{
	HRESULT rc;

	m_pISRResBasic = NULL;
	m_pDragCode = pDragCode;
	m_pNextResObj = NULL;

	m_pDragCode->addResObj( this );
	
	// here we get the ResBasic interface
	if( pIUnknown == NULL )
	{
		return FALSE;
	}
	rc = pIUnknown->QueryInterface(
			__uuidof(ISRResBasic), (void**)&m_pISRResBasic );
	if( FAILED(rc) ) return FALSE; // do not throw from this constructor

	// The following code is necessary to preserve the wave information so
	// that we could use this utterance for playback and/or enrollment.  It
	// is inefficient to save this information for every utterance but in
	// the initial version of this module, I find it easier to save this
	// information by default.

	ISRResMemoryPtr pISRResMemory;
	rc = m_pISRResBasic->QueryInterface(
			__uuidof(ISRResMemory), (void**)&pISRResMemory );
	if( FAILED(rc) ) return FALSE; // do not throw from this constructor

	rc = pISRResMemory->LockSet( TRUE );
	if( FAILED(rc) ) return FALSE; // do not throw from this constructor

	return TRUE;
}

//---------------------------------------------------------------------------

void CResObj::destroy()
{
	if( m_pISRResBasic )
	{
		m_pISRResBasic->Release();
		m_pISRResBasic = NULL;

		m_pDragCode->removeResObj( this );
	}
}

//---------------------------------------------------------------------------

PyObject * CResObj::getResults( int nChoice )
{
	HRESULT rc;

	MUSTBETINITED( "ResObj.getResults" );
	
	// our goal is to produce a Python array of tuples where each tuple is
	// the recognized word (string) and the rule number which contains that
	// word (integer).

	PyObject * pList = PyList_New( 0 );

	ISRResGraphPtr pGraph;
	rc = m_pISRResBasic->QueryInterface(
		__uuidof(ISRResGraph), (void**)&pGraph );
	RETURNIFERROR( rc, "QueryInterface(ResGraph)" );

	// we preallocate 512 words for the best path and hope the grammar does
	// not include something larger
	
	DWORD aPath[ 512 ];
	DWORD pathSize;
	rc = pGraph->BestPathWord( nChoice, aPath, sizeof(aPath), &pathSize );
	onVALUEOUTOFRANGE( rc, "There is no result number %d", nChoice );
	RETURNIFERROR( rc, "ISRResGraph::BestPathWord" );

	// value returned is actually the byte count
	DWORD nCount = pathSize / sizeof(DWORD);

	for( DWORD i = 0; i < nCount; i++ )
	{
		SRRESWORDNODE node;

		// we support a maximum word size of 128 plus overhead
		BYTE aBuffer[ 140 ];
		SRWORD * pWord = (SRWORD *)aBuffer;
		DWORD sizeNeeded;

		rc = pGraph->GetWordNode(
			aPath[i], &node, pWord, sizeof(aBuffer), &sizeNeeded );
		RETURNIFERROR( rc, "ISRResGraph::GetWordNode" );
		#ifdef UNICODE
			int size_needed = ::WideCharToMultiByte( CP_ACP, 0, pWord->szWord, -1, NULL, 0,  NULL, NULL);
			char * szWordA = new char[ size_needed ];
			::WideCharToMultiByte( CP_ACP, 0, pWord->szWord, -1, szWordA, size_needed, NULL, NULL );

			PyObject * pTuple =
				Py_BuildValue( "(si)", szWordA, node.dwCFGParse );

			if ( szWordA )
				delete [] szWordA;
		#else
			PyObject * pTuple =
				Py_BuildValue( "(si)", pWord->szWord, node.dwCFGParse );
#endif
		PyList_Append( pList, pTuple );
		Py_XDECREF( pTuple );
	}

	return pList;
}

//---------------------------------------------------------------------------
// ISRResBasic::PhraseGet is a more efficient way of getting the results
// information because we only have to make one COM call instead one COM
// call per word in the results.

PyObject * CResObj::getWords( int nChoice )
{
	HRESULT rc;

	MUSTBETINITED( "ResObj.getWords" );

	// we preallocate 1024 bytes for the results and if we need more
	// information then we make the call twice

	DWORD dwSize = 1024;
	CPointer<SRPHRASE> pPhrase = (PSRPHRASE) new BYTE[dwSize];
	pPhrase->dwSize = dwSize;

	DWORD dwSizeNeeded;
	rc = m_pISRResBasic->PhraseGet( nChoice, pPhrase, dwSize, &dwSizeNeeded );
	if( rc == SRERR_NOTENOUGHDATA )
	{
		dwSize = dwSizeNeeded;
		pPhrase = (PSRPHRASE) new BYTE[dwSize];
		pPhrase->dwSize = dwSize;
		rc = m_pISRResBasic->PhraseGet( nChoice, pPhrase, dwSize, &dwSizeNeeded );
	}
	onVALUEOUTOFRANGE( rc, "There is no result number %d", nChoice );
	RETURNIFERROR( rc, "ISRResBasic::PhraseGet" );

	// now convert the results into a list

	PyObject * pList = PyList_New( 0 );

    SRWORD * pWord = (SRWORD *) pPhrase->abWords;
    DWORD dwRemaining = pPhrase->dwSize - sizeof( SRPHRASE );

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

	return pList;
}

//---------------------------------------------------------------------------

PyObject * CResObj::correction( PCCHAR * ppWords )
{
	HRESULT rc;

	MUSTBETINITED( "ResObj.getResults" );

	CPointer<SRPHRASE> pPhrase = makePhrase( ppWords );

	ISRResCorrectionPtr pResCorrection;
	rc = m_pISRResBasic->QueryInterface(
		__uuidof(ISRResCorrection), (void**)&pResCorrection );
	RETURNIFERROR( rc, "QueryInterface(ResCorrection)" );

	rc = pResCorrection->Correction( pPhrase, SRCORCONFIDENCE_VERY );
	onINVALIDCHAR( rc, pResCorrection, "Invalid word in ResObj.correction transcript" );
	RETURNIFERROR( rc, "ISRResCorrect::Correction" );

	// returns S_OK if training succeeds and S_FALSE otherwise.
	return Py_BuildValue( "i", rc == S_OK );
}

//---------------------------------------------------------------------------

PyObject * CResObj::getWave()
{
	HRESULT rc;
	
	ISRResAudioPtr pIResAudio;
	rc = m_pISRResBasic->QueryInterface(
		__uuidof(ISRResAudio), (void**)&pIResAudio );
	RETURNIFERROR( rc, "QueryInterface(ISRResAudio)" );

	SDATA sData;
	sData.dwSize = 0;
	sData.pData = 0;

	rc = pIResAudio->GetWAV( &sData );
	onNOTENOUGHDATA( rc, "The wave data is no longer available for this result" );
	RETURNIFERROR( rc, "ISRResAudio::GetWAV" );

	PyObject * pData = Py_BuildValue( "s#", (char *)(sData.pData), sData.dwSize );
	CoTaskMemFree( sData.pData );
	return pData;
}

//---------------------------------------------------------------------------

PyObject * CResObj::getWordInfo( int nChoice )
{
	HRESULT rc;

	if( m_pISRResBasic == NULL ) 
	{ 
		reportError( errNatError, 
			"This results object is no longer usable (calling %s)", "getWordInfo" ); 
		return FALSE; 
	}

	// our goal is to produce a Python array of tuples where each tuple is
	// the recognized word (string) and the rule number which contains that
	// word (integer).

	PyObject * pList = PyList_New( 0 );

	ISRResGraphPtr pGraph;
	rc = m_pISRResBasic->QueryInterface(
		__uuidof(ISRResGraph), (void**)&pGraph );
	RETURNIFERROR( rc, "QueryInterface(SRResGraph)" );

	IDgnSRResGraphPtr pDgnGraph;
	rc = m_pISRResBasic->QueryInterface(
		__uuidof(IDgnSRResGraph), (void**)&pDgnGraph );
	RETURNIFERROR( rc, "QueryInterface(DgnDRResGraph)" );

	ILexPronouncePtr pLexPron;
	rc = m_pDragCode->pISRCentral()->QueryInterface(
		__uuidof(ILexPronounce), (void**)&pLexPron );
	RETURNIFERROR( rc, "QueryInterface(ILexPronounce)" );

	// get the real start and end times so we can compute the relative start
	// and end times for each word

	QWORD qwStartTime;
	QWORD qwEndTime;
	rc = m_pISRResBasic->TimeGet( &qwStartTime, &qwEndTime );
	RETURNIFERROR( rc, "ISRResBasic::TimeGet" );

	// we preallocate 512 words for the best path and hope the grammar does
	// not include something larger
	
	DWORD aPath[ 512 ];
	DWORD pathSize;
	rc = pGraph->BestPathWord( nChoice, aPath, sizeof(aPath), &pathSize );
	onVALUEOUTOFRANGE( rc, "There is no result number %d", nChoice );
	RETURNIFERROR( rc, "ISRResGraph::BestPathWord" );

	// value returned is actually the byte count
	DWORD nCount = pathSize / sizeof(DWORD);

	for( DWORD i = 0; i < nCount; i++ )
	{
		DGNSRRESWORDNODE node;

		// we support a maximum word size of 128 plus overhead
		BYTE aBuffer[ 140 ];
		SRWORD * pWord = (SRWORD *)aBuffer;
		DWORD sizeNeeded;

		rc = pDgnGraph->GetWordNode(
			aPath[i], &node, aBuffer, sizeof(aBuffer), &sizeNeeded );
		RETURNIFERROR( rc, "ISRResGraph::GetWordNode" );

		// this reads out the word information
		TCHAR pronBuf[ 64 ];
		pronBuf[0] = 0;

		DgnEngineInfo info;
		info.dwFlags = 0;
		info.dwWordNum = 0;

		DWORD dwPronSize;
		DWORD dwInfoSize;

		rc = pLexPron->Get(
			CHARSET_ENGINEPHONETIC, pWord->szWord, 0,
			&pronBuf[0], sizeof(pronBuf), &dwPronSize,
			0,	// part of speech
			(BYTE*)&info, sizeof(DgnEngineInfo), &dwInfoSize );
		RETURNIFERROR( rc, "ILexPronounce::Get" )

		#ifdef UNICODE
			int size_needed = ::WideCharToMultiByte( CP_ACP, 0, pWord->szWord, -1, NULL, 0,  NULL, NULL);
			char * szWordA = new char[ size_needed ];
			::WideCharToMultiByte( CP_ACP, 0, pWord->szWord, -1, szWordA, size_needed, NULL, NULL );

			size_needed = ::WideCharToMultiByte( CP_ACP, 0, pronBuf, -1, NULL, 0,  NULL, NULL);
			char * pronBufA = new char[ size_needed ];
			::WideCharToMultiByte( CP_ACP, 0, pronBuf, -1, pronBufA, size_needed, NULL, NULL );

			PyObject * pTuple =
				Py_BuildValue(
					"(siiiiis)",
					szWordA, node.dwCFGParse, node.dwWordScore,
					(int)(node.qwStartTime - qwStartTime),
					(int)(node.qwEndTime - qwStartTime),
					info.dwFlags, pronBufA );

			if ( szWordA )
				delete [] szWordA;
			if ( pronBufA )
				delete [] pronBufA;
		#else
			PyObject * pTuple =
				Py_BuildValue(
					"(siiiiis)",
					pWord->szWord, node.dwCFGParse, node.dwWordScore,
					(int)(node.qwStartTime - qwStartTime),
					(int)(node.qwEndTime - qwStartTime),
					info.dwFlags, pronBuf );
		#endif

		PyList_Append( pList, pTuple );
		Py_XDECREF( pTuple );
	}

	return pList;
}

//---------------------------------------------------------------------------

PyObject * CResObj::getSelectInfo( CGramObj * pGrammar, int nChoice )
{
	HRESULT rc;

	if( m_pISRResBasic == NULL ) 
	{ 
		reportError( errNatError, 
			"This results object is no longer usable (calling %s)", "getWordInfo" ); 
		return FALSE; 
	}

	// The recognizer call to the select information requires that you pass
	// in the GUID of the grammar.  We go to the grammar to get the GUID.
	// The Python programmer will have passed in the grammar pointer.
	GUID grammarGUID;
	if( !pGrammar->getGrammarGuid( &grammarGUID ) )
	{
		return NULL;
	}

	IDgnSRResSelectPtr pIDgnSRResSelect;
	rc = m_pISRResBasic->QueryInterface(
		__uuidof(IDgnSRResSelect), (void**)&pIDgnSRResSelect );
	RETURNIFERROR( rc, "QueryInterface(IDgnSRResSelect)" );

	DWORD dwStart;
	DWORD dwEnd;
	DWORD dwWordNum;
	rc = pIDgnSRResSelect->GetInfo(
		grammarGUID, nChoice, &dwStart, &dwEnd, &dwWordNum );
	onVALUEOUTOFRANGE( rc, "There is no result number %d", nChoice );
	onNOTASELECTGRAMMAR( rc, "Result number %d was not from a Select grammar", nChoice );
	onDOESNOTMATCHGRAMMAR( rc, "Result number %d was not from the indicated grammar", nChoice );
	RETURNIFERROR( rc, "IDgnSRResSelect::GetInfo" );
	
	return Py_BuildValue( "(ii)", dwStart, dwEnd );
}
