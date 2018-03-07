/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 appsupp.h
	The class which NatSpeak calls when it loads a compatibility module.
	This is the definition of a custom COM interface which is called by
	NatSpeak.  The implementation uses ATL for COM intrastructure.
*/

#ifndef appsupp_h
#define appsupp_h

class DECLSPEC_UUID("DD990001-BB89-11d2-B031-0060088DC929") NatLink;
#define IID_IDgnAppSupportA __uuidof(IDgnAppSupportA)

/////////////////////////////////////////////////////////////////////////////
// CDgnAppSupport

class ATL_NO_VTABLE CDgnAppSupport : 
	public CComObjectRootEx<CComSingleThreadModel>,
	public CComCoClass<CDgnAppSupport, &__uuidof(NatLink)>,
	public IDgnAppSupport
{
public:
	CDgnAppSupport();
	~CDgnAppSupport();

	// call this function to re-initialize the Python interface
	void reloadPython();

DECLARE_REGISTRY_RESOURCEID(IDR_APPSUPP)
DECLARE_NOT_AGGREGATABLE(CDgnAppSupport)

BEGIN_COM_MAP(CDgnAppSupport)
	COM_INTERFACE_ENTRY(IDgnAppSupport)
END_COM_MAP()

// IDgnAppSupport
public:
	STDMETHOD(UnRegister)();
	STDMETHOD(EndProcess)(DWORD);
	STDMETHOD(AddProcess)(DWORD, const char *, const char *, DWORD);
	STDMETHOD(Register)(IServiceProvider *);

protected:

	// this is a pointer to the NatSpeak python code module
	PyObject * m_pNatLinkMain;

	// this is a pointer to the CDragonCode module
	CDragonCode * m_pDragCode;
};

#endif // appsupp_h
