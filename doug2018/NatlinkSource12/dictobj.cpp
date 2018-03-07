/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 dictobj.cpp
	Implementation of the CDictObj class which encapulates a VoiceDictation
	object and is exposed in Python as a DictObj.
*/

#include "stdafx.h"
#include "DragCode.h"
#include "DictObj.h"
#include "ResObj.h"
#include "Excepts.h"

// We use this macro to make sure the dictation object is usable
#define MUSTBEUSABLE( func ) \
	if( m_pIVoiceDictation == NULL ) \
	{ \
		reportError( errNatError, \
			"This dictation object is no longer usable (calling %s)", func ); \
		return FALSE; \
	}

/////////////////////////////////////////////////////////////////////////////
// This utility class will make sure that the text object is locked when
// we access it.  When created, this object calls Lock but only if we know
// that we are not locked.  Then when this object is deleted because it
// goes out of scope, the lock is released.

class CGrabLock
{
 public:
	CGrabLock( IVDct0Text * pIText, BOOL bCreateLock = TRUE );
	~CGrabLock();

	static HRESULT setLock( IVDct0Text * pIText );

 protected:
	// if this is not NULL then we have the lock
	IVDct0TextPtr m_pIText;
};

//---------------------------------------------------------------------------

inline CGrabLock::CGrabLock( IVDct0Text * pIText, BOOL bCreateLock )
{
	if( bCreateLock && !FAILED( setLock( pIText ) )  )
	{
		m_pIText = pIText;
	}
}

//---------------------------------------------------------------------------

inline CGrabLock::~CGrabLock()
{
	if( m_pIText )
	{
		m_pIText->UnLock();
	}
}

//---------------------------------------------------------------------------
// This is a static routine so we can share the logic when we need to set
// the lock outside of this class.

HRESULT CGrabLock::setLock( IVDct0Text * pIText )
{
	HRESULT rc;
	
	// Here we get the text lock.  It is possible that the Lock call will
	// return E_PENDING if the VoiceDictation object is busy with another
	// thread.  In that case, the correct behavior is to sleep a little and
	// then try again.

	rc = pIText->Lock();
	while( rc == E_PENDING )
	{
		Sleep( 20 );
		rc = pIText->Lock();
	}

	return rc;
}

/////////////////////////////////////////////////////////////////////////////
//
// This is the main voice dictation notification sink which we use to
// detect the TextChanged and TextSelChanged callbacks.
//
// When a recognition occurs we usually get either a TextChanged or a
// TextSelChanged callback.  Although because of a coding bug (?) we get
// both when a "Scratch That" command occurs.
//
// The JITPause callback which happens at the start of recognition.
//

class CVDct0NotifySink :
	public CComObjectRoot,
	public IVDct0NotifySink,
	public IDgnVDctNotifySink,
	public IDgnGetSinkFlags
{
public:
	CVDct0NotifySink() { m_pParent = 0; }
	
BEGIN_COM_MAP(CVDct0NotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(IVDct0NotifySink), IVDct0NotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(IDgnVDctNotifySink), IDgnVDctNotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(IDgnGetSinkFlags), IDgnGetSinkFlags)
END_COM_MAP()

public:

	STDMETHOD (Command) (DWORD ) { return S_OK; }
	STDMETHOD (TextSelChanged) (); // not inline
	STDMETHOD (TextChanged) (DWORD); // not inline
	STDMETHOD (TextBookmarkChanged) (DWORD) { return S_OK; }
	STDMETHOD (PhraseStart) () { return S_OK; }
	#ifdef UNICODE
		STDMETHOD (PhraseFinish) (DWORD, PSRPHRASEW) { return S_OK; }
		STDMETHOD (PhraseHypothesis) (DWORD, PSRPHRASEW) { return S_OK; }
	#else
		STDMETHOD (PhraseFinish) (DWORD, PSRPHRASEA) { return S_OK; }
		STDMETHOD (PhraseHypothesis) (DWORD, PSRPHRASEA) { return S_OK; }
	#endif
	
	STDMETHOD (UtteranceBegin) () { return S_OK; }
	STDMETHOD (UtteranceEnd) () { return S_OK; }
	STDMETHOD (VUMeter) (WORD) { return S_OK; }
	STDMETHOD (AttribChanged) (DWORD) { return S_OK; }
	STDMETHOD (Interference) (DWORD) { return S_OK; }
	STDMETHOD (Training) (DWORD) { return S_OK; }
	#ifdef UNICODE
		STDMETHOD (Dictating) (const wchar_t*, BOOL) { return S_OK; }
	#else
		STDMETHOD (Dictating) (const char*, BOOL) { return S_OK; }
	#endif

	STDMETHOD (ErrorHappened) (LPUNKNOWN ) { return S_OK; }
	STDMETHOD (WarningHappened) (LPUNKNOWN ) { return S_OK; }
	STDMETHOD (JITPause) (); // not inline
	STDMETHOD (HotKeyHappened) (DWORD ) { return S_OK; }

	STDMETHOD (SinkFlagsGet) (DWORD* );	// not inline

	// this is our parent
	CDictObj * m_pParent;
};

//---------------------------------------------------------------------------

STDMETHODIMP CVDct0NotifySink::SinkFlagsGet( DWORD * pdwFlags )
{
	// Dragon NaturallySpeaking allows sink object to have a separate
	// interface called IDgnGetSinkFlags.  That interface implements a
	// single function which is call by Drgaon NaturallySpeaking when the
	// sink is first registered.
	//
	// if IDgnGetSinkFlags exists, SinkFlagsGet returns a list of the
	// notifications we want.  This interface is optional.
	
	m_pParent->m_pDragCode->logMessage("+ CVDct0NotifySink::SinkFlagsGet\n");
	if( pdwFlags )
	{
		*pdwFlags =
				// only get the notifications we handle
			DGNDICTSINKFLAG_SENDTEXTCHANGED |
			DGNDICTSINKFLAG_SENDTEXTSELCHANGED |
			DGNDICTSINKFLAG_SENDJITPAUSE;
	}
	
	m_pParent->m_pDragCode->logMessage("- CVDct0NotifySink::SinkFlagsGet\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CVDct0NotifySink::TextSelChanged()
{
	// We get this callback if a recognition has caused the selection to
	// change within the internal buffer without a corresponding change in
	// the text.
	
	m_pParent->m_pDragCode->logMessage("+ CVDct0NotifySink::TextSelChanged\n");
	if( m_pParent )
	{
		m_pParent->TextSelChanged();
	}
	
	m_pParent->m_pDragCode->logMessage("- CVDct0NotifySink::TextSelChanged\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CVDct0NotifySink::TextChanged( DWORD dwReason )
{
	// We get this callback if a recognition has caused the text to change
	// within the internal buffer.  The parameter (a reason code) is not
	// currently used in Dragon NaturallySpeaking and can be ignored.
	
	m_pParent->m_pDragCode->logMessage("+ CVDct0NotifySink::TextChanged\n");
	if( m_pParent )
	{
		m_pParent->TextChanged( dwReason );
	}
	
	m_pParent->m_pDragCode->logMessage("- CVDct0NotifySink::TextChanged\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CVDct0NotifySink::JITPause()
{
	// We get this callback when recognition is about to start but before
	// the voice dictation object has activated its grammars.  This allows
	// us to make sure we are in sync with the internal buffer.
	
	m_pParent->m_pDragCode->logMessage("+ CVDct0NotifySink::JITPause\n");
	if( m_pParent )
	{
		m_pParent->JITPause();
	}
	
	m_pParent->m_pDragCode->logMessage("- CVDct0NotifySink::JITPause\n");
	return S_OK;
}

/////////////////////////////////////////////////////////////////////////////
//
// CDictObj
//

//---------------------------------------------------------------------------

BOOL CDictObj::create( CDragonCode * pDragCode )
{
	m_nLockCount = 0;
	m_pBeginCallback = NULL;
	m_pChangeCallback = NULL;
	m_pIVoiceDictation = NULL;
	m_pIVDctText = NULL;
	m_pDragCode = pDragCode;
	m_pNextDictObj = NULL;

	//-----
	// here we do the actual work of connecting to the dictation object

	HRESULT rc;

	if( m_pDragCode == NULL || m_pDragCode->pISRCentral() == NULL )
	{
		reportError( errNatError,
			"Calling DictObj() is not allowed before calling natConnect" );
		return FALSE;
	}

	// get the voice dictation object

	rc = m_pDragCode->getSiteObj()->QueryService(
		__uuidof(DgnVDct), __uuidof(IVoiceDictation0),
		(void**)&m_pIVoiceDictation );
	RETURNIFERROR( rc, "IServiceProvider::QueryService(VoiceDictate)" );

	// create the main notify sink

	CComObject<CVDct0NotifySink> * pVDctSinkObj = 0;
	IVDct0NotifySinkPtr pIVDctSink;

	rc = CComObject<CVDct0NotifySink>::CreateInstance( &pVDctSinkObj );
	RETURNIFERROR( rc, "CreateInstance(GramNotifySink)" );

	pVDctSinkObj->m_pParent = this;

	rc = pVDctSinkObj->QueryInterface(
		__uuidof(IVDct0NotifySink), (void**)&pIVDctSink );
	RETURNIFERROR( rc, "QueryInterface(IVDct0NotifySink)" );

	// register the notify sink

	m_pIVoiceDictation->Register(
		TEXT( "NatLink Python Interface" ),	// application name; RW TEXT macro added
		TEXT( "" ),							// topic name (unused by NatSpeak)
		NULL,								// session data (unused by NatSpeak)
		TEXT( "" ),									// site name (unused by NatSpeak)
		pIVDctSink,							// sink interface
		__uuidof(IVDct0NotifySink),			// type of sink
		0 );								// flags

	// get the text interface pointer
	
	rc = m_pIVoiceDictation->QueryInterface(
		__uuidof(IVDct0Text), (void**)&m_pIVDctText );
	RETURNIFERROR( rc, "QueryInterface(IVDct0Text)" );

	// now we add ourself to the CDragonCode linked list so all the grammars
	// can be freed when we disconnect

	m_pDragCode->addDictObj( this );

	return TRUE;
}

//---------------------------------------------------------------------------

void CDictObj::destroy()
{
	setBeginCallback( Py_None );
	setChangeCallback( Py_None );

	if( m_pIVDctText )
	{
		m_pIVDctText->Release();
		m_pIVDctText = NULL;
	}
	
	if( m_pIVoiceDictation )
	{
		m_pIVoiceDictation->Release();
		m_pIVoiceDictation = NULL;

		m_pDragCode->removeDictObj( this );
	}
}

//---------------------------------------------------------------------------

BOOL CDictObj::setBeginCallback( PyObject *pCallback )
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

BOOL CDictObj::setChangeCallback( PyObject *pCallback )
{
	if( pCallback == Py_None )
	{
		Py_XDECREF( m_pChangeCallback );
		m_pChangeCallback = NULL;
	}
	else
	{
		Py_XINCREF( pCallback );
		Py_XDECREF( m_pChangeCallback );
		m_pChangeCallback = pCallback;
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::activate( HWND hWnd )
{
	HRESULT rc;
	
	MUSTBEUSABLE( "activate" )
	
	if( hWnd != NULL && !IsWindow( hWnd ) )
	{
		reportError( errBadWindow,
			"The handle %d does not refer to an existing window", hWnd );
		return FALSE;
	}

	rc = m_pIVoiceDictation->Activate( hWnd );
	RETURNIFERROR( rc, "IVoiceDictation0::Activate" );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::deactivate()
{
	HRESULT rc;
	
	MUSTBEUSABLE( "deactivate" )
	
	rc = m_pIVoiceDictation->Deactivate();
	RETURNIFERROR( rc, "IVoiceDictation0::Deactivate" );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::setLock( BOOL bState )
{
	HRESULT rc;

	MUSTBEUSABLE( "setLock" )

	if( bState )
	{
		rc = CGrabLock::setLock( m_pIVDctText );
		RETURNIFERROR( rc, "IVDct0Text::Lock" );

		m_nLockCount += 1;
	}
	else
	{
		if( m_nLockCount == 0 )
		{
			reportError( errWrongState,
				"The dictation object was not locked" );
			return FALSE;
		}

		rc = m_pIVDctText->UnLock();
		RETURNIFERROR( rc, "IVDct0Text::UnLock" );
		
		m_nLockCount -= 1;
	}

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::setText( const char * pText, int nStart, int nEnd )
{
	HRESULT rc;
	
	MUSTBEUSABLE( "setText" )

	// if the Python program did not lock the buffer then we gran the lock
	// for the duration of this routine
	CGrabLock lock( m_pIVDctText, !m_nLockCount );

	if( !computeRange( nStart, nEnd ) )
	{
		return FALSE;
	}

	// the last parameter is the dwReason which is ignored
	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pText, -1, NULL, 0 );
		CPointerChar pTextW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, pText, -1, pTextW, size_needed );*/
		CComBSTR bstrText( pText );
		rc = m_pIVDctText->TextSet( nStart, nEnd, bstrText, 0 );
	#else
		rc = m_pIVDctText->TextSet( nStart, nEnd, pText, 0 );
	#endif
	RETURNIFERROR( rc, "IVDct0Text::TextSet" );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::setTextSel( int nStart, int nEnd )
{
	HRESULT rc;
	
	MUSTBEUSABLE( "setTextSel" )
	
	// if the Python program did not lock the buffer then we gran the lock
	// for the duration of this routine
	CGrabLock lock( m_pIVDctText, !m_nLockCount );
	
	if( !computeRange( nStart, nEnd ) )
	{
		return FALSE;
	}
	
	rc = m_pIVDctText->TextSelSet( nStart, nEnd );
	RETURNIFERROR( rc, "IVDct0Text::TextSelSet" );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::setVisibleText( int nStart, int nEnd )
{
	HRESULT rc;
	
	MUSTBEUSABLE( "setVisibleText" )

	// if the Python program did not lock the buffer then we gran the lock
	// for the duration of this routine
	CGrabLock lock( m_pIVDctText, !m_nLockCount );

	if( !computeRange( nStart, nEnd ) )
	{
		return FALSE;
	}
	
	// This is a Dragon specific function so we use a different interface
	IDgnVDctTextPtr pIDgnVDctText;
	rc = m_pIVoiceDictation->QueryInterface(
		__uuidof(IDgnVDctText), (void**)&pIDgnVDctText );
	RETURNIFERROR( rc, "QueryInterface(IDgnVDctText)" );

	rc = pIDgnVDctText->VisibleTextSet( nStart, nEnd );
	RETURNIFERROR( rc, "IDgnVDctText::VisibleTextSet" );

	return TRUE;
}

//---------------------------------------------------------------------------

PyObject * CDictObj::getLength()
{
	MUSTBEUSABLE( "getLength" )

	// if the Python program did not lock the buffer then we gran the lock
	// for the duration of this routine
	CGrabLock lock( m_pIVDctText, !m_nLockCount );

	int nLength;
	if( !computeLength( nLength ) )
	{
		return NULL;
	}
	
	return Py_BuildValue( "i", nLength );
}

//---------------------------------------------------------------------------

PyObject * CDictObj::getText( int nStart, int nEnd )
{
	HRESULT rc;
	
	MUSTBEUSABLE( "getText" )
	
	// if the Python program did not lock the buffer then we gran the lock
	// for the duration of this routine
	CGrabLock lock( m_pIVDctText, !m_nLockCount );
	
	if( !computeRange( nStart, nEnd ) )
	{
		return NULL;
	}

	if( nStart == nEnd )
	{
		// special case of an empty range, just return an empty string
		return Py_BuildValue( "s", "" );
	}

	SDATA sData;
	sData.dwSize = 0;
	sData.pData = NULL;
	rc = m_pIVDctText->TextGet( nStart, nEnd, &sData );
	RETURNIFERROR( rc, "IVDct0Text::TextGet" );

	if( sData.pData == NULL )
	{
		// we sometimes return NULL when we mean an empty string
		return Py_BuildValue( "s", "" );
	}
	else
	{
		#ifdef UNICODE
			int size_needed = ::WideCharToMultiByte( CP_ACP, 0, (wchar_t *)sData.pData, -1, NULL, 0,  NULL, NULL);
			char * pDataA = new char[ size_needed ];
			::WideCharToMultiByte( CP_ACP, 0, (wchar_t *)sData.pData, -1, pDataA, size_needed, NULL, NULL );

			PyObject * pRetn = Py_BuildValue( "s", pDataA );

			if ( pDataA )
				delete [] pDataA;

		#else
			PyObject * pRetn = Py_BuildValue( "s", (char *)(sData.pData) );
		#endif
		CoTaskMemFree( sData.pData );
		return pRetn;
	}
}

//---------------------------------------------------------------------------

PyObject * CDictObj::getTextSel()
{
	HRESULT rc;
	
	MUSTBEUSABLE( "getTextSel" )

	// if the Python program did not lock the buffer then we gran the lock
	// for the duration of this routine
	CGrabLock lock( m_pIVDctText, !m_nLockCount );

	DWORD dwStart;
	DWORD dwCount;
	rc = m_pIVDctText->TextSelGet( &dwStart, &dwCount );
	RETURNIFERROR( rc, "IVDct0Text::TextSelGet" );

	// convert start,count into start,end
	return Py_BuildValue( "(ii)", dwStart, dwStart+dwCount );
}

//---------------------------------------------------------------------------

PyObject * CDictObj::getVisibleText()
{
	HRESULT rc;
	
	MUSTBEUSABLE( "getVisibleText" )

	// if the Python program did not lock the buffer then we gran the lock
	// for the duration of this routine
	CGrabLock lock( m_pIVDctText, !m_nLockCount );

	// This is a Dragon specific function so we use a different interface
	IDgnVDctTextPtr pIDgnVDctText;
	rc = m_pIVoiceDictation->QueryInterface(
		__uuidof(IDgnVDctText), (void**)&pIDgnVDctText );
	RETURNIFERROR( rc, "QueryInterface(IDgnVDctText)" );

	DWORD dwStart;
	DWORD dwCount;
	rc = pIDgnVDctText->VisibleTextGet( &dwStart, &dwCount );
	RETURNIFERROR( rc, "IDgnVDctText::VisibleTextGet" );

	// convert start,count into start,end
	return Py_BuildValue( "(ii)", dwStart, dwStart+dwCount );
}

//---------------------------------------------------------------------------
// There is no call in NatSpeak to get the length of the internal buffer.
// To compute the length, we get all the text in the window and measure its
// length.  Ugly and slow.
//
// This function can only be called when a lock is in effect.

BOOL CDictObj::computeLength( int & nCount )
{
	HRESULT rc;

	// as an optimization, we do not have to get all the text, just from the
	// end of the selection
	DWORD dwSelStart;
	DWORD dwSelCount;
	rc = m_pIVDctText->TextSelGet( &dwSelStart, &dwSelCount );
	RETURNIFERROR( rc, "IVDct0Text::TextSelGet" );

	SDATA sData;
	sData.dwSize = 0;
	sData.pData = NULL;
	rc = m_pIVDctText->TextGet( dwSelStart+dwSelCount, 0x7FFFFFFF, &sData );
	RETURNIFERROR( rc, "IVDct0Text::TextGet" );

	if( sData.pData == NULL )
	{
		nCount = dwSelStart + dwSelCount;
	}
	else
	{
		#ifdef UNICODE
			nCount = dwSelStart + dwSelCount + wcslen( (const wchar_t*)sData.pData );
		#else
			nCount = dwSelStart + dwSelCount + strlen( (const char*)sData.pData );
		#endif
		CoTaskMemFree( sData.pData );
	}

	return TRUE;
}

//---------------------------------------------------------------------------
// This function converts a Python nStart,nEnd pair into a nStart,nCount
// pair.  In general we are very forgiving of the Python input mimicing the
// behavior of the slicing operation.

BOOL CDictObj::computeRange( int & nStart, int & nEndCount )
{
	// because computing the length can be slow, we only do it if necessary
	
	int nLength = -1;

	// A negative start is converted into characters from the end
	if( nStart < 0 )
	{
		if( nLength == -1 && !computeLength(nLength) ) return FALSE;
		nStart = nLength + nStart;
	}

	// A negavive end if converted into characters from the end
	if( nEndCount < 0 )
	{
		if( nLength == -1 && !computeLength(nLength) ) return FALSE;
		nEndCount = nLength + nEndCount;
	}

	// Now we convert the end position into a count
	if( nEndCount < nStart )
	{
		nEndCount = 0;
	}
	else
	{
		nEndCount = nEndCount - nStart;
	}

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::TextChanged( DWORD dwReason )
{
	HRESULT rc;

	// We ignore the reason code.  It is not set by NatSpeak
	dwReason;

	// if there is no callback then there is nothing to do
	if( !m_pChangeCallback )
	{
		return TRUE;
	}

	// Grab the lock (always) for the duration of this function.
	CGrabLock lock( m_pIVDctText );

	// Ask NatSpeak for what region of text changed
	DWORD dwNewStart;
	DWORD dwNewEnd;
	DWORD dwOldStart;
	DWORD dwOldEnd;
	rc = m_pIVDctText->GetChanges(
			&dwNewStart, &dwNewEnd, &dwOldStart, &dwOldEnd );
	RETURNIFERROR( rc, "IVDct0Text::GetChanges" );

	// get the new selection
	DWORD dwSelStart;
	DWORD dwSelCount;
	rc = m_pIVDctText->TextSelGet( &dwSelStart, &dwSelCount );
	RETURNIFERROR( rc, "IVDct0Text::TextSelGet" );

	PyObject * pArgs;

	if( dwNewEnd > dwNewStart )
	{
		// If there is text, get the text and compute the python results
		SDATA sData;
		sData.dwSize = 0;
		sData.pData = NULL;
		rc = m_pIVDctText->TextGet( dwNewStart, dwNewEnd-dwNewStart, &sData );
		RETURNIFERROR( rc, "IVDct0Text::TextGet" );

		if( sData.pData == NULL )
		{
			// we sometimes return NULL when we mean an empty string
			pArgs = Py_BuildValue( "(iisii)",
		   		dwOldStart, dwOldEnd, "", dwSelStart, dwSelStart+dwSelCount );
		}
		else
		{
			#ifdef UNICODE
				int size_needed = ::WideCharToMultiByte( CP_ACP, 0, (wchar_t *)sData.pData, -1, NULL, 0,  NULL, NULL);
				char * pDataA = new char[ size_needed ];
				::WideCharToMultiByte( CP_ACP, 0, (wchar_t *)sData.pData, -1, pDataA, size_needed, NULL, NULL );

				pArgs = Py_BuildValue( "(iisii)",
					dwOldStart, dwOldEnd, pDataA,
					dwSelStart, dwSelStart+dwSelCount );
				if ( pDataA )
					delete [] pDataA;

			#else
				pArgs = Py_BuildValue( "(iisii)",
					dwOldStart, dwOldEnd, (char *)sData.pData,
					dwSelStart, dwSelStart+dwSelCount );
			#endif
			CoTaskMemFree( sData.pData );
		}
	}
	else
	{
		// otherwise, do not bother getting the text, just compute the
		// python results
		pArgs = Py_BuildValue( "(iisii)",
			dwOldStart, dwOldEnd, "", dwSelStart, dwSelStart+dwSelCount );
	}

	// now make the callback (this calls DECREF on pArgs)
	m_pDragCode->makeResultsCallback( m_pChangeCallback, pArgs );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::TextSelChanged()
{
	HRESULT rc;

	// if there is no callback then there is nothing to do
	if( !m_pChangeCallback )
	{
		return TRUE;
	}

	// Grab the lock (always) for the duration of this function.
	CGrabLock lock( m_pIVDctText );

	// get the new selection
	DWORD dwSelStart;
	DWORD dwSelCount;
	rc = m_pIVDctText->TextSelGet( &dwSelStart, &dwSelCount );
	RETURNIFERROR( rc, "IVDct0Text::TextSelGet" );

	// compute the python results; note that there is no deleted region or
	// changed text
	PyObject * pArgs = Py_BuildValue( "(iisii)",
		dwSelStart, dwSelStart, "", dwSelStart, dwSelStart+dwSelCount );

	// now make the callback (this calls DECREF on pArgs)
	m_pDragCode->makeResultsCallback( m_pChangeCallback, pArgs );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDictObj::JITPause()
{
	// if there is no callback then there is nothing to do
	if( !m_pBeginCallback )
	{
		return TRUE;
	}

	// compute the callback information
	m_pDragCode->logMessage("+ CDictObj::JITPause\n");
	PyObject * pInfo = m_pDragCode->getCurrentModule();
	if( pInfo == NULL )
	{
		pInfo = Py_BuildValue( "(ssi)", "", "", 0 );
	}

	// make the callback
	m_pDragCode->logMessage("  CDictObj::JITPause making callback\n");
	m_pDragCode->makeCallback( m_pBeginCallback, Py_BuildValue( "(O)", pInfo ) );

	// clean up
	Py_XDECREF( pInfo );
	m_pDragCode->logMessage("- CDictObj::JITPause\n");
	return TRUE;
}
