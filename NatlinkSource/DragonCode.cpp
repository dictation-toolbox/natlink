/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 dragcode.cpp
	This file contains the guts of the natlink functionality.
*/

//---------------------------------------------------------------------------
//
// Notes about nested callbacks:
//
// NatSpeak is free to call into this code whenever we are in a Windows
// message loop.  We will be in a Windows message loop once initialization
// has ended.  We will also be in a Windows message loop while waiting for
// any of the following commands to complete:
//
//		playString
//		execScript
//		recognitionMimic
//		playEvents
//		inputFromFile
//
// When we are in a Windows message loop another COM callback from NatSpeak
// can come in which can cause us to make a nested call back into Python.
// For example:
//
// - NatSpeak sends us PhraseFinish.  We post ourself a WM_SENDRESULTS message
// - We get the WM_SENDRESULTS message and call the Results callback into the
//		Python interpreter
// - The gotResults Python code calls recognitionMimic
// - We set up a recognition mimic operation and enter a Windows message
//		loop. We are still in the recognitionMimic call from Python and
//		the Python code is still being called from the Results callback.
// - NatSpeak sends us a Paused message when the recognition mimic starts.
// - We call the Begin callback into the Python interpreter.
//
// At this point we have two nested calls to the Python interpreter on the
// stack.  This should not be a problem although it appears a little
// convoluted.  The user needs to be aware that when they do a playString,
// execScript or recognitionMimic, another Python callback is possible.
//
// To simplify things, we do not make a Change callback while we are nested
// in another callback.  This, at least, prevents us from changing users
// while in the middle of processing another command.
//
// The natlinkmain program is also written to avoid reloading changed Python
// modules during a nested callback.  It uses the getCallbackDepth function
// to make this test.
//
// Notes on PhraseFinish synchronization:
//
// Dragon NaturallySpeaking has two places where the recognition loop can be
// paused.  First, at the start of recognition, NatSpeak calls all the
// clients with a (JIT) Pause.  Further processing is then suspended until
// every client responds with Resume. This gives the clients a change to
// create new grammars or activate existing grammars before recognition
// starts.
//
// In this code, we translate this into a "Begin" callback for the
// natlinkmain module followed by a Begin callback for every grammar.
// Recognition is not resumed until each Python callback ends (they are
// called sequentially).
//
// The second place where recognition is paused is when processing results.
// NatSpeak will not start a new recognition until all previous recognitions
// finish processing their results.  This is controlled by the PhraseFinish
// callbacks from NatSpeak.  Until every PhraseFinish callback is done,
// NatSpeak will not continue with recognitions.
//
// PhraseFinish callbacks from NatSpeak are translated into a "Results"
// (gotResults) callback into the Python module for the winning grammar. But
// if the Python code includes a recognitionMimic operation then it will not
// return from the callback until the recognitionMimic completes which will,
// in turn, prevent the recognition loop from starting the next (mimic'ed)
// recognition.  This results in a deadlock (actually a timeout).
//
// To get around this, we do not callback into Python code from a
// PhraseFinish callback.  Instead we post ourselves a message to do the
// callback after returning from the PhraseFinish call. Then we set a flag
// to tell us that we should not respond to the next Paused callback from
// NatSpeak until all our clients have finished processing their Results
// (PhraseFinish) callbacks.
//
// If the client code executes recognitionMimic or execScript then we reset
// this synchronization flag and let the next recognition proceed normally.
//
// Notes on Python threading:
//
// Normally you do not have to worry about threading in Python.  Although
// this subsystem has multiple threads, only one thread is every used in
// conjunction with Python.  However, when used in other systems which both
// include message loops and support Python threading, we need to cleanly
// lock and unlock the Python interpreter to support threading.
//
// If you pass a TRUE flag to natConnect then we enble Python threading
// support.  When enabled, we unlock the Python whenever we enter a message
// loop and we make sure that we establish the Python thread state in all
// COM callbacks.
//
// Notes on message loops and dialog boxes:
//
// When I wrote a sample application which added speech to a dialog box
// written using the PythonWin package I noticed that dialog box messages
// (like alt+p to press a button) were not being processed froma
// RecogognitionMimic.  This is because we enter out own message loop during
// RecogognitionMimic processing.  To make the dialog box messages work, I
// added code to the message loop to process dialog box messages.
//
// This solution is a hack.  It is not clean Windows programming and it is
// incomplete.  For example, it will not handle accelerators in a main
// window.  Normally, this is not a problem since this code is not usually
// used to speech enable a Python program using Windows UI but it can be so
// you should be aware of the limitations.
//



#include "stdafx.h"
#include "Resource.h"
#include "DragonCode.h"
#include "GrammarObject.h"
#include "ResultObject.h"
#include "DictationObject.h"
#include "COM/appsupp.h"
#include "MessageWindow.h"
#include "Exceptions.h"
#include <cstring>

// defined in PythWrap.cpp
CResultObject * resobj_new();

// This macro is used at the top of functions which can not be called
// during initialization
#define NOTDURING_INIT( func ) \
	if( m_bDuringInit ) \
	{ \
		reportError( errNatError, \
			"Calling %s is not allowed during initialization", func ); \
		return FALSE; \
	}

// This macro is used at the top of functions which can not be called
// during a paused (begin) callback
#define NOTDURING_PAUSED( func ) \
	if( m_bDuringPaused ) \
	{ \
		reportError( errNatError, \
			"Calling %s is not allowed from gotBegin callback", func ); \
		return FALSE; \
	}

// This macro is used at the top of functions which can not be called
// before the user successfully calls natConnect
#define NOTBEFORE_INIT( func ) \
	if( m_pISRCentral == NULL ) \
	{ \
		reportError( errNatError, \
			"Calling %s is not allowed before calling natConnect", func ); \
		return FALSE; \
	}

//---------------------------------------------------------------------------
// This class is used to prevent reentrency.  It sets a variable when first
// created and resets that variable when the class is destroyed.  Look in
// CDgnSRNotifySink::inputFromFile for an example of its use.

class CInFunction
{
 public:
	CInFunction( BOOL * pbFlag ) { 
		m_pbFlag = pbFlag;
		m_bOldVal = *m_pbFlag;
		*m_pbFlag = TRUE;
	}
	~CInFunction() { *m_pbFlag = m_bOldVal; }
	BOOL wasAlreadySet() { return m_bOldVal; }
 protected:
	BOOL * m_pbFlag;
	BOOL m_bOldVal;
};

//---------------------------------------------------------------------------
// This class is used to ensure that we aquire the Python global lock around
// callbacks.  We do nothing is pThreadState is NULL which means that we are
// not supporting threads.

class CLockPython
{
 public:
	CLockPython( PyThreadState * pThreadState ) {
		m_pThreadState = pThreadState;
		if( m_pThreadState )
		{
			PyEval_AcquireThread( m_pThreadState );
		}
	}

	~CLockPython() {
		if( m_pThreadState )
		{
			PyEval_ReleaseThread( m_pThreadState );
		}
	}
	
 protected:
	PyThreadState * m_pThreadState;
};

//---------------------------------------------------------------------------
// These macros correspond to Py_BEGIN_ALLOW_THREADS and
// Py_END_ALLOW_THREADS.  Note that we do not execute this code if
// m_pThreadState is NULL which means that we are not supporting threads.

#define MY_BEGIN_ALLOW_THREADS \
	PyThreadState *_save; \
	if( m_pThreadState ) \
		_save = PyEval_SaveThread();

#define MY_END_ALLOW_THREADS \
	if( m_pThreadState ) \
		PyEval_RestoreThread( _save );

//---------------------------------------------------------------------------
// Here are the various windows messages we send ourself.  We give this
// window message some random value to avoid conflicts.

// this is used to detect when playback is done
#define WM_PLAYBACK (WM_USER+345)

// Used to detect when script execution is done
#define WM_EXECUTION (WM_USER+346)

// For when we get the AttribChanged2 notify sink callback
#define WM_ATTRIBCHANGED (WM_USER+347)

// For when we get a Paused notify sink callback
#define WM_PAUSED (WM_USER+348)

// For when we should send results callback
#define WM_SENDRESULTS (WM_USER+349)

// For when we get teh MimicDone notify sink callback
#define WM_MIMICDONE (WM_USER+350)

// Tells the waitForSpeech window to hide itself
#define WM_HIDEWINDOW (WM_USER+351)

// For the tray icon
#define WM_TRAYICON (WM_USER+352)

// These are the bits for m_dwPendingCallback
#define PENDING_SPEAKER	0x0001
#define PENDING_MICSTATE 0x0002

// invalid flag for testFileName
#define INVALID_WAVEFILE 0xFFFFFFFF

// name of the Start rule for the empty grammar
#define START TEXT( "Start" ) // RW TEXT macro added

/////////////////////////////////////////////////////////////////////////////
//
// This is an engine notification sink.
//

class CDgnSRNotifySink :
	public CComObjectRoot,
	public IDgnSREngineNotifySink,
	public ISRNotifySink,
	public IDgnGetSinkFlags
{
public:
	CDgnSRNotifySink() { m_pParent = 0; }
	
BEGIN_COM_MAP(CDgnSRNotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(IDgnSREngineNotifySink), IDgnSREngineNotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(ISRNotifySink), ISRNotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(IDgnGetSinkFlags), IDgnGetSinkFlags)
END_COM_MAP()

public:

	STDMETHOD (OkToTerminate)  () { return S_OK; }
	STDMETHOD (Terminate) 	   ( BOOL ) { return S_OK; }
	STDMETHOD (AttribChanged2) ( DWORD ); // not inline
	STDMETHOD (Paused)         ( QWORD ); // not inline
	STDMETHOD (MimicDone)      ( DWORD, LPUNKNOWN ); // not inline
	STDMETHOD (ErrorHappened)  ( LPUNKNOWN ) { return S_OK; }
	#ifdef UNICODE // RW added ANSI/UNICODE versions
		STDMETHOD (Progress)       ( int, const wchar_t * ) { return S_OK; }
	#else
		STDMETHOD (Progress)       ( int, const char * ) { return S_OK; }
	#endif
  	STDMETHOD (AttribChanged)  ( DWORD ) { return S_OK; }
  	STDMETHOD (Interference)   ( QWORD, QWORD, DWORD ) { return S_OK; }
  	STDMETHOD (Sound)          ( QWORD, QWORD ) { return S_OK; }
  	STDMETHOD (UtteranceBegin) ( QWORD ) { return S_OK; }
  	STDMETHOD (UtteranceEnd)   ( QWORD, QWORD ) { return S_OK; }
  	STDMETHOD (VUMeter)        ( QWORD, WORD ) { return S_OK; }
   
	STDMETHOD (SinkFlagsGet) (DWORD* ); // not inline

	// this is our parent
	CDragonCode * m_pParent;
};

//---------------------------------------------------------------------------

STDMETHODIMP CDgnSRNotifySink::SinkFlagsGet( DWORD * pdwFlags )
{
	m_pParent->logMessage("+ CDgnSRNotifySink::SinkFlagsGet\n");
	if( pdwFlags )
	{
		*pdwFlags =
				// send just-in-time paused before grammars are loaded
			DGNSRSINKFLAG_SENDJITPAUSED |
				// send AttribChanged messages
			DGNSRSINKFLAG_SENDATTRIB |
				// send MimicDone message
			DGNSRSINKFLAG_SENDMIMICDONE;
	}
	m_pParent->logMessage("- CDgnSRNotifySink::SinkFlagsGet\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CDgnSRNotifySink::AttribChanged2( DWORD dwCode )
{
	m_pParent->logMessage("+ CDgnSRNotifySink::AttribChanged2\n");
	assert( m_pParent );
	if( m_pParent )
	{
		m_pParent->postMessage( WM_ATTRIBCHANGED, dwCode, 0 );
	}
	m_pParent->logMessage("- CDgnSRNotifySink::AttribChanged2\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CDgnSRNotifySink::Paused( QWORD qCookie )
{
	m_pParent->logMessage("+ CDgnSRNotifySink::Paused\n");
	m_pParent->logCookie("enter Paused",qCookie);
	assert( m_pParent );
	if( !m_pParent )
	{
		// if we do not have a parent then we gerenate an error since we do
		// not have an engine pointer so we can not call Resume
		return E_UNEXPECTED;
	}

	QWORD * pCookie = new QWORD;
	*pCookie = qCookie;

	m_pParent->postMessage( WM_PAUSED, (WPARAM)pCookie, 0 );
	m_pParent->logMessage("- CDgnSRNotifySink::Paused\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CDgnSRNotifySink::MimicDone(
	DWORD dwClientCode, LPUNKNOWN pIUnknown )
{
	m_pParent->logMessage("+ CDgnSRNotifySink::MimicDone\n");
	assert( m_pParent );
	if( m_pParent )
	{
		if( pIUnknown != NULL )
		{
			pIUnknown->AddRef();
		}
		m_pParent->postMessage( WM_MIMICDONE, dwClientCode, (LPARAM)pIUnknown );
	}

	m_pParent->logMessage("- CDgnSRNotifySink::MimicDone\n");
	return S_OK;
}

/////////////////////////////////////////////////////////////////////////////
//
// This is a playback notification sink.
//

class CDgnSSvcActionNotifySink :
	public CComObjectRoot,
	public IDgnSSvcActionNotifySink
{
public:
	CDgnSSvcActionNotifySink() { m_pParent = 0; }
	
BEGIN_COM_MAP(CDgnSSvcActionNotifySink)
	COM_INTERFACE_ENTRY_IID(__uuidof(IDgnSSvcActionNotifySink), IDgnSSvcActionNotifySink)
END_COM_MAP()

public:
	
	STDMETHOD (PlaybackDone)     ( DWORD );
	STDMETHOD (PlaybackAborted)  ( DWORD, HRESULT );
	STDMETHOD (ExecutionDone)    ( DWORD );
	STDMETHOD (ExecutionStatus)  ( DWORD, DWORD );
	STDMETHOD (ExecutionAborted) ( DWORD, HRESULT, DWORD );

	// this is our parent
	CDragonCode * m_pParent;
};

//---------------------------------------------------------------------------

STDMETHODIMP CDgnSSvcActionNotifySink::PlaybackDone( DWORD dwClientCode )
{
	m_pParent->logMessage("+ CDgnSSvcActionNotifySink::PlaybackDone\n");
	assert( m_pParent );
	if( m_pParent )
	{
		m_pParent->postMessage( WM_PLAYBACK, dwClientCode, 0 );
	}
	m_pParent->logMessage("- CDgnSSvcActionNotifySink::PlaybackDone\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CDgnSSvcActionNotifySink::PlaybackAborted(
	DWORD dwClientCode, HRESULT eCode )
{
	m_pParent->logMessage("+ CDgnSSvcActionNotifySink::PlaybackAborted\n");
	assert( m_pParent );
	if( m_pParent )
	{
		// note that the current Dragon NaturallySpeaking does not generate
		// any meaningful error codes so we just pass some non-zero value
		m_pParent->postMessage( WM_PLAYBACK, dwClientCode, 1 );
	}
	m_pParent->logMessage("- CDgnSSvcActionNotifySink::PlaybackAborted\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CDgnSSvcActionNotifySink::ExecutionDone( DWORD dwClientCode )
{
	m_pParent->logMessage("+ CDgnSSvcActionNotifySink::ExecutionDone\n");
	assert( m_pParent );
	if( m_pParent )
	{
		m_pParent->postMessage( WM_EXECUTION, dwClientCode, 0 );
	}
	m_pParent->logMessage("- CDgnSSvcActionNotifySink::ExecutionDone\n");
	return S_OK;
}

//---------------------------------------------------------------------------
// This callback occurs when a script is being executed and the script
// includes a command which changes the state of the script.  Currently the
// possible status buts are:
//
//	ACTIONSTATUS_F_ALLOWHEARDWORD which means that the script includes a
//		HeardWord command (same as RecognitionMimic) which means that we
//		need to unpause recognition
//
//	ACTIONSTATUS_F_ALLOWUSERINPUT which means that the script is displaying
//		a message box which also means that we need to unpause recognition
//

STDMETHODIMP CDgnSSvcActionNotifySink::ExecutionStatus(
	DWORD dwClientCode, DWORD dwStatus )
{
	m_pParent->logMessage("+ CDgnSSvcActionNotifySink::ExecutionStatus\n");
	if( dwStatus != 0 && m_pParent )
	{
		m_pParent->resetPauseRecog();
	}
	m_pParent->logMessage("- CDgnSSvcActionNotifySink::ExecutionStatus\n");
	return S_OK;
}

//---------------------------------------------------------------------------

STDMETHODIMP CDgnSSvcActionNotifySink::ExecutionAborted(
	DWORD dwClientCode, HRESULT eCode, DWORD iLineNumber )
{
	m_pParent->logMessage("+ CDgnSSvcActionNotifySink::ExecutionAborted\n");
	assert( m_pParent );
	if( m_pParent )
	{
		DWORD * pData = new DWORD[2];
		pData[0] = eCode;
		pData[1] = iLineNumber;

		m_pParent->postMessage( WM_EXECUTION, dwClientCode, (LPARAM)pData );
	}
	m_pParent->logMessage("- CDgnSSvcActionNotifySink::ExecutionAborted\n");
	return S_OK;
}

/////////////////////////////////////////////////////////////////////////////
//
// CMessageStack
//
// I introduced thsi class to fix a bug in the messageLoop where we were in
// nested message loops but got the exit message out of order.  To fix that
// we remember every exit message we get.

class CMessageStack
{
 public:
	CMessageStack( UINT message, WPARAM wParam, CMessageStack * pNext ) :
		m_message(message), m_wParam(wParam), m_pNext(pNext),
		m_lParam(0), m_bTriggered(FALSE) { }
		
	UINT m_message;
	WPARAM m_wParam;
	
	LPARAM m_lParam;
	BOOL m_bTriggered;
	CMessageStack * m_pNext;
};

//---------------------------------------------------------------------------

void CDragonCode::TriggerMessage( UINT message, WPARAM wParam, LPARAM lParam )
{
	for( CMessageStack * pMessage = m_pMessageStack;
		 pMessage; pMessage = pMessage->m_pNext )
	{
		if( pMessage->m_message == message &&
			pMessage->m_wParam == wParam &&
			pMessage->m_bTriggered == FALSE )
		{
			pMessage->m_bTriggered = TRUE;
			pMessage->m_lParam = lParam;
			return;
		}
	}
}

//---------------------------------------------------------------------------

BOOL CDragonCode::IsMessageTriggered(
	UINT message, WPARAM wParam, LPARAM & lParam )
{
	CMessageStack ** ppMessage = &m_pMessageStack;
	
	for( ; *ppMessage; ppMessage = &( (*ppMessage)->m_pNext ) )
	{
		if( (*ppMessage)->m_message == message &&
			(*ppMessage)->m_wParam == wParam &&
			(*ppMessage)->m_bTriggered == TRUE )
		{
			lParam = (*ppMessage)->m_lParam;
			CMessageStack * pSave = *ppMessage;
			*ppMessage = (*ppMessage)->m_pNext;
			delete pSave;
			return TRUE;
		}
	}
	return FALSE;
}

/////////////////////////////////////////////////////////////////////////////
//
// CDragonCode
//

//---------------------------------------------------------------------------
// Note when a posted message comes in, the Python interpreter should be
// unlocked so we first have to establish a thread state and lock the
// interpreter. 

LRESULT CALLBACK hiddenWndProc(
	HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam )
{
	CDragonCode * pDragCode;

	switch( uMsg )
	{
	 case WM_COMMAND:
		// menu command, posted from second thread
		pDragCode = (CDragonCode *)GetWindowLong( hwnd, 0 );
		pDragCode->logMessage("+ hiddenWndProc WM_COMMAND\n");
		if( pDragCode )
		{
			CLockPython cLockPython( pDragCode->getThreadState() );
			pDragCode->onMenuCommand( wParam );
		}
		pDragCode->logMessage("- hiddenWndProc WM_COMMAND\n");
		return 0;
		
	 case WM_ATTRIBCHANGED:
		pDragCode = (CDragonCode *)GetWindowLong( hwnd, 0 );
		pDragCode->logMessage("+ hiddenWndProc WM_ATTRIBCHANGED\n");
		if( pDragCode )
		{
			CLockPython cLockPython( pDragCode->getThreadState() );
			pDragCode->onAttribChanged( wParam );
		}
		pDragCode->logMessage("- hiddenWndProc WM_ATTRIBCHANGED\n");
		return 0;

	 case WM_PAUSED:
		pDragCode = (CDragonCode *)GetWindowLong( hwnd, 0 );
		pDragCode->logMessage("+ hiddenWndProc WM_PAUSED\n");
		if( pDragCode )
		{
			CLockPython cLockPython( pDragCode->getThreadState() );
			pDragCode->onPaused( wParam );
		}
		pDragCode->logMessage("- hiddenWndProc WM_PAUSED\n");
		return 0;

	 case WM_SENDRESULTS:
		pDragCode = (CDragonCode *)GetWindowLong( hwnd, 0 );
		pDragCode->logMessage("+ hiddenWndProc WM_SENDRESULTS\n");
		if( pDragCode )
		{
			CLockPython cLockPython( pDragCode->getThreadState() );
			pDragCode->onSendResults( wParam, lParam );
		}
		pDragCode->logMessage("- hiddenWndProc WM_SENDRESULTS\n");
		return 0;

	 case WM_PLAYBACK:
	 case WM_EXECUTION:
		pDragCode = (CDragonCode *)GetWindowLong( hwnd, 0 );
		pDragCode->logMessage("+ hiddenWndProc WM_PLAYBACK/WM_EXECUTION\n");
		// these are handled in their respective message loops
		pDragCode->logMessage("- hiddenWndProc WM_PLAYBACK/WM_EXECUTION\n");
		return 0;

	 case WM_TIMER:
		pDragCode = (CDragonCode *)GetWindowLong( hwnd, 0 );
		pDragCode->logMessage("+ hiddenWndProc WM_TIMER\n");
		if( pDragCode )
		{
			CLockPython cLockPython( pDragCode->getThreadState() );
			pDragCode->onTimer();
		}
		pDragCode->logMessage("- hiddenWndProc WM_TIMER\n");
		return 0;

	 case WM_TRAYICON:		
		pDragCode = (CDragonCode *)GetWindowLong( hwnd, 0 );
		pDragCode->logMessage("+ hiddenWndProc WM_TRAYICON\n");
		if( pDragCode )
		{
			CLockPython cLockPython( pDragCode->getThreadState() );
			pDragCode->onTrayIcon( wParam, lParam );
		}
		pDragCode->logMessage("- hiddenWndProc WM_TRAYICON\n");
		return 0;
	}
	
	return DefWindowProc( hwnd, uMsg, wParam, lParam );
}

//---------------------------------------------------------------------------
// Returns TRUE if Dragon NaturallySpeaking is running

BOOL CDragonCode::isNatSpeakRunning()
{
	// if NatSpeak is running, the following semaphore will be
	// set to a value of zero (so our wait will timeout)

	HANDLE hSem = CreateSemaphore(
		NULL, 1, 1, 
		TEXT( "Dragon NaturallySpeaking 1.0 -> Server Semaphore") ); // RW TEXT macro added
	if( hSem == NULL )
	{
		return FALSE;
	}

	DWORD res = WaitForSingleObject( hSem, 0 /*no wait*/ );
	if( res == WAIT_OBJECT_0 )
	{
		// we got the semaphore so we must not be running, restore
		// the semaphore and return FALSE
		LONG count;
		ReleaseSemaphore( hSem, 1, &count );
		CloseHandle( hSem );
		return FALSE;
	}

	// otherwise we failed to get the semaphore so assume that
	// NatSpeak is running
	CloseHandle( hSem );
	return TRUE;
}

//---------------------------------------------------------------------------

void CDragonCode::releaseObjects()
{
	// iterate over all the grammar objects and free them; note that when we
	// call unload on a grammar object, the first grammar object in our
	// linked list changes
	while( m_pFirstGramObj )
	{
		CGrammarObject * pOldFirst = m_pFirstGramObj;
		
		m_pFirstGramObj->unload();

		// this should never happen
		if( pOldFirst == m_pFirstGramObj )
		{
			assert( FALSE );
			break;
		}
	}

	// iterate over all results objects and free them
	while( m_pFirstResObj )
	{
		CResultObject * pOldFirst = m_pFirstResObj;
		
		m_pFirstResObj->destroy();

		// this should never happen
		if( pOldFirst == m_pFirstResObj )
		{
			assert( FALSE );
			break;
		}
	}
	
	// iterate over all dictation objects and free them
	while( m_pFirstDictObj )
	{
		CDicationObject * pOldFirst = m_pFirstDictObj;
		
		m_pFirstDictObj->destroy();

		// this should never happen
		if( pOldFirst == m_pFirstDictObj )
		{
			assert( FALSE );
			break;
		}
	}
}

//---------------------------------------------------------------------------

void CDragonCode::onPaused( WPARAM wParam )
{
	QWORD *pCookie = (QWORD *)wParam;
	logCookie("enter on onPaused", *pCookie);
	assert( pCookie );

	if( m_nPauseRecog )
	{
		// whoops, we want to pause recognition for a while (probably
		// because we are processing the results of a previous recognition)
		logMessage("+ CDragonCode::onPaused detefered\n");
		m_deferredCookie = *pCookie;
		logMessage("- CDragonCode::onPaused detefered\n");
	}
	else
	{
		logMessage("+ CDragonCode::onPaused doPausedProcessing\n");
		doPausedProcessing( *pCookie );
		logMessage("- CDragonCode::onPaused doPausedProcessing\n");
	}
	
	delete pCookie;
}

//---------------------------------------------------------------------------

void CDragonCode::doPausedProcessing( QWORD dwCookie )
{
	HRESULT rc;

	logCookie("enter doPausedProcessing",dwCookie);
	// Note: we ignore recognitions which occur during our initialization

	if( !m_bDuringInit )
	{
		// we pass back the results of getCurrentModule

		PyObject * pInfo = getCurrentModule();
		if( pInfo == NULL )
		{
			pInfo = Py_BuildValue( "(ssi)", "", "", 0 );
		}

		// first we call the global callback

		m_bDuringPaused = TRUE;

		if( m_pBeginCallback )
		{
			logMessage("+ CDragonCode::doPausedProcessing beginCallback\n");
			makeCallback(
				m_pBeginCallback,
				Py_BuildValue( "(O)", pInfo ) );
			logMessage("- CDragonCode::doPausedProcessing beginCallback\n");
		}

		// now we call the grammar callbacks

		CGrammarObject * pGramObj;
		for( pGramObj = m_pFirstGramObj;
			 pGramObj != NULL;
			 pGramObj = pGramObj->m_pNextGramObj )
		{
			if( pGramObj->m_pBeginCallback )
			{
				logMessage("+ CDragonCode::doPausedProcessing grammarCallback\n");
				makeCallback(
					pGramObj->m_pBeginCallback,
					Py_BuildValue( "(O)", pInfo ) );
				logMessage("- CDragonCode::doPausedProcessing grammarCallback\n");
			}
		}

		Py_XDECREF( pInfo );
		m_bDuringPaused = FALSE;
	}

	// You must call Resume to get the engine started again.  Just returning
	// from this function is not enough.  For other applications this gives
	// us the flexibility to return from this function and handle the
	// processing later before the recognition loop restarts.
	//
	// If the m_bWaitForResults flag is set then we do not resume just yet
	// but wait for that flag to be reset.

	logCookie("doPausedProcessing Resume",dwCookie);
	rc = m_pIDgnSREngineControl->Resume( dwCookie );
}

//---------------------------------------------------------------------------

void CDragonCode::addGramObj(CGrammarObject * pGramObj )
{
	assert( pGramObj != NULL );
	assert( pGramObj->m_pNextGramObj == NULL );
	
	pGramObj->m_pNextGramObj = m_pFirstGramObj;
	m_pFirstGramObj = pGramObj;
}

//---------------------------------------------------------------------------

void CDragonCode::removeGramObj(CGrammarObject * pGramObj )
{
	assert( pGramObj != NULL );

	// just in case (this should never happen)

	assert( m_pFirstGramObj != NULL );
	if( m_pFirstGramObj == NULL )
	{
		return;
	}

	// is this the first in the linked list

	if( m_pFirstGramObj == pGramObj )
	{
		m_pFirstGramObj = pGramObj->m_pNextGramObj;
		pGramObj->m_pNextGramObj = NULL;
		return;
	}

	// otherwise, we need to find the grammar object in the linked list
	
	CGrammarObject * pCur;
	for( pCur = m_pFirstGramObj;
		 pCur->m_pNextGramObj != NULL;
		 pCur = pCur->m_pNextGramObj )
	{
		if( pCur->m_pNextGramObj == pGramObj )
		{
			pCur->m_pNextGramObj = pGramObj->m_pNextGramObj;
			pGramObj->m_pNextGramObj = NULL;
			return;
		}
	}

	assert( FALSE );
}

//---------------------------------------------------------------------------

void CDragonCode::addResObj(CResultObject * pResObj )
{
	assert( pResObj != NULL );
	assert( pResObj->m_pNextResObj == NULL );
	
	pResObj->m_pNextResObj = m_pFirstResObj;
	m_pFirstResObj = pResObj;
}

//---------------------------------------------------------------------------

void CDragonCode::removeResObj(CResultObject * pResObj )
{
	assert( pResObj != NULL );

	// just in case (this should never happen)

	assert( m_pFirstResObj != NULL );
	if( m_pFirstResObj == NULL )
	{
		return;
	}

	// is this the first in the linked list

	if( m_pFirstResObj == pResObj )
	{
		m_pFirstResObj = pResObj->m_pNextResObj;
		pResObj->m_pNextResObj = NULL;
		return;
	}

	// otherwise, we need to find the results object in the linked list
	
	CResultObject * pCur;
	for( pCur = m_pFirstResObj;
		 pCur->m_pNextResObj != NULL;
		 pCur = pCur->m_pNextResObj )
	{
		if( pCur->m_pNextResObj == pResObj )
		{
			pCur->m_pNextResObj = pResObj->m_pNextResObj;
			pResObj->m_pNextResObj = NULL;
			return;
		}
	}

	assert( FALSE );
}

//---------------------------------------------------------------------------

void CDragonCode::addDictObj(CDicationObject * pDictObj )
{
	assert( pDictObj != NULL );
	assert( pDictObj->m_pNextDictObj == NULL );
	
	pDictObj->m_pNextDictObj = m_pFirstDictObj;
	m_pFirstDictObj = pDictObj;
}

//---------------------------------------------------------------------------

void CDragonCode::removeDictObj(CDicationObject * pDictObj )
{
	assert( pDictObj != NULL );

	// just in case (this should never happen)

	assert( m_pFirstDictObj != NULL );
	if( m_pFirstDictObj == NULL )
	{
		return;
	}

	// is this the first in the linked list

	if( m_pFirstDictObj == pDictObj )
	{
		m_pFirstDictObj = pDictObj->m_pNextDictObj;
		pDictObj->m_pNextDictObj = NULL;
		return;
	}

	// otherwise, we need to find the dictation object in the linked list
	
	CDicationObject * pCur;
	for( pCur = m_pFirstDictObj;
		 pCur->m_pNextDictObj != NULL;
		 pCur = pCur->m_pNextDictObj )
	{
		if( pCur->m_pNextDictObj == pDictObj )
		{
			pCur->m_pNextDictObj = pDictObj->m_pNextDictObj;
			pDictObj->m_pNextDictObj = NULL;
			return;
		}
	}

	assert( FALSE );
}

//---------------------------------------------------------------------------
// This utility function is called by DragCode and GramObj to perform a
// callback and check for errors

void CDragonCode::makeCallback( PyObject *pFunc, PyObject *pArgs )
{
	m_nCallbackDepth += 1;
	PyObject * pRetn = PyEval_CallObject( pFunc, pArgs );
	m_nCallbackDepth -= 1;

	if( PyErr_Occurred() )
	{
		PyErr_Print();
	}

	Py_XDECREF( pRetn );
	Py_XDECREF( pArgs );

	// now if we had deferred sending a change callback because we were in
	// another callback, process it now.

	if( m_nCallbackDepth == 0 )
	{
		if( ( m_dwPendingCallback & PENDING_SPEAKER ) == PENDING_SPEAKER )
		{
			m_dwPendingCallback &= ~PENDING_SPEAKER;
			onAttribChanged( ISRNSAC_SPEAKER );
		}
		if( ( m_dwPendingCallback & PENDING_MICSTATE ) == PENDING_MICSTATE )
		{
			m_dwPendingCallback &= ~PENDING_MICSTATE;
			onAttribChanged( DGNSRAC_MICSTATE );
		}
	}
}

//---------------------------------------------------------------------------
// This is a windows message loop.  We allow Python threads to run during
// this message loop.  We return when we get a specific message and wParam.

LPARAM CDragonCode::messageLoop( UINT message, WPARAM wParam )
{
	MY_BEGIN_ALLOW_THREADS

	// Create a message stack entry
	m_pMessageStack = new CMessageStack( message, wParam, m_pMessageStack );

	MSG msg;
	LPARAM lParam;
	while( GetMessage( &msg, NULL, NULL, NULL ) )
	{
		TriggerMessage( msg.message, msg.wParam, msg.lParam );

		// If we are inside a running dialog box (the top-level window is
		// the magic class named #32770), then we want to make sure that we
		// process the dialog messages.  If we do not do this then a
		// playString of a dialog box message will not work.  This should
		// only effect the case where the dialog box being manipulated is in
		// the same thread as this code.  Otherwise, the IsDialogMessage
		// function should be benign.
		HWND hWnd = GetActiveWindow();
		TCHAR szClassName[ 128 ] = { 0 }; // RW modified char -> TCHAR to cover ANSI/UNICODE
		GetClassName( hWnd, szClassName, 128 );
		if( 0 == _tcscmp( szClassName, TEXT( "#32770" ) ) &&
			IsDialogMessage( hWnd, &msg ) )
		{
			continue;
		}
		
		TranslateMessage(&msg);
		DispatchMessage(&msg);

		if( IsMessageTriggered( message, wParam, lParam ) )
		{
			// This post message will make sure that we enter the loop
			// again to look for any triggered messages.
			PostMessage( msg.hwnd, WM_NULL, 0, 0 );
			break;
		}
	}

	MY_END_ALLOW_THREADS

	return lParam;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::displayText(
	const char * pszText, BOOL bError, BOOL bLogError )
{
	if( m_pSecdThrd )
	{
		m_pSecdThrd->displayText( pszText, bError );
	}
	if( bLogError )
	{
		logMessage( pszText );
	}
	return TRUE;
}

//---------------------------------------------------------------------------

void CDragonCode::onAttribChanged( WPARAM wParam )
{
	DWORD dwCode = wParam;

	// do nothing if there is no callback installed
	
	if( !m_pChangeCallback )
	{
		return;
	}

	// figure out what changes

	const char * pszCode = "";
	PyObject * pInfo;
	
	switch( dwCode )
	{
		
	 case ISRNSAC_SPEAKER:
		if( m_nCallbackDepth || m_bDuringInit )
		{
			// change callbacks are not allowed when we are processing
			// another callback, like a begin utterance.  Therefore, we
			// defer the change request until later
			m_dwPendingCallback |= PENDING_SPEAKER;
			return;
		}
		pszCode = "user";
		pInfo = getCurrentUser();
		if( pInfo == NULL )
		{
			// we can't handle exceptions at this time so we mimic no user
			pInfo = Py_BuildValue( "(ss)", "", "" );
		}
		break;

	 case DGNSRAC_MICSTATE:
		if( m_nCallbackDepth || m_bDuringInit )
		{
			// change callbacks are not allowed when we are processing
			// another callback, like a begin utterance.  Therefore, we
			// defer the change request until later
			m_dwPendingCallback |= PENDING_MICSTATE;
			return;
		}
		pszCode = "mic";
		pInfo = getMicState();
		if( pInfo == NULL )
		{
			// we can't handle exceptions at this time
			pInfo = Py_BuildValue( "s", "error" );
		}
		break;

	 default:
		// nothing changes that we are interested in
		return;
	}

	// now form the parameter and make the Python callback

	makeCallback(
		m_pChangeCallback,
		Py_BuildValue( "(sO)", pszCode, pInfo ) );
	Py_DECREF( pInfo );
}

//---------------------------------------------------------------------------

void CDragonCode::onTimer()
{
	// if there is no timer callback, reset the timer
	
	if( !m_pTimerCallback )
	{
		if( m_nTimer )
		{
			KillTimer( m_hMsgWnd, m_nTimer );
			m_nTimer = 0;
		}
	}

	// make the Python callback (if we are not in another callback)

	else
	if( m_nCallbackDepth == 0 )
	{
		makeCallback( m_pTimerCallback, Py_BuildValue( "()" ) );
	}
}

//---------------------------------------------------------------------------
// This is the routine which is finally exected when a menu command occurs
// in the output window.  We got here via a very long path (WM_COMMAND was
// posted to the output window in the other thread which was then posted to
// the message window in this thread which caused this function to be
// called.)

void CDragonCode::onMenuCommand( WPARAM wParam )
{
	if( LOWORD(wParam) == IDD_RELOAD )
	{
		// currently we do not support this operation if we are using thread
		// support because I have not worked through the issues about what
		// to do about the thread state
		if( m_pThreadState )
		{
			return;	
		}
		
		// reload the Python subsystem
		displayText( "Reloading Python subsystem...\r\n", FALSE, FALSE );

		// Although we do not really care about the Python reference count
		// we do want to reset the callbacks so we do not make a call into
		// an obselete intrepreter.
		setChangeCallback( Py_None );
		setBeginCallback( Py_None );
		setTimerCallback( Py_None );
		setTrayIcon( "", "", Py_None );

		// We call this because the reinitialization will not free up the
		// python objects.  Note that we do free the COM objects but we do
		// not free the Python objects.  This means that we will have a
		// minor memory leak but no object leaks (which would prevent
		// shutdown of NatSpeak).
		releaseObjects();

		m_pAppClass->reloadPython();
	}
}

//---------------------------------------------------------------------------

void CDragonCode::onTrayIcon( WPARAM wParam, LPARAM lParam )
{
	if( m_nCallbackDepth == 0 && m_pTrayIconCallback != NULL &&
		lParam >= WM_LBUTTONDOWN && lParam <= WM_MBUTTONDBLCLK )
	{
		makeCallback( m_pTrayIconCallback, Py_BuildValue( "(i)", lParam ) );
	}
}

//---------------------------------------------------------------------------

void CDragonCode::onSendResults( WPARAM wParam, LPARAM lParam )
{
	PyObject *pFunc = (PyObject *)wParam;
	PyObject *pArgs = (PyObject *)lParam;
	assert( pFunc );
	assert( pArgs );

	// makeCallback calls DECREF on pArgs
	makeCallback( pFunc, pArgs );
	
	// now that results are processed, we can resume recognitions
	resetPauseRecog();
}

//---------------------------------------------------------------------------

void CDragonCode::makeResultsCallback( PyObject *pFunc, PyObject *pArgs )
{
	// setting this will delay recognition at the start of the next
	// utterance until results are processed
	m_nPauseRecog += 1;
	
	postMessage( WM_SENDRESULTS, (WPARAM)pFunc, (LPARAM)pArgs );
}

//---------------------------------------------------------------------------

void CDragonCode::resetPauseRecog()
{
	logCookie("resetPauseRecog", m_deferredCookie);
	if( m_nPauseRecog )
	{
		m_nPauseRecog -= 1;
	}
	
	if( m_nPauseRecog == 0 && m_deferredCookie )
	{
		doPausedProcessing( m_deferredCookie );
		m_deferredCookie = 0;
	}
}

//---------------------------------------------------------------------------
// This test a wave filename for validity.  Returns INVALID_WAVEFILE in case
// of error. Otherwise, it returns the file type.
DWORD CDragonCode::testFileName( const char * pszFileName )
{
	if ( !pszFileName )
		return 0;
	
	// first see if the file exists by trying to open it
	
	#ifdef UNICODE

		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszFileName, -1, NULL, 0 );
		CPointerChar pszFileNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, pszFileName, -1, pszFileNameW, size_needed );*/
		CComBSTR bstrFileName( pszFileName );

		HANDLE hFile = CreateFile(
			bstrFileName,			// pointer to name of the file
			GENERIC_READ,			// access (read-write) mode
			FILE_SHARE_READ,		// share mode
			NULL,					// pointer to security descriptor
			OPEN_EXISTING,			// how to create
			0,						// file attributes
			NULL );					// handle to file with attributes to copy

	#else
		HANDLE hFile = CreateFile(
			pszFileName,			// pointer to name of the file
			GENERIC_READ,			// access (read-write) mode
			FILE_SHARE_READ,		// share mode
			NULL,					// pointer to security descriptor
			OPEN_EXISTING,			// how to create
			0,						// file attributes
			NULL );					// handle to file with attributes to copy
	#endif
	
	if( hFile == INVALID_HANDLE_VALUE )
	{
		reportError( errValueError,
			"The file named %s does not exists or can not be opened (calling %s)",
			pszFileName, "natlink.inputFromFile" );
		return INVALID_WAVEFILE;
	}

	CloseHandle( hFile );

	// then test the extension of the filename
	
	int len = strlen( pszFileName );
	
	char pszExtension[5];
	strcpy( pszExtension, len < 4 ? "" : pszFileName + len-4 );
	_strlwr( pszExtension );
	
	if( 0 == strcmp( pszExtension, ".utd" ) )
	{
		return DGNUTTTYP_COMBINED;
	}
	else
	if( 0 == strcmp( pszExtension, ".utt" ) ||
		0 == strcmp( pszExtension, ".utb" ) )
	{
		return DGNUTTTYP_UTT;
	}
	else
	if( 0 == strcmp( pszExtension, ".wav" ) )
	{
		return DGNUTTTYP_MSWAV;
	}
	else
	if( 0 == strcmp( pszExtension, ".nwv" ) )
	{
		return DGNUTTTYP_NISTWAV;
	}
	else
	{
		reportError( errValueError,
			"The file named %s does not have a legal extension (calling %s)",
			pszFileName, "natlink.inputFromFile" );
		return INVALID_WAVEFILE;
	}
}
//---------------------------------------------------------------------------

void CDragonCode::logMessage( const char * pszText )
{
	if( !m_pszLogFile )
	{
		return;
	}

	// open the log file and write the message.  The logfile is a shared
	// resourceso we may need to retry the open if the logfile is in use.
	FILE * fp = fopen( m_pszLogFile, "at+" );
	for( int i = 0; i < 50 && fp && fp == NULL; i++ )
	{
		Sleep( 1 );
		fp = fopen( m_pszLogFile, "at+" );
	}

	if( fp )
	{
		fputs( pszText, fp );
		fclose( fp );
	}
}

/////////////////////////////////////////////////////////////////////////////
//
// Wait for Speech dialog box
//

//---------------------------------------------------------------------------
// Called when a message is sent to the waitForSpeech dialog box.

BOOL CALLBACK waitDialogProc( 
	HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam )
{
	int nTimeout;
	
	switch( msg )
	{
	 case WM_INITDIALOG:
		nTimeout = (int)lParam;

		// if the timeout is negative then we hide the dialog box; it will
		// only be closed when the timeout occurs
		if( nTimeout < 0 )
		{
			nTimeout = 0 - nTimeout;
			PostMessage( hWnd, WM_HIDEWINDOW, 0, 0 );
		}

		// if the timeout is non-negative then we start a timer which will
		// close the dialog box
		if( nTimeout )
		{
			SetTimer( hWnd, 1, nTimeout, NULL );
		}
		
		return TRUE;

	 case WM_HIDEWINDOW:
		ShowWindow( hWnd, SW_HIDE );
		return TRUE;

	 case WM_TIMER:
		// when the timer expires, we destroy the window
		KillTimer( hWnd, 1 );
		EndDialog( hWnd, IDCANCEL );
		return TRUE;
		
	 case WM_CLOSE:
		EndDialog( hWnd, IDCANCEL );
		return TRUE;

	 case WM_COMMAND:
		if( LOWORD(wParam) == IDCANCEL )
		{
			EndDialog( hWnd, IDCANCEL );
			return TRUE;
		}
		return FALSE;

	 default:
		return FALSE;
	}
}

/////////////////////////////////////////////////////////////////////////////
//
// Initialization functions
//

//---------------------------------------------------------------------------

BOOL CDragonCode::initGetSiteObject( IServiceProvider * & pIDgnSite )
{
	HRESULT rc;

	// We connect to NatSpeak through a site object which is a better way
	// than using the SAPI enumerator objects because it also gives us
	// access to the other DgnSAPI interfaces at the same time.

	if( pIDgnSite != NULL )
	{
		m_pIServiceProvider = pIDgnSite;
	}
	else
	{
		for( int retry = 0; retry < 5; retry++ )
		{
			// DgnSite is the class dragon site object.  IServiceProvider is
			// a Microsoft standard interface.
			rc = CoCreateInstance(
				__uuidof(DgnSite), NULL, CLSCTX_LOCAL_SERVER,
				__uuidof(IServiceProvider), (void **)&m_pIServiceProvider );

			// The CoCreateInstance call is known to occassionally fail with
			// a CO_E_OBJSRV_RPC_FAILURE error but retrying this will get
			// around this unexplained failure.
			if( rc != CO_E_OBJSRV_RPC_FAILURE )
			{
				break;
			}
		}
		RETURNIFERROR( rc, "CoCreateInstance(DgnSite)" );
	}

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::initSecondWindow()
{
	// create a window for posting ourself messages

	HINSTANCE hInstance = _Module.GetModuleInstance();

	WNDCLASSEX regCls;
	memset( &regCls, 0, sizeof(WNDCLASSEX) );
	regCls.cbSize = sizeof(WNDCLASSEX);
	regCls.lpfnWndProc = hiddenWndProc; 
    regCls.hInstance = hInstance;
    regCls.lpszClassName = TEXT( "natlink") ; // RW TEXT macro added
	regCls.cbWndExtra = 4;
	RegisterClassEx( &regCls );

	m_hMsgWnd = CreateWindow(
		TEXT( "natlink" ), // RW TEXT macro added
		TEXT( "natlink" ), // dito
		WS_POPUP,
		0, 0, 0, 0,
		NULL, NULL,
		hInstance, 0 );
	if( !m_hMsgWnd )
	{
		// Note: this is not really a COM error
		reportComError(
			GetLastError(), "CreateWindow", "DragCode.cpp", __LINE__ );
		return FALSE;
	}

	// we store out class pointer in the window's extra data field so we
	// get called back when a menu message occurs
	SetWindowLong( m_hMsgWnd, 0, (LONG)this );

	// tell the thread about out message window
	if( m_pSecdThrd )
	{
		m_pSecdThrd->setMsgWnd( m_hMsgWnd );
	}

	return TRUE;
}

//---------------------------------------------------------------------------
// This returns an allocated datablock which holds a standard SAPI command
// and control grammar.  The specific grammar returned by thus function
// contins an empty list so it will never be recognized.

SDATA makeEmptyGrammar()
{
	// I need the following chunks
	//
	// (1) A SRCKCFG_RULES chunk with a single rule:
	//		SRCFG_STARTOPERATION(SRCGFGO_SEQUENCE)
	//		SRCFG_LIST(1)
	//		SRCFG_ENDOPERATION(SRCFGO_SEQUENCE)
	//
	// (2) A SRCKCFG_EXPORTRULES chunk with the rule "Start"
	//
	// (3) A SRCKCFG_LISTS chunk with the list "Empty"

	// compute the sizes that we need; remember that strings have to be
	// padded.

	DWORD dwStartWordSize = ( _tcslen( START ) + 1 );
	dwStartWordSize = ( dwStartWordSize + 3 ) & ~3;

	DWORD dwEmptyWordSize = ( _tcslen( TEXT( "Empty" ) ) + 1 );
	dwEmptyWordSize = ( dwEmptyWordSize + 3 ) & ~3;

	DWORD dwRuleChunkSize = sizeof(SRCFGRULE) + 3 * sizeof(SRCFGSYMBOL);

	DWORD dwExportChunkSize = sizeof(SRCFGXRULE) + dwStartWordSize;

	DWORD dwListChunkSize = sizeof(SRCFGLIST) + dwEmptyWordSize;

	DWORD dwSize = 
		sizeof(SRHEADER) + 3 * sizeof(SRCHUNK) +
		dwRuleChunkSize + dwExportChunkSize + dwListChunkSize;

	// allocate a buffer which can hold everything

	BYTE * pTemp = new BYTE[ dwSize ];
	
	SDATA sData;
	sData.dwSize = dwSize;
	sData.pData = pTemp;

	// create the header

	SRHEADER * pHeader = (SRHEADER *)pTemp;
	pHeader->dwType = SRHDRTYPE_CFG;
	pHeader->dwFlags = 0;

	pTemp += sizeof(SRHEADER);

	// create the rules chunk

	SRCHUNK * pChunk = (SRCHUNK *)pTemp;
	pChunk->dwChunkID = SRCKCFG_RULES;
	pChunk->dwChunkSize = dwRuleChunkSize;

	SRCFGRULE * pRule = (SRCFGRULE *)pChunk->avInfo;
	pRule->dwSize = dwRuleChunkSize;
	pRule->dwUniqueID = 1;

	SRCFGSYMBOL * pSymbol = (SRCFGSYMBOL *)pRule->abData;

	pSymbol[0].wType = SRCFG_STARTOPERATION;
	pSymbol[0].wProbability = 0;
	pSymbol[0].dwValue = SRCFGO_SEQUENCE;
	
	pSymbol[1].wType = SRCFG_LIST;
	pSymbol[1].wProbability = 0;
	pSymbol[1].dwValue = 1;
	
	pSymbol[2].wType = SRCFG_ENDOPERATION;
	pSymbol[2].wProbability = 0;
	pSymbol[2].dwValue = SRCFGO_SEQUENCE;

	pTemp += dwRuleChunkSize + sizeof(SRCHUNK);

	// create the export chunk

	pChunk = (SRCHUNK *)pTemp;
	pChunk->dwChunkID = SRCKCFG_EXPORTRULES;
	pChunk->dwChunkSize = dwExportChunkSize;

	SRCFGXRULE * pExport = (SRCFGXRULE *)pChunk->avInfo;
	pExport->dwSize = dwExportChunkSize;
	pExport->dwRuleNum = 1;
	_tcscpy( pExport->szString, START );

	pTemp += dwExportChunkSize + sizeof(SRCHUNK);

	// create the import chunk
	
	pChunk = (SRCHUNK *)pTemp;
	pChunk->dwChunkID = SRCKCFG_LISTS;
	pChunk->dwChunkSize = dwListChunkSize;

	SRCFGLIST * pList = (SRCFGLIST *)pChunk->avInfo;
	pList->dwSize = dwExportChunkSize;
	pList->dwListNum = 1;
	_tcscpy( pList->szString, TEXT( "Empty" ) );

	// done

	return sData;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::natConnect( IServiceProvider * pIDgnSite, BOOL bUseThreads )
{
	HRESULT rc;

	NOTDURING_INIT( "natConnect" );
	NOTDURING_PAUSED( "natConnect" );
	
	if( m_pISRCentral )
	{
		natDisconnect();
	}
	assert( m_pISRCentral == NULL );

#ifdef MUSTRUN
	// set the preprocessor variable MUSTRUN inorder to add this test
	//
	// it is not really necessary to start NatSpeak first since the
	// connection to NatSpeak will launch it if necessary but then you do
	// not get to select a user.
	if( !isNatSpeakRunning() )
	{
		reportError(
			"Dragon NaturallySpeaking is not running (calling %s).",
			"natlink.natConnect" );
		return FALSE;
	}
#endif

	// here we start the second thread for displaying messages; we only need
	// this when we are called as a compatibility module

	if( pIDgnSite != NULL )
	{
		m_pSecdThrd = new MessageWindow();
	}

	// Connect to NatSpeak

	if( !initGetSiteObject( pIDgnSite ) )
	{
		return FALSE;
	}

	// Now that we have the site object, we can get an engine object from
	// the SAPI SR interface.  This is what you get from ISREnum::Select.

	rc = m_pIServiceProvider->QueryService(
		__uuidof(DgnDictate), __uuidof(ISRCentral), (void**)&m_pISRCentral );
	RETURNIFERROR( rc, "IServiceProvider::QueryService(DgnDictate)" );

	// This interface contains the microphone logic
	
	rc = m_pISRCentral->QueryInterface(
		__uuidof(IDgnSREngineControl), (void**)&m_pIDgnSREngineControl );
	RETURNIFERROR( rc, "ISRCentral::QueryInterface(IDgnSREngineControl)" );

	// get the speech services interfaces

	IDgnSpeechServicesPtr pSpchSvc;

	rc = m_pIServiceProvider->QueryService(
		__uuidof(SpchServices), _uuidof(IDgnSpeechServices), (void**)&pSpchSvc );
	RETURNIFERROR( rc, "IServiceProvider::QueryService(DgnSpeechServices)" );

	rc = pSpchSvc->QueryInterface(
		__uuidof(IDgnSSvcOutputEvent), (void**)&m_pIDgnSSvcOutputEvent);
	RETURNIFERROR( rc, "IDgnSSvcOutputEvent::QueryInterface(DgnSSvcOutputEvent)" );
	
	rc = m_pIDgnSSvcOutputEvent->QueryInterface(
		__uuidof(IDgnSSvcInterpreter), (void**)&m_pIDgnSSvcInterpreter );
	RETURNIFERROR( rc, "IDgnSSvcOutputEvent::QueryInterface(IDgnSSvcInterpreter)" );

	// we use this interface in getCurrentModule

	rc = m_pIServiceProvider->QueryService(
		__uuidof(DgnExtModSupport), __uuidof(IDgnExtModSupStrings),
		(void**)&m_pIDgnExtModSupStrings );
	RETURNIFERROR( rc, "IServiceProvider::QueryService(DgnExtModSupport)" );

	// here we get the name of the log file
	// RW deactivated writing to the Dragon log file

	/*IDgnExtModSupErrorsPtr pIDgnExtModSupErrors;
	rc = m_pIDgnExtModSupStrings->QueryInterface(
		__uuidof(IDgnExtModSupErrors), (void **)&pIDgnExtModSupErrors );
	RETURNIFERROR( rc, "IServiceProvider::QueryService(DgnExtModSupport)" );

	DWORD dwSize = MAX_PATH;
	DWORD dwSizeNeeded;
	m_pszLogFile = new char[dwSize];
	rc = pIDgnExtModSupErrors->GetLogFileName(
		m_pszLogFile, dwSize, &dwSizeNeeded );
	if( dwSizeNeeded > dwSize )
	{
		delete m_pszLogFile;
		dwSize = dwSizeNeeded;
		m_pszLogFile = new char[dwSize];
		rc = pIDgnExtModSupErrors->GetLogFileName(
			m_pszLogFile, dwSize, &dwSizeNeeded );
	}
	RETURNIFERROR( rc, "IDgnExtModSupErrors::GetLogFileName" );*/

	// create an engine sink and register it
	
	IDgnSREngineNotifySinkPtr pIEngSink;
	CComObject<CDgnSRNotifySink> * pEngSinkObj;

	rc = CComObject<CDgnSRNotifySink>::CreateInstance( &pEngSinkObj );
	RETURNIFERROR( rc, "CComObject<CDgnSRNotifySink>::CreateInstance" );

	rc = pEngSinkObj->QueryInterface(
		__uuidof(IDgnSREngineNotifySink), (void**)&pIEngSink );
	RETURNIFERROR( rc, "CDgnSRNotifySink::QueryInterface" );

	pEngSinkObj->m_pParent = this;

	rc = m_pISRCentral->Register(
		pIEngSink, __uuidof(IDgnSREngineNotifySink), &m_dwKey );
	RETURNIFERROR( rc, "ISRCentral::Register" );

	// create a playback sink and register it

	IDgnSSvcActionNotifySinkPtr pISSvcSink;
	CComObject<CDgnSSvcActionNotifySink> * pSSvcSinkObj;

	rc = CComObject<CDgnSSvcActionNotifySink>::CreateInstance( &pSSvcSinkObj );
	RETURNIFERROR( rc, "CComObject<CDgnSSvcActionNotifySink>::CreateInstance" );

	rc = pSSvcSinkObj->QueryInterface(
		__uuidof(IDgnSSvcActionNotifySink), (void**)&pISSvcSink );
	RETURNIFERROR( rc, "CDgnSSvcActionNotifySink::QueryInterface" );

	pSSvcSinkObj->m_pParent = this;

	rc = m_pIDgnSSvcOutputEvent->Register( pISSvcSink );
	RETURNIFERROR( rc, "IDgnSSvcOutputEvent::Register" );

	rc = m_pIDgnSSvcInterpreter->Register( pISSvcSink );
	RETURNIFERROR( rc, "IDgnSSvcInterpreter::Register" );

	// Used for training

	rc = m_pISRCentral->QueryInterface(
		__uuidof(IDgnSRTraining), (void**)&m_pIDgnSRTraining );
	RETURNIFERROR( rc, "ISRCentral::QueryInterface(IDgnSRTraining)" );

	// Additional initialization

	if( !initSecondWindow() )
	{
		return FALSE;
	}

	// now we create a local Python thread state which we can use in callbacks
	if( !m_pThreadState && bUseThreads )
	{
		PyThreadState * threadStateSave = PyThreadState_Swap( NULL );
		assert( threadStateSave != NULL );
		m_pThreadState = PyThreadState_New( threadStateSave->interp );
		PyThreadState_Swap( threadStateSave );
	}

	return TRUE;
}

/////////////////////////////////////////////////////////////////////////////
//
// Python called functions
//

//---------------------------------------------------------------------------

BOOL CDragonCode::natDisconnect()
{
	NOTDURING_INIT( "natDisconnect" );
	NOTDURING_PAUSED( "natDisconnect" );

	// check for special training mode which we should cancel
	if( m_bSetTraining && m_pIDgnSRTraining != NULL )
	{
		m_pIDgnSRTraining->TrainingCancel();
		m_bSetTraining = FALSE;
	}

	// unregister the engine sink
	if( m_dwKey )
	{
		// The Unregister call will caused NatSpeak to release its
		// references on the notification sink
		m_pISRCentral->UnRegister( m_dwKey );
		m_dwKey = 0;
	}

	// kill the tray icon
	setTrayIcon( "", "", Py_None );

	// free all grammar objects
	releaseObjects();

	// release all our intefaces
	m_pIDgnSREngineControl = NULL;
	m_pIDgnSSvcOutputEvent = NULL;
	m_pIDgnExtModSupStrings = NULL;
	m_pIServiceProvider = NULL;
	m_pIDgnSSvcInterpreter = NULL;
	m_pIDgnSRTraining = NULL;
	m_pISRCentral = NULL;

	// shutdown the second thread
	if( m_pSecdThrd )
	{
		delete m_pSecdThrd;
		m_pSecdThrd = NULL;
	}

	// destroy our hidden window
	if( m_hMsgWnd )
	{
		if( m_nTimer )
		{
			KillTimer( m_hMsgWnd, m_nTimer );
			m_nTimer = 0;
		}
		DestroyWindow( m_hMsgWnd );
		m_hMsgWnd = NULL;
	}

	// free the memory from the log file
	if( m_pszLogFile )
	{
		delete m_pszLogFile;
		m_pszLogFile = NULL;
	}

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::setBeginCallback( PyObject *pCallback )
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

BOOL CDragonCode::setChangeCallback( PyObject *pCallback )
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

PyObject * CDragonCode::getCallbackDepth()
{
	return Py_BuildValue( "i", m_nCallbackDepth );
}

//---------------------------------------------------------------------------

BOOL CDragonCode::playString( const char * pszKeys, DWORD dwFlags )
{
	HRESULT rc;

	NOTBEFORE_INIT( "playString" );
	NOTDURING_INIT( "playString" );
	NOTDURING_PAUSED( "playString" );

	// each request to NatSpeak will have a different request number so we
	// can match up PlaybackDone callbacks.
	static DWORD dwUnique = 1;
	DWORD dwClientCode = ++dwUnique;

	DWORD dwNumUndo;
	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszKeys, -1, NULL, 0 );
		CPointerChar pszKeysW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, pszKeys, -1, pszKeysW, size_needed );*/
		CComBSTR bstrKeys( pszKeys );
		rc = m_pIDgnSSvcOutputEvent->PlayString(
			bstrKeys,	// string to send
			dwFlags,		// flags
			0xFFFFFFFF,		// delay (-1 for app specific delay)
			dwClientCode,	// to identify which WM_PLAYBACK is ours
			&dwNumUndo );	// not used (number of backspaces needed to undo)
	#else
		rc = m_pIDgnSSvcOutputEvent->PlayString(
			pszKeys, 	  // string to send
			dwFlags,	  // flags
			0xFFFFFFFF,   // delay (-1 for app specific delay)
			dwClientCode, // to identify which WM_PLAYBACK is ours
			&dwNumUndo ); // not used (number of backspaces needed to undo)
	#endif

	RETURNIFERROR( rc, "IDgnSSvcOutputEvent::PlayString" );

	// Now we want to wait until the playback finishes or is aborted
	//
	// if we get the message posted by onPlaybackDone and onPlaybackAborted
	// then we exit this windows message loop

	BOOL bAborted = messageLoop( WM_PLAYBACK, dwClientCode );

	if( bAborted )
	{
		// the eCode will be set when we get a PlaybackAborted callback
		// instead of a PlaybackDone callback
		reportError( errNatError,
			"Error returned from playString (calling %s)",
			"natlink.playString" );
		return FALSE;
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getCurrentModule()
{
	HRESULT rc;

	NOTBEFORE_INIT( "getCurrentModule" );

	// get the handle of the current forground window

	logMessage("+ CDragonCode::getCurrentModule\n");
	HWND hWnd = GetForegroundWindow();
	if( hWnd == NULL )
	{
		// This can happen if the current foreground window is closing.
		return Py_BuildValue( "(ssi)", "", "", 0 );
	}

	// get the caption of the current foreground window

	int length = GetWindowTextLength( hWnd ) + 1;
	CPointerChar pTitle = new TCHAR[ length ];
	logMessage("  CDragonCode::getCurrentModule 1\n");
	GetWindowText( hWnd, pTitle, length );
	
	// get the module name of the current foreground window; note that this
	// operation is very complicated under Win32.  Fortunately, Dragon
	// NaturallySpeaking has worked out all the details and has exposed the
	// function for our use.

	DWORD dwLength = _MAX_PATH + 1;
	CPointerChar pModule = new TCHAR[ dwLength ];
	DWORD dwNeeded;

	logMessage("  CDragonCode::getCurrentModule 2\n");

	rc = m_pIDgnExtModSupStrings->GetWindowModuleFileName(
				hWnd, pModule, dwLength, &dwNeeded );
	
	logMessage("  CDragonCode::getCurrentModule 3\n");

	if( rc == E_BUFFERTOOSMALL )
	{
		logMessage("  CDragonCode::getCurrentModule 3a\n");
		dwLength = dwNeeded + 1;
		pModule = new TCHAR[ dwLength ];
		rc = m_pIDgnExtModSupStrings->GetWindowModuleFileName(
					hWnd, pModule, dwLength, &dwNeeded );
	}
	if( rc == HOOKERR_INJECTFAILED )
	{
		// This error sometimes happens when NatSpeak tries to get the
		// module name of the currently active module and fails because the
		// target module is busy or otherwise unable to be accessed through
		// the NatSpeak hooking mechanism.  This condition may be temporary
		// so retrying is always an option.
		logMessage("  CDragonCode::getCurrentModule 3b\n");
		return Py_BuildValue( "(ssi)", "", "", 0 );
	}
	if( rc == HOOKERR_CANNOTINJECT )
	{
		// This error is similar to the error above except that it can not
		// be retried.  However, we do not remember that the error can not
		// be retried and blindly try to repeat the operation over and over
		// again :-).  For now, ignore this error and return unknown app.
		logMessage("  CDragonCode::getCurrentModule 3c\n");
		return Py_BuildValue( "(ssi)", "", "", 0 );
	}
	if( rc == SRERR_INVALIDPARAM )
	{
		// I seem to see this error when switch users; probably because the
		// window is no longer valis and we did not catch this earlier.
		logMessage("  CDragonCode::getCurrentModule 3d\n");
		return Py_BuildValue( "(ssi)", "", "", 0 );
	}		
	logMessage("  CDragonCode::getCurrentModule 4\n");
	RETURNIFERROR( rc, "IDgnExtModSupStrings::GetWindowModuleFileName" );

	// build the result tuple and return
	
	logMessage("  CDragonCode::getCurrentModule 5\n");

	#ifdef UNICODE
		int size_needed = ::WideCharToMultiByte( CP_ACP, 0, pModule, -1, NULL, 0,  NULL, NULL);
		char * pModuleA = new char[ size_needed ];
		::WideCharToMultiByte( CP_ACP, 0, pModule, -1, pModuleA, size_needed, NULL, NULL );

		size_needed = ::WideCharToMultiByte( CP_ACP, 0, pTitle, -1, NULL, 0,  NULL, NULL);
		char * pTitleA = new char[ size_needed ];
		::WideCharToMultiByte( CP_ACP, 0, pTitle, -1, pTitleA, size_needed, NULL, NULL );
		
		return Py_BuildValue( "(ssi)",	pModuleA, pTitleA, hWnd );

		if ( pModuleA )
			delete [] pModuleA;
		if ( pTitleA )
			delete [] pTitleA;

	#else
		return Py_BuildValue( "(ssi)", pModule, pTitle, hWnd );
	#endif

}

//---------------------------------------------------------------------------
PyObject * CDragonCode::getCurrentUser()
{
	HRESULT rc;

	NOTBEFORE_INIT( "getCurrentUser" );
	
	// first we get the name of the speaker.  If there is no speaker loaded
	// we return empty strings

	ISRSpeakerPtr pISRSpeaker;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(ISRSpeaker), (void**)&pISRSpeaker );
	RETURNIFERROR( rc, "ISRCentral::QueryInterface(ISRSpeaker)" );

	DWORD dwLength = _MAX_PATH + 1;
	CPointerChar pUser = new TCHAR[ dwLength ];
	DWORD dwNeeded;
	rc = pISRSpeaker->Query( pUser, dwLength, &dwNeeded );
	if( rc == E_BUFFERTOOSMALL )
	{
		dwLength = dwNeeded + 1;
		pUser = new TCHAR[ dwLength ];
		rc = pISRSpeaker->Query( pUser, dwLength, &dwNeeded );
	}
	if( rc == SRERR_NOUSERSELECTED )
	{
		return Py_BuildValue( "(ss)", "", "" );
	}
	RETURNIFERROR( rc, "ISRSpeaker::Query" );

	// now we get the speaker directory 
		
	IDgnSRSpeakerPtr pIDgnSRSpeaker;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(IDgnSRSpeaker), (void**)&pIDgnSRSpeaker );
	RETURNIFERROR( rc, "ISRCentral::QueryInterface(IDgnSRSpeaker)" );

	dwLength = _MAX_PATH + 11;
	CPointerChar pPath = new TCHAR[ dwLength ];
	rc = pIDgnSRSpeaker->GetSpeakerDirectory( 
		pUser, pPath, dwLength, &dwNeeded );
	if( rc == E_BUFFERTOOSMALL )
	{
		dwLength = dwNeeded + 11;
		pPath = new TCHAR[ dwLength ];
		rc = pIDgnSRSpeaker->GetSpeakerDirectory( 
			pUser, pPath, dwLength, &dwNeeded );
	}
	RETURNIFERROR( rc, "IDgnSRSpeaker::GetSpeakerDirectory" );

	// NatSpeak returns the base user directory, we append "current" to get
	// us to where the files are.
	_tcscat( pPath, TEXT( "\\current" ) );

	// return the Python information

	#ifdef UNICODE
		int size_needed = ::WideCharToMultiByte( CP_ACP, 0, pUser, -1, NULL, 0,  NULL, NULL);
		char * pUserA = new char[ size_needed ];
		::WideCharToMultiByte( CP_ACP, 0, pUser, -1, pUserA, size_needed, NULL, NULL );

		size_needed = ::WideCharToMultiByte( CP_ACP, 0, pPath, -1, NULL, 0,  NULL, NULL);
		char * pPathA = new char[ size_needed ];
		::WideCharToMultiByte( CP_ACP, 0, pPath, -1, pPathA, size_needed, NULL, NULL );
		
		return Py_BuildValue( "(ss)", pUserA, pPathA );

		if ( pUserA )
			delete [] pUserA;
		if ( pPathA )
			delete [] pPathA;
		
	#else
		return Py_BuildValue( "(ss)", pUser, pPath );
	#endif
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getMicState()
{
	HRESULT rc;
	WORD wState;

	NOTBEFORE_INIT( "getMicState" );

	// get the microphone state here

	rc = m_pIDgnSREngineControl->GetMicState( &wState );
	RETURNIFERROR( rc, "IDgnSREngineControl::GetMicState" );

	// convert the microphone state to a string

	PyObject * pRetn;
	switch( wState )
	{
	 case DGNMIC_DISABLED:
		pRetn = Py_BuildValue( "s", "disabled" );
		break;
	 case DGNMIC_OFF:
		pRetn = Py_BuildValue( "s", "off" );
		break;
	 case DGNMIC_ON:
		pRetn = Py_BuildValue( "s", "on" );
		break;
	 case DGNMIC_SLEEPING:
		pRetn = Py_BuildValue( "s", "sleeping" );
		break;
	 default:
		assert( FALSE );
		pRetn = Py_BuildValue( "s", "error" );
	}

	return pRetn;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::setMicState( const char * pState )
{
	HRESULT rc;
	WORD wState;

	NOTBEFORE_INIT( "setMicState" );
	
	// decode the parameter, converting the string into a code
	
	if( 0 == _stricmp( pState, "on" ) )
	{
		wState = DGNMIC_ON;
	}
	else
	if( 0 == _stricmp( pState, "off" ) )
	{
		wState = DGNMIC_OFF;
	}
	else
	if( 0 == _stricmp( pState, "sleeping" ) )
	{
		wState = DGNMIC_SLEEPING;
	}
	else
	{
		reportError( errValueError, 
			"Invalid parameter (calling %s)", "setMicState" );
		return FALSE;
	}

	// change the microphone state here

	rc = m_pIDgnSREngineControl->SetMicState( wState, FALSE );
	RETURNIFERROR( rc, "IDgnSREngineControl::SetMicState" );

	return TRUE;
}

//---------------------------------------------------------------------------
// This utility subroutine takes an array of words and packs them into a
// newly allocated string.  We return the new string and the length.  The
// words are concatenated together with only their terminators separating
// them.  The string is also padded upto a multiple of four.

TCHAR * packString( PCCHAR * ppWords, DWORD * pdwSize, DWORD * pdwCount )
{
	// count the number of bytes, round up to a multiple of four

	*pdwCount = 0;
	*pdwSize = 0;
	for( int i = 0; ppWords[i]; i++ )
	{
		*pdwCount += 1;
		*pdwSize += strlen( ppWords[i] ) + 1;
	}

	#ifdef UNICODE
		*pdwSize = *pdwSize * 2;
	#endif
	*pdwSize = (*pdwSize + 3) & ~3;

	// allocate a buffer

	TCHAR * pszList = new TCHAR[*pdwSize];

	// copy the arguments into a single buffer

	DWORD offset = 0;
	for( int i = 0; ppWords[i]; i++ )
	{
		#ifdef UNICODE
			/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, ppWords[i], -1, NULL, 0 );
			CPointerChar ppWordsW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, ppWords[i], -1, ppWordsW, size_needed );*/
			CComBSTR bstrWord( ppWords[i] );
			wcscpy( pszList + offset, bstrWord );
		#else
			strcpy( pszList + offset, ppWords[i] );
		#endif
		offset += strlen( ppWords[i] ) + 1;
	}

	// pad the buffer with terminators

	while( offset < *pdwSize )
	{
		pszList[offset++] = 0;
	}

	return pszList;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::execScript(
	const char * pszScript, PCCHAR * ppWords, const char * pszComment )
{
	HRESULT rc;

	NOTBEFORE_INIT( "execScript" );
	NOTDURING_INIT( "execScript" );
	NOTDURING_PAUSED( "execScript" );

	if( pszComment == NULL )
	{
		pszComment = "execScript";
	}

	// Although this is optional, if we check the script syntax first, we
	// can report errors in a cleaner way.

	DWORD dwErrorCode;
	DWORD dwLineNumber;

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszScript, -1, NULL, 0 );
		CPointerChar pszScriptW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, pszScript, -1, pszScriptW, size_needed );*/
		CComBSTR bstrScript( pszScript );

		rc = m_pIDgnSSvcInterpreter->CheckScript(
			bstrScript, &dwErrorCode, &dwLineNumber );
	#else
		rc = m_pIDgnSSvcInterpreter->CheckScript(
			pszScript, &dwErrorCode, &dwLineNumber );
	#endif

	RETURNIFERROR( rc, "IDgnSSvcInterpreter::CheckScript" );

	if( dwErrorCode )
	{
		reportError( errSyntaxError,
			 "Error %d compiling script %s (line %d)",
			 dwErrorCode, pszComment, dwLineNumber );
		return FALSE;
	}

	// can match up ExecutionDone callbacks.
	static DWORD dwUnique = 1;
	DWORD dwClientCode = ++dwUnique;

	// We use this for if there are no list parameters

	if( ppWords == NULL )
	{
		#ifdef UNICODE
			/*size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszComment, -1, NULL, 0 );
			CPointerChar pszCommentW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, pszComment, -1, pszCommentW, size_needed );*/
			CComBSTR bstrComment( pszComment );

			rc = m_pIDgnSSvcInterpreter->ExecuteScript(
						bstrScript, &dwErrorCode, &dwLineNumber, bstrComment, dwUnique );
		#else
			rc = m_pIDgnSSvcInterpreter->ExecuteScript(
				pszScript, &dwErrorCode, &dwLineNumber, pszComment, dwUnique );
		#endif
	}

	// if there are list parameters, we use this form.  The list parameters
	// need to be passed in a single buffer separated with terminators

	else
	{
		DWORD dwCount = 0;
		DWORD dwListSize = 0;
		TCHAR * pszList = packString( ppWords, &dwListSize, &dwCount );

		#ifdef UNICODE
			/*size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszComment, -1, NULL, 0 );
			CPointerChar pszCommentW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, pszComment, -1, pszCommentW, size_needed );*/
			CComBSTR bstrComment( pszComment );

			rc = m_pIDgnSSvcInterpreter->ExecuteScriptWithListResults(
				bstrScript, dwListSize, pszList,
				&dwErrorCode, &dwLineNumber, bstrComment, dwUnique );
		#else
			rc = m_pIDgnSSvcInterpreter->ExecuteScriptWithListResults(
				pszScript, dwListSize, pszList,
				&dwErrorCode, &dwLineNumber, pszComment, dwUnique );
		#endif

		delete pszList;
	}
	RETURNIFERROR( rc, "IDgnSSvcInterpreter::ExecuteScript" );

	// Now we want to wait until the script finishes or is aborted
	//
	// if we get the message posted by ExecutionDone and ExecutionAborted
	// then we exit this windows message loop

	DWORD * pErrorInfo = (DWORD *)messageLoop( WM_EXECUTION, dwClientCode );

	if( pErrorInfo )
	{
		// ExecutionAborted allocates two DWORDs which contain the error
		// information.  We report the error and free the memory.
		reportError( errNatError,
			"Error %d executing script %s (line %d)",
			pErrorInfo[0], pszComment, pErrorInfo[1] );
		delete pErrorInfo;
		return FALSE;
	}

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::recognitionMimic( PCCHAR * ppWords )
{
	HRESULT rc;
	
	NOTBEFORE_INIT( "recognitionMimic" );
	NOTDURING_INIT( "recognitionMimic" );
	NOTDURING_PAUSED( "recognitionMimic" );

	resetPauseRecog();

	// each request to NatSpeak will have a different request number so we
	// can match up ExecutionDone callbacks.
	static DWORD dwUnique = 1;
	DWORD dwClientCode = ++dwUnique;

	SDATA sData;
	DWORD dwCount;
	sData.pData = packString( ppWords, &(sData.dwSize), &dwCount );

	rc = m_pIDgnSREngineControl->RecognitionMimic( dwCount, sData, dwClientCode );
	onINVALIDCHAR( rc, m_pIDgnSREngineControl, "Invalid word in recognitionMimic word list" );
	RETURNIFERROR( rc, "IDgnSREngineControl::RecognitionMimic" );

	delete sData.pData;

	// Now we want to wait until the recognition mimic is done

	LPUNKNOWN pIUnknown = (LPUNKNOWN)messageLoop( WM_MIMICDONE, dwClientCode );

	// if an error occurred then we will have a pIUnknown interface.  From
	// this interface we can display an error message
	
	if( pIUnknown != NULL )
	{
		reportError( errMimicFailed, pIUnknown, "recognitionMimic call failed" );
		pIUnknown->Release();
		return FALSE;
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getCursorPos()
{
	POINT pt;
	BOOL bSuccess = GetCursorPos( &pt );

	if( !bSuccess )
	{
		reportError( errNatError,
			"Windows' GetCursorPos call failed (calling %s)",
			"getCursorPos" );
		return NULL;
	}

	return Py_BuildValue( "(ii)", pt.x, pt.y );
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getScreenSize()
{
	int xSize = GetSystemMetrics( SM_CXFULLSCREEN );
	int ySize = GetSystemMetrics( SM_CYFULLSCREEN );

	return Py_BuildValue( "(ii)", xSize, ySize );
}

//---------------------------------------------------------------------------

BOOL CDragonCode::playEvents( DWORD dwCount, HOOK_EVENTMSG * pEvents )
{
	HRESULT rc;

	NOTBEFORE_INIT( "playEvents" );
	NOTDURING_INIT( "playEvents" );
	NOTDURING_PAUSED( "playEvents" );

	// each request to NatSpeak will have a different request number so we
	// can match up PlaybackDone callbacks.
	static DWORD dwUnique = 1;
	DWORD dwClientCode = ++dwUnique;

	rc = m_pIDgnSSvcOutputEvent->PlayEvents(
		dwCount, pEvents, 
		0xFFFFFFFF,   	// delay (-1 for app specific delay)
		dwClientCode ); // to identify which WM_PLAYBACK is ours
	RETURNIFERROR( rc, "IDgnSSvcOutputEvent::PlayEvents" );

	// Now we want to wait until the playback finishes or is aborted
	//
	// if we get the message posted by onPlaybackDone and onPlaybackAborted
	// then we exit this windows message loop

	BOOL bAborted = messageLoop( WM_PLAYBACK, dwClientCode );

	if( bAborted )
	{
		// the eCode will be set when we get a PlaybackAborted callback
		// instead of a PlaybackDone callback
		reportError( errNatError,
			"Error returned from playEvents (calling %s)",
			"natlink.playEvents" );
		return FALSE;
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::waitForSpeech( int nTimeout )
{
	NOTBEFORE_INIT( "waitForSpeech" );
	NOTDURING_INIT( "waitForSpeech" );
	NOTDURING_PAUSED( "waitForSpeech" );

	// this creates the dialog box and waits for it to be destroyed.  We
	// pass in the timeout as the parameter

	MY_BEGIN_ALLOW_THREADS
	
	HINSTANCE hInstance = _Module.GetModuleInstance();
	DialogBoxParam(
		hInstance, MAKEINTRESOURCE( IDD_WAITFOR ),
		NULL /* no parent */, waitDialogProc, (LPARAM) nTimeout );

	MY_END_ALLOW_THREADS

	return TRUE;
}

//---------------------------------------------------------------------------
BOOL CDragonCode::inputFromFile(
	const char * pszFileName, BOOL bRealTime,
	DWORD dwPlayList, DWORD * adwPlayList, int nUttDetect )
{
    HRESULT rc;
	assert( dwPlayList && adwPlayList || !dwPlayList && !adwPlayList );

	NOTBEFORE_INIT( "inputFromFile" );
	NOTDURING_INIT( "inputFromFile" );
	NOTDURING_PAUSED( "inputFromFile" );

	// We do not allow playback if we are already in the middle of playback.
	// This is really a limitation of NatSpeak because there can only be one
	// active file-based audio source.
	static BOOL bInFunction = FALSE;
	CInFunction cInFunction( &bInFunction );
	if( cInFunction.wasAlreadySet() )
	{
		reportError( errNatError,
			"inputFromFile can not be reentered, input is already active (calling %s)", 
			"natlink.inputFromFile" );
		return FALSE;
	}
	
	// make sure the file exists before continuing
	
	DWORD dwFileType = testFileName( pszFileName );
	if( dwFileType == INVALID_WAVEFILE )
	{
		return FALSE;
	}

	// open the audio source and start playback
	
	IDgnSRAudioFileSourcePtr pIDgnSRAudioFileSource;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(IDgnSRAudioFileSource), (void**)&pIDgnSRAudioFileSource );
	RETURNIFERROR( rc, "ISRCentral::QueryInterface(IDgnSRAudioFileSource)" );

	// we perform utterance detection if this is a WAV file; we also have to
	// pass in the realtime flag when we open the file
	DWORD dwFlags = 0;
	if( nUttDetect == 1 ||
		( nUttDetect != 0 && dwFileType == DGNUTTTYP_MSWAV ) )
	{
		dwFlags |= DGNUTTFLG_DETECTUTT;
	}
	if( bRealTime )
	{
		dwFlags |= DGNUTTFLG_REALTIME;
	}

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszFileName, -1, NULL, 0 );
		CPointerChar pszFileNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, pszFileName, -1, pszFileNameW, size_needed );*/
		CComBSTR bstrFileName( pszFileName );

		rc = pIDgnSRAudioFileSource->FileNameSet( dwFlags, bstrFileName );
	#else
		rc = pIDgnSRAudioFileSource->FileNameSet( dwFlags, pszFileName );
	#endif
	
	RETURNIFERROR( rc, "IDgnSRAudioFileSource::FileNameSet" );

	if( dwPlayList )
	{
    	rc = pIDgnSRAudioFileSource->PlayListSet( adwPlayList, dwPlayList * 2 );
		RETURNIFERROR( rc, "IDgnSRAudioFileSource::PlayListSet" );
	}

    rc = pIDgnSRAudioFileSource->EnableSet( TRUE );
	RETURNIFERROR( rc, "IDgnSRAudioFileSource::EnableSet(TRUE)" );

	// Now we want to wait until the playback finishes

	messageLoop( WM_ATTRIBCHANGED, DGNSRAC_PLAYBACKDONE );

	// close the audio source

	rc = pIDgnSRAudioFileSource->EnableSet( FALSE );
	RETURNIFERROR( rc, "IDgnSRAudioFileSource::EnableSet(FALSE)" );
	
    rc = pIDgnSRAudioFileSource->FileClose();
	RETURNIFERROR( rc, "IDgnSRAudioFileSource::FileClose" );

	return TRUE;
}
//---------------------------------------------------------------------------

BOOL CDragonCode::setTimerCallback( PyObject * pCallback, int nMilliseconds )
{
	NOTBEFORE_INIT( "setTimerCallback" );

	// first we clean up from the previous call (this makes sure that we
	// delete the timer)
	if( m_nTimer )
	{
		KillTimer( m_hMsgWnd, m_nTimer );
		m_nTimer = 0;
	}
	Py_XDECREF( m_pTimerCallback );
	m_pTimerCallback = NULL;

	// now we install a new callback and timer if desired
	if( pCallback != Py_None )
	{
		Py_XINCREF( pCallback );
		m_pTimerCallback = pCallback;
		m_nTimer = SetTimer( m_hMsgWnd, 2, nMilliseconds, NULL );
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------
PyObject * CDragonCode::getTrainingMode()
{
	HRESULT rc;

	NOTBEFORE_INIT( "getTrainingMode" );

	DWORD dwMode;
	DWORD dwSpeechLength;
	DWORD dwNumberCalls;
	rc = m_pIDgnSRTraining->TrainingModeGet(
		&dwMode,			// current training mode
		&dwSpeechLength,	// milliseconds of speech trained so far
		&dwNumberCalls );	// total number of calls to correction
	RETURNIFERROR( rc, "IDgnSRTraining::TrainingModeGet" );

	PyObject * pRetn;
	switch( dwMode )
	{
	 case DGNTRNMODE_NORMAL:
	 case DGNTRNMODE_SINGLESET:		// this mode is currently unused
		Py_INCREF( Py_None );
		pRetn = Py_None;
		break;
	 case DGNTRNMODE_CALIBRATE:
		pRetn = Py_BuildValue( "(si)", "calibrate", dwSpeechLength );
		break;
	 case DGNTRNMODE_CROSSWORD:
		pRetn = Py_BuildValue( "(si)", "longtrain", dwSpeechLength );
		break;
	 case DGNTRNMODE_BATCHWORD:
		pRetn = Py_BuildValue( "(si)", "batchadapt", dwSpeechLength );
		break;
	case DGNTRNMODE_SHORTBATCH:
		pRetn = Py_BuildValue( "(si)", "shorttrain", dwSpeechLength );
		break;
	 default:
		assert( FALSE );
		pRetn = Py_BuildValue( "(si)", "error", dwSpeechLength );
	}

	return pRetn;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::startTraining( char * pMode )
{
	HRESULT rc;

	NOTBEFORE_INIT( "startTraining" );

	// decode the parameter, converting the string into a code

	DWORD dwMode;
	if( 0 == _stricmp( pMode, "calibrate" ) )
	{
		dwMode = DGNTRNMODE_CALIBRATE;
	}
	else
	if( 0 == _stricmp( pMode, "shorttrain" ) )
	{
		dwMode = DGNTRNMODE_SHORTBATCH;
	}
	else
	if( 0 == _stricmp( pMode, "longtrain" ) )
	{
		dwMode = DGNTRNMODE_CROSSWORD;
	}
	else
	if( 0 == _stricmp( pMode, "batchadapt" ) )
	{
		dwMode = DGNTRNMODE_BATCHWORD;
	}
	else
	{
		reportError( errValueError, 
			"Invalid parameter (calling %s)", "startTraining" );
		return FALSE;
	}

	// set the training mode and handle the expected errors

	rc = m_pIDgnSRTraining->TrainingModeSet( dwMode );
	onINVALIDMODE( rc, "Training mode %s is not valid at this time for the current user", pMode );
	onALREADYACTIVE( rc, "A special training mode is already active" );
	RETURNIFERROR( rc, "IDgnSRTraining::TrainingModeSet" );

	m_bSetTraining = TRUE;
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::finishTraining( BOOL bNoCancel )
{
	HRESULT rc;

	NOTBEFORE_INIT( "finishTraining" );

	m_bSetTraining = FALSE;

	if( bNoCancel )
	{
		rc = m_pIDgnSRTraining->TrainingPerform();
	}
	else
	{
		rc = m_pIDgnSRTraining->TrainingCancel();
	}

	if( rc == DGNERR_MODENOTACTIVE )
	{
		reportError( errWrongState,
			"A special training mode is not active (calling %s)",
			"finishTraining" );
		return FALSE;
	}
	RETURNIFERROR( rc, "IDgnSRTraining::TrainingPerform" );
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::createUser(
	char * pszUserName, char * pszBaseModel, char * pszBaseTopic )
{
	HRESULT rc;

	// The normal SAPI way of creating a user is to call ISRSpeaker::New.
	// This method does not allow for a model or topic name, however.  If
	// the Python client has not specified a model name then we use the
	// standard SAPI function call.  This causes NatSpeak to create a
	// speaker with the default model and topic.

	if( pszBaseModel == NULL || *pszBaseModel == 0 )
	{
		ISRSpeakerPtr pISRSpeaker;
		rc = m_pISRCentral->QueryInterface(
			__uuidof(ISRSpeaker), (void**)&pISRSpeaker );
		RETURNIFERROR( rc, "ISRCentral::QueryInterface(ISRSpeaker)" );

		#ifdef UNICODE
			/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszUserName, -1, NULL, 0 );
			CPointerChar pszUserNameW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, pszUserName, -1, pszUserNameW, size_needed );*/
			CComBSTR bstrUserName( pszUserName );
			rc = pISRSpeaker->New( bstrUserName );
		#else
			rc = pISRSpeaker->New( pszUserName );
		#endif

		onINVALIDARG( rc, "The user name '%s' is invalid", pszUserName );
		onSPEAKEREXISTS( rc, "A user names '%s' already exists", pszUserName );
		RETURNIFERROR( rc, "ISRSpeaker::New" );
	}

	// If a model name has been specified then we use the Dragon varient
	// which takes the name of the model.

	else
	{
		IDgnSRSpeakerPtr pIDgnSRSpeaker;
		rc = m_pISRCentral->QueryInterface(
			__uuidof(IDgnSRSpeaker), (void**)&pIDgnSRSpeaker );
		RETURNIFERROR( rc, "ISRCentral::QueryInterface(IDgnSRSpeaker)" );

		#ifdef UNICODE
			/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszUserName, -1, NULL, 0 );
			CPointerChar pszUserNameW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, pszUserName, -1, pszUserNameW, size_needed );

			size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszBaseModel, -1, NULL, 0 );
			CPointerChar pszBaseModelW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, pszBaseModel, -1, pszBaseModelW, size_needed );*/
			CComBSTR bstrUserName( pszUserName );
			CComBSTR bstrBaseModel( pszBaseModel );

			rc = pIDgnSRSpeaker->New( bstrUserName, bstrBaseModel );
		#else
			rc = pIDgnSRSpeaker->New( pszUserName, pszBaseModel );
		#endif

		onINVALIDARG( rc, "The user name '%s' is invalid", pszUserName );
		onSPEAKEREXISTS( rc, "A user names '%s' already exists", pszUserName );
		onVALUEOUTOFRANGE( rc, "The base model '%s' does not exist", pszBaseModel );
		RETURNIFERROR( rc, "IDgnSRSpeaker::New" );
	}

	// Now if a topic has been specified, we create that topic.  Otherwise
	// we do not explicitly create a topic and count on the fact that
	// NatSpeak will create a default topic when the user is opened.

	if( pszBaseTopic != NULL && *pszBaseTopic != 0 )
	{
		IDgnSRTopic2Ptr pIDgnSRTopic2;
		rc = m_pISRCentral->QueryInterface(
			__uuidof(IDgnSRTopic2), (void**)&pIDgnSRTopic2 );
		RETURNIFERROR( rc, "ISRCentral::QueryInterface(IDgnSRTopic2)" );

		// This call lets you specify the base topic to use and the topic
		// name to use.  We make the topic name the same as the base topic.
		// This matches the behavior of the NatSpeak new user wizard

		#ifdef UNICODE
			/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszUserName, -1, NULL, 0 );
			CPointerChar pszUserNameW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, pszUserName, -1, pszUserNameW, size_needed );

			size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszBaseTopic, -1, NULL, 0 );
			CPointerChar pszBaseTopicW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, pszBaseTopic, -1, pszBaseTopicW, size_needed );*/
			CComBSTR bstrUserName( pszUserName );
			CComBSTR bstrBaseTopic( pszBaseTopic );
			rc = pIDgnSRTopic2->New( bstrUserName, bstrBaseTopic, bstrBaseTopic );
		#else
			rc = pIDgnSRTopic2->New( pszUserName, pszBaseTopic, pszBaseTopic );
		#endif
		
		onVALUEOUTOFRANGE( rc, "The base topic '%s' does not exist", pszBaseTopic );
		RETURNIFERROR( rc, "IDgnSRTopic2::New" );
	}
	
	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::openUser( char * pszUserName )
{
	HRESULT rc;

	NOTBEFORE_INIT( "openUser" );

	ISRSpeakerPtr pISRSpeaker;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(ISRSpeaker), (void**)&pISRSpeaker );
	RETURNIFERROR( rc, "ISRCentral::QueryInterface(ISRSpeaker)" );

	// make sure the user exists

	TCHAR * pBuffer;
	DWORD dwSize;
	rc = pISRSpeaker->Enum( &pBuffer, &dwSize );
	
	RETURNIFERROR( rc, "ISRSpeaker::Enum" );

	PyObject * pList = PyList_New( 0 );

	BOOL bFound = FALSE;
	TCHAR * pName = pBuffer;
	while( *pName && !bFound )
	{
		#ifdef UNICODE
			CComBSTR bstrUserName( pszUserName );
			if( 0 == _tcscmp( pName, bstrUserName ) )
		#else
			if( 0 == _tcscmp( pName, pszUserName ) )
		#endif
		{
			bFound = TRUE;
			break;
		}
		pName += _tcslen( pName ) + 1;
	}

	CoTaskMemFree( pBuffer );

	if( !bFound )
	{
		reportError( errUnknownName,
			"The user named '%s' does not exist", pszUserName );
		return FALSE;
	}

	#ifdef UNICODE
		CComBSTR bstrUserName( pszUserName );
		rc = pISRSpeaker->Select( bstrUserName, FALSE /*bLock*/ );
	#else
		rc = pISRSpeaker->Select( pszUserName, FALSE /*bLock*/ );
	#endif

	onINVALIDARG( rc, "The user name '%s' is invalid", pszUserName );
	RETURNIFERROR( rc, "ISRSpeaker::Select" );

	return TRUE;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::saveUser()
{
	HRESULT rc;

	NOTBEFORE_INIT( "saveUser" );

	rc = m_pIDgnSREngineControl->SaveSpeaker( FALSE /*bBackup*/ );
	RETURNIFERROR( rc, "IDgnSREngineControl::SaveSpeaker" );
	
	return TRUE;
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getUserTraining()
{
	HRESULT rc;

	NOTBEFORE_INIT( "getUserTraining" );

	BOOL bCalibrate;
	DWORD dwBatchCount;
	DWORD dwSpeechLength;
	rc = m_pIDgnSRTraining->TotalCountGet(
		&bCalibrate,		// has calibration been done
		&dwBatchCount,		// count of calls to batch training or adapt
		&dwSpeechLength );	// total length of all training utterances
	RETURNIFERROR( rc, "IDgnSRTraining::TotalCountGet" );

	if( !bCalibrate )
	{
		// no training has been done
		Py_INCREF( Py_None );
		return Py_None;
	}
	else
	if( dwBatchCount == 0 )
	{
		// only calibration has been done
		return Py_BuildValue( "s", "calibrate" );
	}
	else
	{
		// at least one pass of batch training has been done
		return Py_BuildValue( "s", "trained" );
	}
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getClipboard()
{
	if( !OpenClipboard( NULL ) )
	{
		reportError( errNatError, "Clipboard is not available" );
		return NULL;
	}

	HANDLE hClipData = GetClipboardData( CF_TEXT );
	if( !hClipData )
	{
		CloseClipboard();
		return Py_BuildValue( "s", "" );
	}

	void * pClipData = GlobalLock( hClipData );
	if( !pClipData )
	{
		reportError( errNatError, "Out of memory reading clipboard" );
		CloseClipboard();
		return NULL;
	}

	PyObject * pRetn = Py_BuildValue( "s", pClipData );

	CloseClipboard();
	return pRetn;
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getAllUsers()
{
	HRESULT rc;

	NOTBEFORE_INIT( "getAllUsers" );

	ISRSpeakerPtr pISRSpeaker;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(ISRSpeaker), (void**)&pISRSpeaker );
	RETURNIFERROR( rc, "ISRCentral::QueryInterface(ISRSpeaker)" );

	TCHAR * pBuffer;
	DWORD dwSize;
	rc = pISRSpeaker->Enum( &pBuffer, &dwSize );
	RETURNIFERROR( rc, "ISRSpeaker::Enum" );

	PyObject * pList = PyList_New( 0 );
	
	TCHAR * pName = pBuffer;
	while( *pName )
	{
		#ifdef UNICODE
			int size_needed = ::WideCharToMultiByte( CP_ACP, 0, pName, -1, NULL, 0,  NULL, NULL);
			char * pNameA = new char[ size_needed ];
			::WideCharToMultiByte( CP_ACP, 0, pName, -1, pNameA, size_needed, NULL, NULL );
			PyObject * pyName = Py_BuildValue( "s", pNameA );
			delete [] pNameA;
		#else
			PyObject * pyName = Py_BuildValue( "s", pName );
		#endif

		PyList_Append( pList, pyName );
		Py_DECREF( pyName );
		pName += _tcslen( pName ) + 1;
	}
	
	CoTaskMemFree( pBuffer );

	return pList;
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getWordInfo( char * wordName, int flags )
{
	HRESULT rc;

	NOTBEFORE_INIT( "getWordInfo" );

	if( flags & ~0x07 )
	{
		reportError( errValueError, "Unknown flags passed to getWordInfo" );
		return NULL;
	}

	IDgnSRLexiconPtr pDgnSRLexicon;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(IDgnSRLexicon), (void**)&pDgnSRLexicon);
	RETURNIFERROR( rc, "QueryInterface(IDgnSRLexicon)" );

	ILexPronouncePtr pLexPron;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(ILexPronounce), (void**)&pLexPron );
	RETURNIFERROR( rc, "QueryInterface(ILexPronounce)" );

	//	1 = consider inactive words (backup dictionary)
	//	2 = consider active non-dictation words
	//	4 = case insensitive match

	DWORD dwFlags = 0;
	if( (flags & 0x01) == 0 )
	{
		dwFlags |= DGNWORDTESTFLAG_ACTIVEVOCONLY;
	}
	if( (flags & 0x02) == 0 )
	{
		dwFlags |= DGNWORDTESTFLAG_DICTONLY;
	}
	if( (flags & 0x04) == 0 )
	{
		dwFlags |= DGNWORDTESTFLAG_CASESENSITIVE;
	}
	
	BOOL bExists;

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, wordName, -1, NULL, 0 );
		CPointerChar wordNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, wordName, -1, wordNameW, size_needed );*/
		CComBSTR bstrWordName( wordName );
		rc = pDgnSRLexicon->WordTest( dwFlags, bstrWordName, &bExists );
	#else
		rc = pDgnSRLexicon->WordTest( dwFlags, wordName, &bExists );
	#endif

	RETURNIFERROR( rc, "IDgnSRLexicon::WordTest" )

	if( rc == S_FALSE )
	{
		// we return S_FALSE when the word is invalid
		reportError( errInvalidWord, "The word '%s' is invalid (NatSpeak does not allow that spelling)", wordName );
		return NULL;
	}

	if( !bExists )
	{
		// if the word does not exist, return None
		Py_INCREF( Py_None );
		return Py_None;
	}

	// If we got here then the word exists and is valid.  Look up the engine
	// specific information (formatting flags).

	TCHAR pronBuf[1];

	DgnEngineInfo info;
	info.dwFlags = 0;
	info.dwWordNum = 0;

	DWORD dwPronSize;
	DWORD dwInfoSize;

	#ifdef UNICODE
		rc = pLexPron->Get(
			CHARSET_ENGINEPHONETIC, bstrWordName, 0,
			&pronBuf[0], 0, &dwPronSize, 0,
			(BYTE*)&info, sizeof(DgnEngineInfo), &dwInfoSize );
	#else
		rc = pLexPron->Get(
			CHARSET_ENGINEPHONETIC, wordName, 0,
			&pronBuf[0], 0, &dwPronSize, 0,
			(BYTE*)&info, sizeof(DgnEngineInfo), &dwInfoSize );
	#endif

	RETURNIFERROR( rc, "ILexPronounce::Get" )

	return Py_BuildValue( "i", info.dwFlags );
}

//---------------------------------------------------------------------------

BOOL CDragonCode::deleteWord( char * wordName )
{
	HRESULT rc;

	NOTBEFORE_INIT( "deleteWord" );

	IDgnLexWordPtr pDgnLexWord;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(IDgnLexWord), (void**)&pDgnLexWord);
	RETURNIFERROR( rc, "QueryInterface(IDgnLexWord)" );

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, wordName, -1, NULL, 0 );
		CPointerChar wordNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, wordName, -1, wordNameW, size_needed );*/
		CComBSTR bstrWordName( wordName );
		rc = pDgnLexWord->Remove( bstrWordName );
	#else
		rc = pDgnLexWord->Remove( wordName );
	#endif

	onINVALIDTEXTCHAR( rc, "The word '%s' is invalid (NatSpeak does not allow that spelling)", wordName );

	if( rc == S_FALSE )
	{
		reportError( errUnknownName, "The word '%s' is not in the active vocabulary", wordName );
		return FALSE;
	}

	return TRUE;
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::addWord(
	char * wordName, DWORD wordInfo, PCCHAR * ppProns )
{
	HRESULT rc;

	NOTBEFORE_INIT( "addWord" );

	ILexPronouncePtr pLexPron;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(ILexPronounce), (void**)&pLexPron );
	RETURNIFERROR( rc, "QueryInterface(ILexPronounce)" );

	// The word number is non-zero when the wordInfo is non-zero and zero
	// otherwise.
	DgnEngineInfo info;
	info.dwFlags = wordInfo;
	info.dwWordNum = wordInfo ? 1 : 0;

	if( ppProns == NULL )
	{
		#ifdef UNICODE
			/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, wordName, -1, NULL, 0 );
			CPointerChar wordNameW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, wordName, -1, wordNameW, size_needed );*/
			CComBSTR bstrWordName( wordName );
			rc = pLexPron->Add(
				CHARSET_ENGINEPHONETIC, bstrWordName, L"",
				VPS_UNKNOWN, (BYTE*)&info, sizeof(DgnEngineInfo) );
		#else
			rc = pLexPron->Add(
				CHARSET_ENGINEPHONETIC, wordName, "",
				VPS_UNKNOWN, (BYTE*)&info, sizeof(DgnEngineInfo) );
		#endif

		if( rc == LEXERR_ALREADYINLEX )
		{
			// word was not added because it already exists
			return Py_BuildValue( "i", 0 );
		}
		onINVALIDTEXTCHAR( rc, "The word '%s' is invalid (NatSpeak does not allow that spelling)", wordName );
		RETURNIFERROR( rc, "ILexPronounce::Add" )
	}
	else
	{
		for( int i = 0; ppProns[i] != NULL; i++ )
		{
			#ifdef UNICODE
				/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, wordName, -1, NULL, 0 );
				CPointerChar wordNameW = new TCHAR[ size_needed ];
				::MultiByteToWideChar( CP_ACP, 0, wordName, -1, wordNameW, size_needed );

				size_needed = ::MultiByteToWideChar( CP_ACP, 0, ppProns[i], -1, NULL, 0 );
				CPointerChar ppPronsW = new TCHAR[ size_needed ];
				::MultiByteToWideChar( CP_ACP, 0, ppProns[i], -1, ppPronsW, size_needed );*/
				CComBSTR bstrWordName( wordName );
				CComBSTR bstrPron( ppProns[i] );
				rc = pLexPron->Add(
					CHARSET_ENGINEPHONETIC, bstrWordName, bstrPron,
					VPS_UNKNOWN, (BYTE*)&info, sizeof(DgnEngineInfo) );
			#else
				rc = pLexPron->Add(
					CHARSET_ENGINEPHONETIC, wordName, ppProns[i],
					VPS_UNKNOWN, (BYTE*)&info, sizeof(DgnEngineInfo) );
			#endif
			onINVALIDTEXTCHAR( rc, "The word '%s' is invalid (NatSpeak does not allow that spelling)", wordName );
			RETURNIFERROR( rc, "ILexPronounce::Add" )
		}
	}
	
	// word was successfully added
	return Py_BuildValue( "i", 1 );
}

//---------------------------------------------------------------------------

BOOL CDragonCode::setWordInfo( char * wordName, DWORD wordInfo )
{
	HRESULT rc;

	NOTBEFORE_INIT( "setWordInfo" );
	
	IDgnSRLexiconPtr pDgnSRLexicon;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(IDgnSRLexicon), (void**)&pDgnSRLexicon);
	RETURNIFERROR( rc, "QueryInterface(IDgnSRLexicon)" );

	ILexPronouncePtr pLexPron;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(ILexPronounce), (void**)&pLexPron );
	RETURNIFERROR( rc, "QueryInterface(ILexPronounce)" );

	// Test for the word first.  Only consider the active dictionary.

	DWORD dwFlags =
		DGNWORDTESTFLAG_ACTIVEVOCONLY |
		DGNWORDTESTFLAG_DICTONLY |
		DGNWORDTESTFLAG_CASESENSITIVE;
	
	BOOL bExists;

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, wordName, -1, NULL, 0 );
		CPointerChar wordNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, wordName, -1, wordNameW, size_needed );*/
		CComBSTR bstrWordName( wordName );
		rc = pDgnSRLexicon->WordTest( dwFlags, bstrWordName, &bExists );
	#else
		rc = pDgnSRLexicon->WordTest( dwFlags, wordName, &bExists );
	#endif

	RETURNIFERROR( rc, "IDgnSRLexicon::WordTest" )

	if( rc == S_FALSE )
	{
		reportError( errInvalidWord, "The word '%s' is invalid (NatSpeak does not allow that spelling)", wordName );
		return NULL;
	}

	if( !bExists )
	{
		reportError( errUnknownName, "The word '%s' is not in the active vocabulary", wordName );
		return FALSE;
	}

	// The way Draqgon NaturallySpeaking is coded, the wordInfo data will
	// not be changed for an existing word unless you add the word back to
	// the system with a pronunciation.  Therefore, we use a trick.  We
	// first get all the word information then we write back that same
	// information except that we include the new wordInfo.

	DWORD dwInfoSize;
	DWORD dwPronSize;
	TCHAR pronBuf[64];
	DgnEngineInfo info;
	VOICEPARTOFSPEECH partSpeech;

	#ifdef UNICODE
		rc = pLexPron->Get(
			CHARSET_ENGINEPHONETIC, bstrWordName, 0,
			&pronBuf[0], 64, &dwPronSize, &partSpeech,
			(BYTE*)&info, sizeof(DgnEngineInfo), &dwInfoSize );
	#else
		rc = pLexPron->Get(
			CHARSET_ENGINEPHONETIC, wordName, 0,
			&pronBuf[0], 64, &dwPronSize, &partSpeech,
			(BYTE*)&info, sizeof(DgnEngineInfo), &dwInfoSize );
	#endif

	RETURNIFERROR( rc, "ILexPronounce::Get" )

	info.dwFlags = wordInfo;
	info.dwWordNum = wordInfo ? 1 : 0;

	#ifdef UNICODE
		rc = pLexPron->Add(
			CHARSET_ENGINEPHONETIC, bstrWordName, &pronBuf[0],
			partSpeech, (BYTE*)&info, sizeof(DgnEngineInfo) );
	#else
		rc = pLexPron->Add(
			CHARSET_ENGINEPHONETIC, wordName, &pronBuf[0],
			partSpeech, (BYTE*)&info, sizeof(DgnEngineInfo) );
	#endif

	RETURNIFERROR( rc, "ILexPronounce::Add" )

	return TRUE;
}

//---------------------------------------------------------------------------

PyObject * CDragonCode::getWordProns( char * wordName )
{
	HRESULT rc;
	
	IDgnSRLexiconPtr pDgnSRLexicon;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(IDgnSRLexicon), (void**)&pDgnSRLexicon);
	RETURNIFERROR( rc, "QueryInterface(IDgnSRLexicon)" );

	ILexPronouncePtr pLexPron;
	rc = m_pISRCentral->QueryInterface(
		__uuidof(ILexPronounce), (void**)&pLexPron );
	RETURNIFERROR( rc, "QueryInterface(ILexPronounce)" );

	// Test for the word first.  Only consider the active dictionary.

	DWORD dwFlags =
		DGNWORDTESTFLAG_ACTIVEVOCONLY |
		DGNWORDTESTFLAG_DICTONLY |
		DGNWORDTESTFLAG_CASESENSITIVE;
	
	BOOL bExists;

	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, wordName, -1, NULL, 0 );
		CPointerChar wordNameW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, wordName, -1, wordNameW, size_needed );*/
		CComBSTR bstrWordName( wordName );
		rc = pDgnSRLexicon->WordTest( dwFlags, bstrWordName, &bExists );
	#else
		rc = pDgnSRLexicon->WordTest( dwFlags, wordName, &bExists );
	#endif

	RETURNIFERROR( rc, "IDgnSRLexicon::WordTest" )

	if( rc == S_FALSE )
	{
		reportError( errInvalidWord, "The word '%s' is invalid (NatSpeak does not allow that spelling)", wordName );
		return NULL;
	}

	if( !bExists )
	{
			Py_INCREF( Py_None );
			return Py_None;
	}

	// There is no SAPI call which gets all the word prons, we have to
	// iterate over all the possible pronunciations.
	
	PyObject * pList = PyList_New( 0 );

	for( WORD wSense = 0; wSense < 100; wSense++ )
	{
		DWORD dwInfoSize;
		DWORD dwPronSize;
		TCHAR pronBuf[64];
		DgnEngineInfo info;
		VOICEPARTOFSPEECH partSpeech;
		
		#ifdef UNICODE
			rc = pLexPron->Get(
				CHARSET_ENGINEPHONETIC, bstrWordName, wSense,
				&pronBuf[0], 64, &dwPronSize, &partSpeech,
				(BYTE*)&info, sizeof(DgnEngineInfo), &dwInfoSize );
		#else
			rc = pLexPron->Get(
				CHARSET_ENGINEPHONETIC, wordName, wSense,
				&pronBuf[0], 64, &dwPronSize, &partSpeech,
				(BYTE*)&info, sizeof(DgnEngineInfo), &dwInfoSize );
		#endif

		onINVALIDTEXTCHAR( rc, "The word '%s' is invalid (NatSpeak does not allow that spelling)", wordName );
		if( rc == LEXERR_INVALIDSENSE )
		{
			// no more pronunciations
			break;
		}
		RETURNIFERROR( rc, "ILexPronounce::Get" )

		// add the word to the list
		#ifdef UNICODE
			int size_needed = ::WideCharToMultiByte( CP_ACP, 0, pronBuf, -1, NULL, 0,  NULL, NULL);
			char * pronBufA = new char[ size_needed ];
			::WideCharToMultiByte( CP_ACP, 0, pronBuf, -1, pronBufA, size_needed, NULL, NULL );

			PyObject * pText = Py_BuildValue( "s", pronBufA );

			if ( pronBufA )
				delete [] pronBufA;
		#else
			PyObject * pText = Py_BuildValue( "s", pronBuf );
		#endif

		PyList_Append( pList, pText );
		Py_XDECREF( pText );
	}

	return pList;
}

//---------------------------------------------------------------------------

BOOL CDragonCode::setTrayIcon(
	char * iconName, char * toolTip, PyObject * pCallback )
{
	HICON hIcon = NULL;
	HINSTANCE hInstance = _Module.GetModuleInstance();

	Py_XDECREF( m_pTrayIconCallback );
	m_pTrayIconCallback = NULL;
	
	// It is always safe to delete the icon. This could 
	// be called when we shutdown.
	if( iconName == NULL || *iconName == '\0' )
	{
		if( m_bHasTrayIcon )
		{
			NOTIFYICONDATA iconData;
			memset( &iconData, 0, sizeof(NOTIFYICONDATA) );
			iconData.cbSize = sizeof(NOTIFYICONDATA);
			iconData.hWnd = m_hMsgWnd;
			Shell_NotifyIcon( NIM_DELETE, &iconData );
			m_bHasTrayIcon = FALSE;
		}
		return TRUE;
	}
	
	NOTBEFORE_INIT( "setTrayIcon" );
	
	// Figure out what icon to use

	if( 0 == _stricmp(iconName,"right") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_RIGHT));
	}
	else if( 0 == _stricmp(iconName,"right2") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_RIGHT2));
	}
	else if( 0 == _stricmp(iconName,"down") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_DOWN));
	}
	else if( 0 == _stricmp(iconName,"down2") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_DOWN2));
	}
	else if( 0 == _stricmp(iconName,"left") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_LEFT));
	}
	else if( 0 == _stricmp(iconName,"left2") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_LEFT2));
	}
	else if( 0 == _stricmp(iconName,"up") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_UP));
	}
	else if( 0 == _stricmp(iconName,"up2") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_UP2));
	}
	else if( 0 == _stricmp(iconName,"nodir") )
	{
		hIcon = LoadIcon(hInstance,MAKEINTRESOURCE(IDI_NODIR));
	}
	else
	{
		#ifdef UNICODE
			/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, iconName, -1, NULL, 0 );
			CPointerChar iconNameW = new TCHAR[ size_needed ];
			::MultiByteToWideChar( CP_ACP, 0, iconName, -1, iconNameW, size_needed );*/
			CComBSTR bstrIconName( iconName );
			hIcon = (HICON) LoadImage(
				hInstance, bstrIconName, IMAGE_ICON, 0, 0,
				LR_DEFAULTSIZE | LR_DEFAULTCOLOR | LR_LOADFROMFILE );
		#else
			hIcon = (HICON) LoadImage(
				hInstance, iconName, IMAGE_ICON, 0, 0,
				LR_DEFAULTSIZE | LR_DEFAULTCOLOR | LR_LOADFROMFILE );
		#endif
	}

	if( hIcon == NULL )
	{
		reportError( errValueError,
			"Icon file %s could not be loaded", iconName );
		return FALSE;
	}
	
	// Here we do the actual work

	DWORD action = m_bHasTrayIcon ? NIM_MODIFY : NIM_ADD;

	NOTIFYICONDATA iconData;
	iconData.cbSize = sizeof(NOTIFYICONDATA);
	iconData.hWnd = m_hMsgWnd;
	iconData.uID = 0;
	iconData.uFlags = NIF_TIP | NIF_ICON | NIF_MESSAGE;
	iconData.uCallbackMessage = WM_TRAYICON;
	iconData.hIcon = hIcon;
	#ifdef UNICODE
		/*int size_needed = ::MultiByteToWideChar( CP_ACP, 0, toolTip, -1, NULL, 0 );
		CPointerChar toolTipW = new TCHAR[ size_needed ];
		::MultiByteToWideChar( CP_ACP, 0, toolTip, -1, toolTipW, size_needed );*/
		CComBSTR bstrToolTip( toolTip );
		wcsncpy_s( iconData.szTip, bstrToolTip, sizeof(iconData.szTip) );
	#else
		strncpy( iconData.szTip, toolTip, sizeof(iconData.szTip) );
	#endif

	BOOL bSuccess = Shell_NotifyIcon( action, &iconData );
	if( !bSuccess )
	{
		// Not really a COM error
		reportComError(
			GetLastError(), "Shell_NotifyIcon", "DragCode.cpp", __LINE__ );
		return FALSE;
	}
	m_bHasTrayIcon = TRUE;


	if( pCallback != Py_None )
	{
		Py_XINCREF( pCallback );
		m_pTrayIconCallback = pCallback;
	}
	
	return TRUE;
}

void CDragonCode::logCookie( const char * pText, QWORD qCookie )
{
	DWORD *pCookie = (DWORD*)&qCookie;
	char buffer[200];
	sprintf(buffer, "... %s %.4x %.4x\n",
			pText, pCookie[0], pCookie[1] );
	logMessage(buffer);
}
