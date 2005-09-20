#pragma once

#ifdef UseCLR

#ifdef CLR
#using <mscorlib.dll>
#using <System.dll>
#using "MessageWindow.dll"
using namespace System;
using namespace NatLink::MessageWindow;
#endif


#ifdef CLR
# define GCHANDLE(T) gcroot<T>
#else
# define GCHANDLE(T) intptr_t
#endif


class CMMessageWindow
{
private:
	GCHANDLE(NLMessageWindow *) h;
public:
	CMMessageWindow(void);
	~CMMessageWindow(void);
	void ShowError(const char *);
	void ShowMessage(const char *);
};

#endif
