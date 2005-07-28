#include "DotNetBasics.h"

#ifdef CLR
using namespace Microsoft::Win32;
#endif


class DotNetMisc
{
private:
	//GCHANDLE(Object *) h;
public:
	DotNetMisc(void);
	~DotNetMisc(void);
	int GetDebugLogOptions();
};
