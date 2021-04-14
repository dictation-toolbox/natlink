// CDgnAppSupport.h : Declaration of the CDgnAppSupport

#pragma once
#include "resource.h"       // main symbols


#include <string>
#include "StdAfx.h"
#include "Resource.h"
#include "DragonCode.h"
#include "natlink_i.h"
#include "com/dspeech.h"


#if defined(_WIN32_WCE) && !defined(_CE_DCOM) && !defined(_CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA)
#error "Single-threaded COM objects are not properly supported on Windows CE platform, such as the Windows Mobile platforms that do not include full DCOM support. Define _CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA to force ATL to support creating single-thread COM object's and allow use of it's single-threaded COM object implementations. The threading model in your rgs file was set to 'Free' as that is the only threading model supported in non DCOM Windows CE platforms."
#endif

using namespace ATL;


// CDgnAppSupport

class ATL_NO_VTABLE CDgnAppSupport :
	public CComObjectRootEx<CComSingleThreadModel>,
	public CComCoClass<CDgnAppSupport, &CLSID_CDgnAppSupport>,
	public IDgnAppSupport
{
public:
	CDgnAppSupport();
	~CDgnAppSupport();

	// call this function to re-initialize the Python interface
	void reloadPython();

// no idea where 108 came from - the wizard did it.

DECLARE_REGISTRY_RESOURCEID(IDR_CDGNAPPSUPPORT1)

DECLARE_NOT_AGGREGATABLE(CDgnAppSupport)

BEGIN_COM_MAP(CDgnAppSupport)
	COM_INTERFACE_ENTRY(IDgnAppSupport)
END_COM_MAP()



	DECLARE_PROTECT_FINAL_CONSTRUCT()

	HRESULT FinalConstruct()
	{
		return S_OK;
	}

	void FinalRelease()
	{
	}

	// IDgnAppSupport
public:
	STDMETHOD(UnRegister)();
	STDMETHOD(EndProcess)(DWORD);
#ifdef UNICODE
	STDMETHOD(AddProcess)(DWORD, const wchar_t*, const wchar_t*, DWORD);
#else
	STDMETHOD(AddProcess)(DWORD, const char*, const char*, DWORD);
#endif
	STDMETHOD(Register)(IServiceProvider*);

protected:

	// this is a pointer to the NatSpeak python code module
	PyObject* m_pNatLinkMain;

	// this is a pointer to the CDragonCode module
	CDragonCode* m_pDragCode;



};

OBJECT_ENTRY_AUTO(__uuidof(CDgnAppSupport), CDgnAppSupport)
