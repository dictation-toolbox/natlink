// dllmain.h : Declaration of module class.
#ifndef dllmain_h
#define dllmain_h

#include "initguid.h"
#include "Resource.h"
#include "natlink_i.h"
class CnatlinkModule : public ATL::CAtlDllModuleT< CnatlinkModule >
{
public :
	DECLARE_LIBID(LIBID_natlinkLib)
	DECLARE_REGISTRY_APPID_RESOURCEID(IDR_NATLINK, "{d1277b20-15d9-4f65-bacc-3e3257e89efd}")
};

extern class CnatlinkModule _AtlModule;
#endif