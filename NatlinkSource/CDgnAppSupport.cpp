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
#include <algorithm>
#include "stdafx.h"
#include "CdgnAppSupport.h"

// #include <plog/Log.h>
// from PythWrap.cpp
CDragonCode* initModule();


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

STDMETHODIMP CDgnAppSupport::Register(IServiceProvider* pIDgnSite)
{
	BOOL bSuccess;
	// load and initialize the Python system

	std::string this_module_path = get_this_module_path();
	size_t const last_slash = this_module_path.find_last_of("\\");

	//site-packages should be located two above the natlink.pyd.
	//keep this code around lest we decide to support virtual environments.
	std::string site_packages = this_module_path;
	site_packages.erase(last_slash, -1);
	size_t const last_slash2 = site_packages.find_last_of("\\");
	site_packages.erase(last_slash2, -1);

	
	Py_Initialize();

	// Set sys.argv so it exists as [''].
	PySys_SetArgvEx(1, NULL, 0);
	PyRun_SimpleString("import winreg, sys");

	// load the natlink module into Python and return a pointer to the
	// shared CDragonCode object
	m_pDragCode = initModule();

	m_pDragCode->setAppClass(this);

//	m_pDragCode->displayText(
//		"\nCDgnAppSupport::Register calling natConnect\r\n", TRUE);
	// simulate calling natlink.natConnect() except share the site object
	bSuccess = m_pDragCode->natConnect(pIDgnSite);


	if (!bSuccess)
	{
		OutputDebugString(
			TEXT("NatLink: failed to initialize NatSpeak interfaces")); // RW TEXT macro added
		m_pDragCode->displayText(
			"Failed to initialize NatSpeak interfaces\r\n", TRUE);
		return S_OK;
	}

	//this is the first place to call m_pDragCode->displayText (or the other functions
	//that write to the message window) where output will appear.

	PyRun_SimpleString("import winreg, sys");

	


	/*
	* https://www.python.org/dev/peps/pep-0514/
	* According to PEP514 python should scan this registry location when
	* it builds sys.path when the interpreter is initialised. At least on
	* my system this is not happening correctly, and natlinkmain is not being
	* found. This code pulls the value (set by the config scripts) from the
	* registry manually and adds it to the module search path.
	*
	* Exceptions raised here will not cause a crash, so the worst case scenario
	* is that we add a value to the path which is already there.
	*/


	PyRun_SimpleString("hive, key, flags = (winreg.HKEY_LOCAL_MACHINE, f\"Software\\\\Python\\\\PythonCore\\\\{str(sys.winver)}\\\\PythonPath\\\\Natlink\", winreg.KEY_WOW64_32KEY)");
	// PyRun_SimpleString returns 0 on success and -1 if an exception is raised.
	if (PyRun_SimpleString("natlink_key = winreg.OpenKeyEx(hive, key, access=winreg.KEY_READ | flags)")) {
		m_pDragCode->displayText("Failed to find Natlink key in Windows registry.\r\n");
	}
	if (PyRun_SimpleString("core_path = winreg.QueryValue(natlink_key, \"\")")) {
		m_pDragCode->displayText("Failed to extract value from Natlink key.\r\n");
	}
	PyRun_SimpleString("sys.path.append(core_path)");
	PyRun_SimpleString("winreg.CloseKey(natlink_key)");


	// now load the Python code which sets all the callback functions
	m_pDragCode->setDuringInit(TRUE);
	m_pNatLinkMain = PyImport_ImportModule("redirect_output");
	wchar_t * prefix  = Py_GetPrefix();

	//add the site-packages in case it isn't (i.e. becuase of virtualenv).
	std::replace(site_packages.begin(), site_packages.end(), '\\', '/');

	
	PyRun_SimpleString((std::string("natlink_local_site_package = '") +   site_packages + "'").c_str()); 

	std::string site_packages_cmd = std::string("sys.path.insert(0,natlink_local_site_package)");
	PyRun_SimpleString(site_packages_cmd.c_str());

	m_pDragCode->displayText(FALSE, TRUE, "Displaying Python Environment:");
	m_pNatLinkMain = PyImport_ImportModule("natlinkcore.natlinkpythoninfo");

	m_pNatLinkMain = PyImport_ImportModule("natlinkcore.natlinkmain");
	m_pDragCode->setDuringInit(FALSE);


	if (m_pNatLinkMain == NULL) {
		OutputDebugString(
			TEXT("NatLink: an exception occurred loading 'natlinkmain' module")); // RW TEXT macro added
		m_pDragCode->displayText(
			"An exception occurred loading 'natlinkmain' module\r\n", TRUE);
		if (PyErr_Occurred()) {
			PyObject* ptype, * pvalue, * ptraceback;
			PyErr_Fetch(&ptype, &pvalue, &ptraceback);
			if (pvalue) {
				PyObject* pstr = PyObject_Str(pvalue);
				if (pstr) {
					const char* pStrErrorMessage = PyUnicode_AsUTF8(pstr);
					m_pDragCode->displayText("Error message:\r\n");
					m_pDragCode->displayText(pStrErrorMessage, TRUE);
				}
				Py_XDECREF(pstr);
			}
			PyErr_Restore(ptype, pvalue, ptraceback);
		}
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
	Py_XDECREF(m_pNatLinkMain);

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
	const wchar_t* pszModuleName,
	const wchar_t* pszRegistryKey,
	DWORD lcid)
{
	return S_OK;
}
#else
STDMETHODIMP CDgnAppSupport::AddProcess(
	DWORD dwProcessID,
	const char* pszModuleName,
	const char* pszRegistryKey,
	DWORD lcid)
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

STDMETHODIMP CDgnAppSupport::EndProcess(DWORD dwProcessID)
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
	PyImport_ReloadModule(m_pNatLinkMain);
}
