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
#include <string>
#include "../StdAfx.h"
#include "../Resource.h"
#include "../DragonCode.h"
#include "appsupp.h"
#include <winreg.h>
#include "../extern/WinReg/WinReg.hpp"

#define WQUOTE_(x)    L#x
#define WQUOTE(x)     WQUOTE_(x)

// #include <plog/Log.h>
// from PythWrap.cpp
CDragonCode * initModule();

/////////////////////////////////////////////////////////////////////////////
// CDgnAppSupport

//---------------------------------------------------------------------------

CDgnAppSupport::CDgnAppSupport()
{
	m_pNatlinkModule = NULL;
	m_pDragCode = NULL;
}

//---------------------------------------------------------------------------

CDgnAppSupport::~CDgnAppSupport()
{
}

// Add natlink .py file directory to sys.path so that 'natlink' 
// module can be loaded (and final desired sys.path can be changed if needed)
// return empty string on success; otherwise return error message
static std::string AddToPythonSysPath(CDragonCode* pDragCode) {
	using winreg::RegKey, winreg::RegResult;
	// _natlinkcore.pyd (this code, dear reader!) doesn't know where it is; find out
	std::wstring key_wstring(L"SOFTWARE\\Python\\PythonCore\\" WQUOTE(PYTHON_VERSION) "-32" 
			         L"\\PythonPath\\" TEXT(MYAPP_NAME));
    RegKey key;
	RegResult result = key.TryOpen(HKEY_LOCAL_MACHINE, key_wstring.c_str(), KEY_READ);
	if (!result) {
		return (std::string("Error: could not open HKLM\\") + 
				std::string(key_wstring.begin(), key_wstring.end()) + 
							std::string("\n"));
	} 
	else { // now the install location of Natlink pyd and sources is known; add to sys.path
		wchar_t *wstring = Py_GetPath();
		std::wstring str_wstring(wstring);
		std::wstring new_wstring(key.GetStringValue(L"") + std::wstring(L"\\;") + str_wstring);
		// amend psys.path so that the python package 'natlink' can be loaded
		Py_SetPath(new_wstring.c_str());
	    return (std::string(""));
	}
}

static void DisplaySysPath(CDragonCode* pDragCode) {
	// display sys.path 
	std::wstring str_wstring = std::wstring(Py_GetPath());
	std::string str_string(str_wstring.begin(), str_wstring.end());
	pDragCode->displayText((std::string("initial sys.path: ") + str_string + "\n").c_str(), FALSE);
}

static void DisplayVersions(CDragonCode* pDragCode) {
#ifdef NATLINK_VERSION
	const std::string natlinkVersionMsg = std::string("Natlink Version: ") + std::string(NATLINK_VERSION) + 
										  std::string("\r\n");
	pDragCode->displayText(natlinkVersionMsg.c_str(), FALSE); // TODO: remove since version is showed in title of window
#endif
	const std::string pythonVersionMsg = std::string("Python Version: ") + std::string(Py_GetVersion()) + std::string("\r\n");
	pDragCode->displayText(pythonVersionMsg.c_str(), FALSE);
}

static void DisplayPythonException(CDragonCode* pDragCode) {
	if (PyErr_Occurred()) {
			PyObject* ptype, * pvalue, * ptraceback;
			PyErr_Fetch(&ptype, &pvalue, &ptraceback);
			if (pvalue) {
				PyObject* pstr = PyObject_Str(pvalue);
				if (pstr) {
					const char* pStrErrorMessage = PyUnicode_AsUTF8(pstr);
					pDragCode->displayText("Python exception: ", TRUE);
					pDragCode->displayText(pStrErrorMessage, TRUE);
					pDragCode->displayText("\n", TRUE);
				}
				Py_XDECREF(pstr);
			}
			PyErr_Restore(ptype, pvalue, ptraceback);
			PyErr_Clear();
		}
}

static void CallPyFunctionOrDisplayError(CDragonCode* pDragCode, PyObject* pMod, const char* szModName, const char* szName)
{
	PyObject* result = PyObject_CallMethod(pMod, szName, NULL);
	if (result == NULL)
	{
		std::string err = std::string("NatLink: an exception occurred in '") + std::string(szModName) + std::string(".") + std::string(szName) + std::string("'.\r\n");
		pDragCode->displayText(err.c_str(), TRUE);
		DisplayPythonException(pDragCode);
		}
	Py_XDECREF(result);
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
	// when this code (_natlinkcore.pyd) executes, the python interpreter (included in 
	// the natlink library as a sibling of of _natlinkcore.pyd) has already been 
	// dynamically linked to offer CPython calls, but it doesn't know where the natlink
	// python code is, so help it!
	std::string syspath_error = AddToPythonSysPath(m_pDragCode);
	// load and initialize the Python system
	Py_Initialize();
	// set sys.argv so it exists as [''].
	PySys_SetArgvEx(1, NULL, 0);

	// load the natlink module into Python and return a pointer to shared CDragonCode object
	m_pDragCode = initModule();
	m_pDragCode->setAppClass( this );

	// simulate calling natlink.natConnect() except share the site object
	BOOL bSuccess = m_pDragCode->natConnect( pIDgnSite );
	if( !bSuccess )	{
		OutputDebugString(
			TEXT( "NatLink: failed to initialize NatSpeak interfaces") );
		m_pDragCode->displayText( "Failed to initialize NatSpeak interfaces\r\n", TRUE ); // TODO: bug? won't show
		return S_OK;
	}
	
    // only now do we have the window to show info and possible error message from registry lookup
	DisplayVersions(m_pDragCode);
	if ( !syspath_error.empty()) {
		m_pDragCode->displayText(syspath_error.c_str());
		return S_OK;
	}

	// now load the Python code which sets all the callback functions
	m_pDragCode->setDuringInit( TRUE );
    m_pNatlinkModule = PyImport_ImportModule( "natlink" );
	if ( m_pNatlinkModule == NULL ) {
		OutputDebugString( TEXT( "NatLink: an exception occurred loading 'natlink' module" ) );
		DisplaySysPath(m_pDragCode);
		DisplayPythonException(m_pDragCode);
		return S_OK;
	} else {
		m_pDragCode->displayText( "NatLink: LOADED!\n", FALSE );
	}
	CallPyFunctionOrDisplayError(m_pDragCode, m_pNatlinkModule, "natlink", "redirect_all_output_to_natlink_window");
	DisplayPythonException(m_pDragCode);
	CallPyFunctionOrDisplayError(m_pDragCode, m_pNatlinkModule, "natlink", "run_loader");
	DisplayPythonException(m_pDragCode);
	m_pDragCode->setDuringInit( FALSE );
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
	Py_XDECREF( m_pNatlinkModule );

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
	PyImport_ReloadModule(m_pNatlinkModule);
}
