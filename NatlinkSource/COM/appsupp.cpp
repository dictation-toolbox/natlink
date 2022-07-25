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
//see https://gist.github.com/pwm1234/05280cf2e462853e183d
static std::string get_this_module_path()
{
	void* address = (void*)get_this_module_path;
	char path[FILENAME_MAX];
	HMODULE hm = NULL;

	if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
		GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
		(LPCSTR)address,
		&hm))
	{
		//if this fails, well just return nonsense.
		return "";
	}
	GetModuleFileNameA(hm, path, sizeof(path));

	std::string p = path;
	return p;
}
static int pyrun_string(std::string python_cmd)
{
	std::string message = std::string("CDgnAppSupport Running python: ") + python_cmd;
	char const* const msg_str = message.c_str();
	OutputDebugStringA(msg_str);
	int rc = PyRun_SimpleString(python_cmd.c_str());
	std::string result_message=std::string("CDganAppSupport Ran ") + python_cmd  + std::string(" result: ") +
		std::to_string(rc);


	OutputDebugStringA(result_message.c_str());
	return rc;
}
static int pyrun_string(const char python_cmd[])
{
	return pyrun_string(std::string(python_cmd));
}

static std::string AddOurDirToConfig(PyConfig *config) {
	using winreg::RegKey, winreg::RegResult;
	// _natlinkcore.pyd (this code, dear reader!) doesn't know where it is; find out

	std::wstring key_wstring(L"SOFTWARE\\Natlink");
    RegKey key;
	RegResult result = key.TryOpen(HKEY_LOCAL_MACHINE, key_wstring.c_str(), KEY_READ);
	if (!result) {
		return (std::string("Error: could not open HKLM\\") + 
				std::string(key_wstring.begin(), key_wstring.end()) + std::string("\n"));
	} 
	else { // now the install location of Natlink pyd and sources is known; add to sys.path
	    if (auto new_wstring = key.TryGetStringValue(L"sitePackagesDir")) {
			// amend psys.path so that the python package 'natlink' can be loaded
			PyStatus status = PyWideStringList_Append(&(config->module_search_paths), 
														(*new_wstring).c_str());
			if (PyStatus_Exception(status))
				return (std::string("Natlink: could not append: ") +
						std::string((*new_wstring).begin(), (*new_wstring).end()) + 
						std::string("\n"));
			else
				return std::string("");
		} else {
			return (std::string("Error: could not open subkey sitePackagesDir of HKLM\\") + 
					std::string(key_wstring.begin(), key_wstring.end()) + std::string("\n"));
		}
	}
}


static std::string AddPythonInstallPathToConfig(PyConfig *config) {
	using winreg::RegKey, winreg::RegResult;
	std::wstring key_wstring(L"SOFTWARE\\Natlink");
    RegKey key;
	RegResult result = key.TryOpen(HKEY_LOCAL_MACHINE, key_wstring.c_str(), KEY_READ);
	if (!result) {
		return (std::string("Error: could not open HKLM\\") + 
				std::string(key_wstring.begin(), key_wstring.end()) + std::string("\n"));
	} 
	else { // now the install location of Python is known
		std::wstring new_wstring(key.GetStringValue(L"pythonInstallPath"));
  	    if (auto new_wstring = key.TryGetStringValue(L"pythonInstallPath")) {
	    	PyConfig_SetString(config, &(config->prefix), (*new_wstring).c_str());
			return std::string("");
		  } else {
			  return (std::string("Error: could not open subkey pythonInstallPath of HKLM\\") + 
					std::string(key_wstring.begin(), key_wstring.end()) + std::string("\n"));
		  }
	}
}


static void DisplaySysPath(CDragonCode* pDragCode) {
	std::wstring str_wstring = std::wstring(Py_GetPath());
	std::string str_string(str_wstring.begin(), str_wstring.end());
	pDragCode->displayText((std::string("initial sys.path: ") + str_string + "\n").c_str(), FALSE);
}

static void DisplayVersions(CDragonCode* pDragCode) {
#ifdef NATLINK_VERSION
	const std::string natlinkVersionMsg = std::string("Natlink Version: ") + std::string(NATLINK_VERSION) + 
										  std::string("\r\n");

	pDragCode->displayText(natlinkVersionMsg.c_str(), FALSE); // TODO: remove since version is showed in title of window
	pDragCode->displayText((std::string("Natlink pyd path: ")+ get_this_module_path()).c_str(),FALSE);
	pDragCode->displayText("\nUse DebugView to debug natlink problems.\n\thttps://docs.microsoft.com/en-us/sysinternals/downloads/debugview\n");
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
		std::string err = std::string("Natlink: an exception occurred in '") + std::string(szModName) + std::string(".") + std::string(szName) + std::string("'.\r\n");
		pDragCode->displayText(err.c_str(), TRUE);
		DisplayPythonException(pDragCode);
		}
	Py_XDECREF(result);
}

// Try to make our customized Python behave like regular Python;
// see https://docs.python.org/3/c-api/init_config.html#init-python-config
std::string DoPyConfig(void) {
	std::string init_error = "";
    PyStatus status;
    PyConfig config;
    PyConfig_InitPythonConfig(&config);

	init_error = AddOurDirToConfig(&config);
	if (!init_error.empty()) {
		goto fail;
	}

	init_error = AddPythonInstallPathToConfig(&config);
	if (!init_error.empty()) {
		goto fail;
	}

    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
		init_error = "Natlink: failed initialize from config\n";
        goto fail;
    }
	
	return init_error; // success, return ""

fail:
   //   PyConfig_Clear(&config);
   //  Py_ExitStatusException(status);
	OutputDebugString(TEXT( "NatLink: failed python_init") );
	
    status = Py_InitializeFromConfig(&config);
	return init_error;
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
	// load and initialize the Python system
	std::string init_error =  DoPyConfig();
	Py_Initialize();

	// load the natlink COM interface into Python and return a pointer to shared CDragonCode object
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
	
    // only now do we have the window to show info and possible error messages from before 
	// Python init
	DisplayVersions(m_pDragCode);
	if ( !init_error.empty()) {
		m_pDragCode->displayText(init_error.c_str());
		return S_OK;
	}

	// now load the Python code which sets all the callback functions
	m_pDragCode->setDuringInit( TRUE );
    m_pNatlinkModule = PyImport_ImportModule( "natlinkcore" );
	if ( m_pNatlinkModule == NULL ) {
		OutputDebugString( TEXT( "Natlink: an exception occurred loading 'natlinkcore' module" ) );
		DisplaySysPath(m_pDragCode);
		DisplayPythonException(m_pDragCode);
		return S_OK;
	} else {
		m_pDragCode->displayText( "Natlink is loaded...\n\n", FALSE );
	}

	//need to add the path of natlinkcore to the Python path.
	//it could be in either platlib\natlinkcore (i.e. the python install diretory/site-packages)
	//sysconfig.get_path('purelib')
	//
	//or in site.USER_SITE/site-package.  
	//
	pyrun_string("import sys,site,sysconfig");
    pyrun_string("import pydebugstring.output as o");

	//add natlinkcore to the import paths, because the is required for pyrun_string to load modules from natlinkcore
	pyrun_string("d1=site.USER_SITE+'\\natlinkcore'");
	pyrun_string("d2=sysconfig.get_path('purelib')+'\\natlinkcore'");

	pyrun_string("sys.path.append(d1)"); 
	pyrun_string("sys.path.append(d2)");

	//we have to import natlinkcore this way as well, so we can use natlinkcore.* in pyrun_string
	//pDragCode->displayText("import redirect\n");

	pyrun_string("from natlinkcore import redirect_output");
	pyrun_string("redirect_output.redirect()");

	pyrun_string("from natlinkcore import loader");
	pyrun_string("loader.run()");

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
