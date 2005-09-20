#ifdef UseCLR

#define CLR
#include "DotNetMisc.h"

DotNetMisc::DotNetMisc() {}
DotNetMisc::~DotNetMisc() {}
int DotNetMisc::GetDebugLogOptions()
{
//	__try {
		gcroot<RegistryKey *> rk;
		rk = Registry::CurrentUser->OpenSubKey("Software\\NatLink");
		if (!rk)
		{
			return 0;
		}

		int val = *dynamic_cast<__box int*>(rk->GetValue("NatLinkDebug",0));
		rk->Close();
		return val;
//	}
	

}
#endif