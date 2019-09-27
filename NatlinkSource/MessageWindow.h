/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 secdthrd.h
	Declarations for the second thread.  See SecdThrd.cpp for details.
*/

class CSecondThread
{
 public:
	// the constructor will create the thread
	CSecondThread();

	// the destructor will terminate the thread
	~CSecondThread();

	// this will post a string to the output window in the second thread
	void displayText( const char * pszText, BOOL bError );

	// we tell the second thread the handle of a window in which the
	// WM_COMMAND messages received by the output window should be reposted
	void setMsgWnd( HWND hWnd ) { m_hMsgWnd = hWnd; }

	// these are called from the second thread itself
	void setOutWnd( HWND hWnd ) { m_hOutWnd = hWnd; }
	void signalEvent() { SetEvent( m_hEvent ); }
	HWND getMsgWnd() { return m_hMsgWnd; }

 protected:
	// This is the window handle in the primarty thread where we
	// send WM_COMMAND messages
	HWND m_hMsgWnd;
		
	// This is the handle of the thread which we use to wait for the thread
	// to terminate
	HANDLE m_hThread;

	// This is the handle of a event object which we use to wait for the
	// thread to start execution
	HANDLE m_hEvent;

	// This is the handle of the output window itself
	HWND m_hOutWnd;
};
