// CDgnAppSupport.cpp : Implementation of CDgnAppSupport

#include "pch.h"
#include "CDgnAppSupport.h"


CDragonCode* initModule();

// CDgnAppSupport

CDgnAppSupport::~CDgnAppSupport()
{
}

CDgnAppSupport::CDgnAppSupport()
{

	OutputDebugString(L"CDgnAppSupport::CDgnAppSupport");
	m_pNatLinkMain = NULL;
	m_pDragCode = NULL;
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
//	MessageBeep(MB_ICONQUESTION);
//	DebugBreak();
	// load and initialize the Python system
	MessageBox(0, L"PY_Initialize", L"CDgnAppSupport.cpp", 0);

	Py_Initialize();

	// Set sys.argv so it exists as [''].
	PySys_SetArgvEx(1, NULL, 0);

	// load the natlink module into Python and return a pointer to the
	// shared CDragonCode object
	m_pDragCode = initModule();
	m_pDragCode->setAppClass(this);


	// simulate calling natlink.natConnect() except share the site object
	bSuccess = m_pDragCode->natConnect(pIDgnSite);


	if (!bSuccess)
	{

		MessageBox(0, L"natlink failed to connect", L"CDgnAppSupport.cpp", 0);

		OutputDebugString(
			TEXT("NatLink: failed to initialize NatSpeak interfaces")); // RW TEXT macro added
		m_pDragCode->displayText(
			"Failed to initialize NatSpeak interfaces\r\n", TRUE);
		return S_OK;
	}

	MessageBox(0, L"natlink connected", L"CDgnAppSupport.cpp", 0);
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
	PyRun_SimpleString("import winreg, sys");
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
	m_pDragCode->displayText("Importing redirect_output");
	m_pNatLinkMain = PyImport_ImportModule("redirect_output");



	m_pDragCode->displayText("Importing natlinkmain");

	m_pNatLinkMain = PyImport_ImportModule("natlinkmain");

	m_pDragCode->displayText("Imported natlinkmain");

	if (m_pNatLinkMain)
	{
		//call the function start_natlink in natlinkmain.  what will happen?
		//TODO test this.
		m_pDragCode->displayText("calling natlinkmain:start_natlink");
		OutputDebugString(
			TEXT("Calling natlinkmain:start_natlink"));

		MessageBox(0, L"Calling natlinkmain:start_natlink", L"appsup.cpp", MB_OK);

		PyObject* natLinkMain_dict = PyModule_GetDict(m_pNatLinkMain);
		static char const function[] = "start_natlink";
		PyObject* pnatlinkMainFunc = PyDict_GetItemString(natLinkMain_dict, function);
		PyObject* result = PyObject_CallObject(pnatlinkMainFunc, 0);
		OutputDebugString(
			TEXT("Called natlinkmain:start_natlink"));
		MessageBox(0, L"Called natlinkmain:start_natlink", L"appsup.cpp", MB_OK);
		Py_XDECREF(natLinkMain_dict);
		Py_XDECREF(pnatlinkMainFunc);
		Py_XDECREF(result);

	}

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
