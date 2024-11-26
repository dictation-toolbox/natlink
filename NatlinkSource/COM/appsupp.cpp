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
	OutputDebugStringA("CDgnAppSupport::CDgnAppSupport");
	m_pNatlinkModule = NULL;
	m_pDragCode = NULL;
}

//---------------------------------------------------------------------------

CDgnAppSupport::~CDgnAppSupport()
{
		OutputDebugStringA("CDgnAppSupport::~CDgnAppSupport");
}
//see https://gist.github.com/pwm1234/05280cf2e462853e183d
static std::string get_this_module_path()

{
	OutputDebugStringA("get_this_module_path");
	void* address = (void*)get_this_module_path;
	char path[FILENAME_MAX];
	HMODULE hm = NULL;

	if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
		GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
		(LPCSTR)address,
		&hm))
	{	OutputDebugString(TEXT("get_this_module_path fail GetModuleHandleExA"));
		//if this fails, well just return nonsense.
		return "";
	}
	GetModuleFileNameA(hm, path, sizeof(path));

	std::string p = path;
	std::string msg = std::string("get_this_module_path returning: ") + p;
	OutputDebugStringA(msg.c_str());

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
	try
	{
		using winreg::RegKey, winreg::RegResult;
		std::wstring key_wstring(L"SOFTWARE\\Natlink");
		RegKey key;
		std::wstring msg=std::wstring(L"AddPythonInstallPathToConfig:  key_wstring: ")+key_wstring + L" trying TryOpen";
		OutputDebugStringW(msg.c_str());

		RegResult result = key.TryOpen(HKEY_LOCAL_MACHINE, key_wstring.c_str(), KEY_READ);
		OutputDebugString(TEXT("Try Open returned"));
		

		if (!result) {
			return (std::string("Error: could not open HKLM\\") + 
					std::string(key_wstring.begin(), key_wstring.end()) + std::string("\n"));
		} 
		else { // now the install location of Python is known
			OutputDebugString(L"Attempted pythonInstallPath");
			std::wstring new_wstring(key.GetStringValue(L"pythonInstallPath"));
			OutputDebugString( (std::wstring(L"new_wstring: ") + new_wstring).c_str());	

			OutputDebugString(L"Attempted pythonInstallPath again");

			if (auto new_wstring = key.TryGetStringValue(L"pythonInstallPath")) {

				OutputDebugString(std::wstring(L"Attempting PyConfig_SetString: ").c_str() );
				OutputDebugString( (std::wstring(L"new_wstring: ") + *new_wstring).c_str());	

				PyConfig_SetString(config, &(config->prefix), (*new_wstring).c_str());
				OutputDebugString(std::wstring(L"SetString Completed ").c_str() );

				return std::string("");
			} else {
				return (std::string("Error: could not open subkey pythonInstallPath of HKLM\\") + 
						std::string(key_wstring.begin(), key_wstring.end()) + std::string("\n"));
			}
		}
	}
	catch(...)
	{
		OutputDebugString(L"Exception in AddPythonInstallPathToConfig");
		return std::string("");
	}
	return std::string("");
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

	OutputDebugString(TEXT("DoPyConfig"));

	std::string init_error = "";
    PyStatus status;
    PyConfig config;
    PyConfig_InitPythonConfig(&config);
	OutputDebugString(TEXT("DoPyConfig PyConfig_InitPythonConfig done, attempt AddOutDirToConfig"));


	init_error = AddOurDirToConfig(&config);

	std::string msg1 = std::string("DoPyConfig PyConfig_InitPythonConfig done, init_error: ")+ init_error;
	OutputDebugStringA(msg1.c_str());

	if (!init_error.empty()) {
		goto fail;
	}
	OutputDebugString(TEXT("DoPyConfig  attempt AddPythonInstallPathToConfig"));

	init_error = AddPythonInstallPathToConfig(&config);
	if (!init_error.empty()) {
		goto fail;
	}
	OutputDebugString(TEXT("DoPyConfig  attempt PyConfig_SetString"));

	status = PyConfig_SetString(&config, &(config.program_name), L"Python");
	if (PyStatus_Exception(status)) {
		init_error = "Natlink: failed to set program_name\n";
		goto fail;
	}
	OutputDebugString(TEXT("DoPyConfig  attempt PyIntializeFromConfig"));

    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
		init_error = "Natlink: failed initialize from config\n";
        goto fail;
    }

	OutputDebugString(TEXT("DoPyConfig   sucess"));

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
	OutputDebugString(TEXT("CDgnAppSupport::Register"));

	// TODO check here with C++ if Natlink is enabled for the current
	// windows user.  If not, return S_OK early

	// load and initialize the Python system
	std::string init_error =  DoPyConfig();
	Py_Initialize();

	// load the natlink COM interface into Python and return a pointer to shared CDragonCode object
	m_pDragCode = initModule();
	m_pDragCode->setAppClass( this );

	// start the message window, without a callback and with all menu items
	// disabled, in order to use displayText()
	// this is fine, the callback and menu will be set up later
	m_pDragCode->setMessageWindow( NULL, 0x4 );

	// simulate calling natlink.natConnect() except share the site object
	BOOL bSuccess = m_pDragCode->natConnect( pIDgnSite );
	if( !bSuccess )	{
		OutputDebugString(
			TEXT( "NatLink: failed to initialize NatSpeak interfaces") );
		m_pDragCode->displayText( "Failed to initialize NatSpeak interfaces\r\n", TRUE );
		return S_OK;
	}

    // show info and error messages
	DisplayVersions(m_pDragCode);
	if ( !init_error.empty()) {
		OutputDebugStringA(init_error.c_str() );
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
		OutputDebugString( TEXT( "Natlink is loaded..." ) );

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
	OutputDebugString( TEXT( "CDgnAppSupport::UnRegister, calling natDisconnect" ) );

	// simulate calling natlink.natDisconnect()
	m_pDragCode->natDisconnect();

	OutputDebugString( TEXT( "CDgnAppSupport::UnRegister, free reference to Python modules" ) );

	// free our reference to the Python modules
	Py_XDECREF( m_pNatlinkModule );

	// finalize the Python interpreter
	OutputDebugString( TEXT( "CDgnAppSupport::UnRegister, finalize interpreter" ) );

	Py_Finalize();

	PyMem_RawFree(L"python");

	// finalize the Python interpreter
	OutputDebugString( TEXT( "CDgnAppSupport::UnRegister, exit UnRegister" ) );

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
