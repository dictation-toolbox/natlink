//#include "stdafx.h"
#ifdef UseCLR

#pragma managed
#define CLR
#using <mscorlib.dll>
#using <System.dll>
#using <System.Windows.Forms.dll>
#include <vcclr.h>
using namespace System;


[assembly: System::Reflection::AssemblyVersionAttribute("1.3.4.0")];
[assembly: System::Reflection::AssemblyKeyFileAttribute("..\\NatLink.key")];
using namespace System::Windows::Forms;



#include ".\cmmessagewindow.h"


CMMessageWindow::CMMessageWindow(void)
{
		h= new NLMessageWindow();
	//catch (gcroot<Exception*> ex)
	//{
	//	System::Windows::Forms::MessageBox::Show(ex->ToString());
	//	System::IO::StreamWriter *f = new System::IO::StreamWriter("C:\\Documents and Settings\\swein\\My Documents\\NatLink\\f.txt",true);
	//	f->WriteLine(ex->ToString());
	//	f->Close();
	//}
}

CMMessageWindow::~CMMessageWindow(void)
{
}
void CMMessageWindow::ShowError(const char *msg)
{
	gcroot<String *> m = new String(msg);
	h->ShowError(m);
}


void CMMessageWindow::ShowMessage(const char *msg)
{
	gcroot<String *> m = new String(msg);
	h->ShowMessage(m);
}

#endif