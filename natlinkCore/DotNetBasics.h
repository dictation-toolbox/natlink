#ifdef CLR
#include <vcclr.h>

#using <mscorlib.dll>
#using <System.dll>


using namespace System;


#define GCHANDLE(T) gcroot<T>







#else
#define GCHANDLE(T) intptr_t
#endif
