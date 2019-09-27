/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 appsupp.cpp
	This module implements the COM interface which Dragon NaturallySpeaking
	calls when it connects with a compatibility module.  This implementation
	is designed to be a global client and not a app-specific client.  That
	decision simplifies the design somewhat.
*/

#include "../StdAfx.h"
#include "../Resource.h"
#include "../DragonCode.h"
#include "appsupp.h"

// from PythWrap.cpp
CDragonCode * initModule();

/////////////////////////////////////////////////////////////////////////////
// CDgnAppSupport

//---------------------------------------------------------------------------

CDgnAppSupport::CDgnAppSupport()
{
	m_pNatLinkMain = NULL;
	m_pDragCode = NULL;
}

//---------------------------------------------------------------------------

CDgnAppSupport::~CDgnAppSupport()
{
}

//---------------------------------------------------------------------------
// Called by NatSpeak once when the compatibility module is first loaded.
// This will never be called more than once in normal use.  (Although if one
// compatibility module calls another as is occassionally the case it could
// be called more than once.  Needless to say that does not apply for this
// project.)
//
// NatSpeak passes in a site object which saves us the trouble of finding
// one ourselves.  NatSpeak will be running.

STDMETHODIMP CDgnAppSupport::Register( IServiceProvider * pIDgnSite )
{
	BOOL bSuccess;

	// load and initialize the Python system
	Py_Initialize();

	// load the natlink module into Python and return a pointer to the
	// shared CDragonCode object
	m_pDragCode = initModule();
	m_pDragCode->setAppClass( this );

	// simulate calling natlink.natConnect() except share the site object
	bSuccess = m_pDragCode->natConnect( pIDgnSite );

	if( !bSuccess )
	{
		OutputDebugString(
			TEXT( "NatLink: failed to initialize NatSpeak interfaces") ); // RW TEXT macro added
		m_pDragCode->displayText(
			"Failed to initialize NatSpeak interfaces\r\n", TRUE );
		return S_OK;
	}
	
	// now load the Python code which does most of the work
	m_pDragCode->setDuringInit( TRUE );
	m_pNatLinkMain = PyImport_ImportModule( "natlinkmain" );
	
	// until natlink has been loaded, we restrict some of the function
	// callbacks into DragCode to avoid deadlock.
	m_pDragCode->setDuringInit( FALSE );

	if( m_pNatLinkMain == NULL )
	{
		OutputDebugString(
			TEXT( "NatLink: an exception occurred loading 'natlinkmain' module" ) ); // RW TEXT macro added
		m_pDragCode->displayText(
			"An exception occurred loading 'natlinkmain' module\r\n", TRUE );
		m_pDragCode->displayText(
			"No more error information is available\r\n", TRUE );
		return S_OK;
	}

	return S_OK;
}

//---------------------------------------------------------------------------
// Called by NatSpeak during shutdown as the last call into this
// compatibility module.  There is always one UnRegister call for every
// Register call (all one of them).

STDMETHODIMP CDgnAppSupport::UnRegister()
{
	// simulate calling natlink.natDisconnect()
	m_pDragCode->natDisconnect();

	// free our reference to the Python modules
	Py_XDECREF( m_pNatLinkMain );

	return S_OK;
}

//---------------------------------------------------------------------------
// For a non-global client, this call is made evrey time a new instance of
// the target application is started.  The process ID of the target
// application is passed in along with the target application module name
// and a string which tells us where to find NatSpeak information specific
// to that module in the registry.
//
// For global clients (like us), this is called once after Register and we
// can ignore the call.

#ifdef UNICODE
	STDMETHODIMP CDgnAppSupport::AddProcess(
		DWORD dwProcessID, 
		const wchar_t * pszModuleName, 
		const wchar_t * pszRegistryKey, 
		DWORD lcid )
	{
		return S_OK;
	}
#else
	STDMETHODIMP CDgnAppSupport::AddProcess(
		DWORD dwProcessID, 
		const char * pszModuleName, 
		const char * pszRegistryKey, 
		DWORD lcid )
	{
		return S_OK;
	}
#endif
//---------------------------------------------------------------------------
// For a non-global client, this call is made whenever the application whose
// process ID was passed to AddProcess terminates.
//
// For global clients (like us), this is called once just before UnRegister
// and we can ignore the call.

STDMETHODIMP CDgnAppSupport::EndProcess( DWORD dwProcessID )
{
	return S_OK;
}

//---------------------------------------------------------------------------
// This utility function reloads the Python interpreter.  It is called from
// the display window menu and is useful for debugging during development of
// natlinkmain and natlinkutils. In normal use, we do not need to reload the
// Python interpreter.

void CDgnAppSupport::reloadPython()
{
	// free our reference to the Python modules
	Py_XDECREF( m_pNatLinkMain );

	// terminate the Python subsystem
	Py_Finalize();

	// load and initialize the Python system
	Py_Initialize();

	// load the natlink module into Python
	initModule();

	// load the Python code which does most of the work
	m_pDragCode->setDuringInit( TRUE );
	m_pNatLinkMain = PyImport_ImportModule( "natlinkmain" );
	m_pDragCode->setDuringInit( FALSE );
	
	if( m_pNatLinkMain == NULL )
	{
		OutputDebugString(
			TEXT( "NatLink: an exception occurred loading 'natlinkmain' module" ) ); // RW TEXT macro added
		m_pDragCode->displayText(
			"An exception occurred loading 'natlinkmain' module\r\n", TRUE );
		m_pDragCode->displayText(
			"No more error information is available\r\n", TRUE );
	}
}
