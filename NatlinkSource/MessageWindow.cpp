/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 secdthrd.cpp
	This file contains the code which handles the second thread used in the
	natlink module.  The second thread provised a dialog in which we display
	Python error messages

 April 25, 1999
	- packaged for external release

 March 3, 1999
	- initial version
*/

#include "stdafx.h"
#include "Resource.h"
#include "MessageWindow.h"
#include <richedit.h>

// This is the message we send to the other thread to add text to the output
// window.  wParam = TRUE for error text, FALSE for normal text.  lParam is
// the pointer to a string to display.  The thread should delete the string
// when finished.
#define WM_SHOWTEXT (WM_USER+362)

// Send this message to the other thread to destroy the window and exit the
// thread.
#define WM_EXITTHREAD (WM_USER+363)

// The color for error messages
#define DARKRED RGB( 128, 0, 0 )

//---------------------------------------------------------------------------
// Called when a message is sent to the dialog box.  Return FALSE to tell
// the dialog box default window message handler to process the message.

BOOL CALLBACK dialogProc( 
	HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam )
{
	// This is the threads copy of the MessageWindow class pointer. I
	// supposed that this should not really be global but stored in some
	// thread or windows storage instead. Oh, well.
	static MessageWindow * s_pSecdThrd = NULL;

	switch( msg )
	{
	    case WM_CREATE:

            return TRUE;
	 case WM_INITDIALOG:
         HMENU hMenu, hSubMenu;

            hMenu = CreateMenu();
            hSubMenu = CreatePopupMenu();
            AppendMenu(hSubMenu, MF_STRING, IDD_RELOAD, L"&Reload");
            AppendMenu(hMenu, MF_STRING | MF_POPUP, (UINT)hSubMenu, L"&File");



            SetMenu(hWnd, hMenu);
		s_pSecdThrd = (MessageWindow *)lParam;
		ShowWindow( hWnd, SW_HIDE );
		return TRUE;

	 case WM_EXITTHREAD:
		DestroyWindow( hWnd );
		return TRUE;
		
	 case WM_DESTROY:
		PostQuitMessage( 0 );
		return FALSE;

	 case WM_CLOSE:
		// do not really close, hide instead
		ShowWindow( hWnd, SW_HIDE );
		// also clear out the contents of the window
		SetDlgItemText( hWnd, IDC_RICHEDIT, TEXT( "" ) ); // RW TEXT macro added
		return TRUE;

	 case WM_COMMAND:
		if( s_pSecdThrd && s_pSecdThrd->getMsgWnd() )
		{
			PostMessage( s_pSecdThrd->getMsgWnd(), msg, wParam, lParam );
		}
		return TRUE;

	 case WM_SIZE: // RW Added: track resizing of the window and call repaint
		{
			HWND hEdit = GetDlgItem( hWnd, IDC_RICHEDIT );
			MoveWindow(hEdit, 0, 0,
				LOWORD(lParam),        // width of client area 
				HIWORD(lParam),        // height of client area 
				TRUE);					// repaint window
		}
	 return TRUE;

	 case WM_SHOWTEXT:
		{
			char * pszText = (char *)lParam;

			ShowWindow( hWnd, SW_SHOW );
			
			CHARFORMAT chForm;
			chForm.cbSize = sizeof(chForm);
			chForm.dwMask = CFM_COLOR;
			chForm.crTextColor =
				wParam ? DARKRED : GetSysColor( COLOR_WINDOWTEXT );
			chForm.dwEffects = 0;
						
			HWND hEdit = GetDlgItem( hWnd, IDC_RICHEDIT );
			int ndx = GetWindowTextLength( hEdit);
			#ifdef WIN32
				SendMessage( hEdit, EM_SETSEL, (WPARAM)ndx, (LPARAM)ndx );
			#else
				SendMessage( hEdit, EM_SETSEL, 0, MAKELONG( ndx, ndx ) );
			#endif
			//SendMessage( hEdit, EM_SETSEL, 0x7FFF, 0x7FFF );
			SendMessage( hEdit, EM_SETCHARFORMAT, SCF_SELECTION, (LPARAM) &chForm );
			#ifdef UNICODE
				int size_needed = ::MultiByteToWideChar( CP_ACP, 0, pszText, -1, NULL, 0 );
				TCHAR * pszTextW = new TCHAR[ size_needed ];
				::MultiByteToWideChar( CP_ACP, 0, pszText, -1, pszTextW, size_needed );

				SendMessage( hEdit, EM_REPLACESEL, FALSE, (LPARAM) pszTextW );
				if ( pszTextW )
					delete [] pszTextW;
			#else
				SendMessage( hEdit, EM_REPLACESEL, FALSE, (LPARAM)pszText );
			#endif
			//SendMessage( hEdit, EM_SETSEL, 0x7FFF, 0x7FFF );
			SendMessage( hEdit, EM_SCROLLCARET, 0, 0 );
			if ( pszText )
				delete pszText;			
		}
		return TRUE;
		
	 default:
		return FALSE;
	}
}

//---------------------------------------------------------------------------
// This is the main routine which the thread runs.  It contains a windows
// message loop and will not return until the thread returns.

DWORD CALLBACK threadMain( void * pArg )
{
	MessageWindow * pThis = (MessageWindow *)pArg;

	// create a dialog box to display the messages

	HINSTANCE hInstance = _Module.GetModuleInstance();

	HWND hWnd = CreateDialogParam(
		hInstance,						// instance handle
		MAKEINTRESOURCE( IDD_STDOUT ), 	// dialog box template
		NULL,							// parent window
		dialogProc,						// dialog box window proc
		(LPARAM)pThis );				// parameter to pass
	assert( hWnd );

	pThis->setOutWnd( hWnd );
	pThis->signalEvent();

	if( hWnd == NULL )
	{
		return 1;
	}
	
	// enter a Windows message loop

	MSG msg;
	while( GetMessage( &msg, NULL, NULL, NULL ) )
	{
		if( !IsDialogMessage( hWnd, &msg ) )
		{
			TranslateMessage( &msg );
			DispatchMessage( &msg );
		}
	}

	return 0;
}

//---------------------------------------------------------------------------

MessageWindow::MessageWindow()
{
	// create the thread we use to display messages; we use an event to make
	// sure that the thread has started before continuing

	m_hEvent = CreateEvent(
		NULL,	// security options
		TRUE,	// manual reset
		FALSE,	// not signaled
		NULL );	// name

	DWORD dwId;
	m_hThread = CreateThread(
		NULL,			// security (use default)
		0, 				// stack size (use default)
		threadMain,		// thread function
		(void *)this,	// argument for thread
		0,				// creation flags
		&dwId );		// address for returned thread ID
	assert( m_hThread != NULL );

	if ( m_hEvent)
	{
		WaitForSingleObject( m_hEvent, 1000 );
		CloseHandle( m_hEvent );
		m_hEvent = NULL;
	}
}

//---------------------------------------------------------------------------

MessageWindow::~MessageWindow()
{
	// terminate the output window then wait for the thread to terminate

	if( m_hOutWnd )
	{
		PostMessage( m_hOutWnd, WM_EXITTHREAD, 0, 0 );
		m_hOutWnd = NULL;
	}
	if( m_hThread != NULL )
	{
		WaitForSingleObject( m_hThread, 1000 /*ms*/ );
		m_hThread = NULL;
	}
}

//---------------------------------------------------------------------------

void MessageWindow::displayText(const char * pszText, BOOL bError )
{
	if( m_hOutWnd )
	{
		char * pszCopy = _strdup( pszText );
		PostMessage( m_hOutWnd, WM_SHOWTEXT, bError, (LPARAM)pszCopy );
	}
}
