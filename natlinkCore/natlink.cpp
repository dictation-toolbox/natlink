/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 natlink.cpp
	This file was originally constructed by the Visual C++ AppWizard.  This
	file contains the basic code necessary to allow natlink.dll to function
	as a COM server.
*/

#include "stdafx.h"
#include "resource.h"
#include "DragCode.h"

#include "appsupp.h"
#ifdef UseCLR
#include <_vcclrit.h>
#endif


CComModule _Module;

BEGIN_OBJECT_MAP(ObjectMap)
	OBJECT_ENTRY( __uuidof(NatLink), CDgnAppSupport)
END_OBJECT_MAP()

OBJECT_ENTRY_AUTO( __uuidof(NatLink), CDgnAppSupport)
/////////////////////////////////////////////////////////////////////////////
// DLL Entry Point
//http://support.microsoft.com/Default.aspx?id=814472

extern "C"
BOOL WINAPI DllMain(HINSTANCE hInstance, DWORD dwReason, LPVOID /*lpReserved*/)
{
	if (dwReason == DLL_PROCESS_ATTACH)
	{
		_Module.Init(ObjectMap, hInstance);
		DisableThreadLibraryCalls(hInstance);

		// this is needed for when you run this module from within Python
		// and you use the second thread with its dialog box
		LoadLibrary("riched32");
	}
	else if (dwReason == DLL_PROCESS_DETACH)
		_Module.Term();
	return TRUE;    // ok
}

/////////////////////////////////////////////////////////////////////////////
// Used to determine whether the DLL can be unloaded by OLE

STDAPI DllCanUnloadNow(void)
{
	if ( _Module.GetLockCount() == 0 )
	{
#ifdef UseCLR
		__crt_dll_terminate();
#endif
        return S_OK;
	}
    else
    {
        return S_FALSE;
    }
}

/////////////////////////////////////////////////////////////////////////////
// Returns a class factory to create an object of the requested type

STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID* ppv)
{
#ifdef UseCLR
	if ( !( __crt_dll_initialize() ) )
	{
		return E_FAIL;
	}
    else
    {
        return _Module.GetClassObject(rclsid, riid, ppv);
    }
#else
        return _Module.GetClassObject(rclsid, riid, ppv);
#endif

}

/////////////////////////////////////////////////////////////////////////////
// DllRegisterServer - Adds entries to the system registry

STDAPI DllRegisterServer(void)
{
#ifdef UseCLR
	if ( !( __crt_dll_initialize() ) )
	{
		return E_FAIL;
	}
#endif

	// Call your registration code here
    HRESULT hr = _Module.RegisterServer(FALSE);
    return hr;
}

/////////////////////////////////////////////////////////////////////////////
// DllUnregisterServer - Removes entries from the system registry

STDAPI DllUnregisterServer(void)
{
	 HRESULT hr = S_OK;
#ifdef UseCLR
	__crt_dll_terminate();
#endif

    // Call your unregistration code here
    hr = _Module.UnregisterServer();
    return hr;
}
