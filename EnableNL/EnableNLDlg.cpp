/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 EnableNLDlg.cpp
	This file implements the EnableNL dialog box and contains all of the
	code specific to this application.

 October 12, 2000

 I now support NatSpeak version 5 as well as earlier versions of NatSpeak.
 NatSpeak version 5 adds significant complexity to the algorithms.  Here
 is the technical data.

 For NatSpeak versions prior to version 5, each version of NatSpeak has its
 own subkey under the NaturallySpeaking registry key.  You would iterate
 over that key to find out what versions of NatSpeak were installed.

 For example (NatSpeak Preferred 4.0 and Professional 4.0 both installed):

 	HKEY_LOCAL_MACHINE
	  Software
	    Dragon Systems
		  NaturallySpeaking
		    Preferred 4.0
			  Applications
			    ...
		    Professional 4.0
			  Applications
			    ...

 Starting with version 5.0 but not including the Professional edition, the
 top level registry key was changed and all versions use the same registry
 tree.

 For example (NatSpeak Preferred 5.0 installed):

 	HKEY_LOCAL_MACHINE
	  Software
	    Dragon Systems
		  NaturallySpeaking 5.0
		    Instal
			  Applications
			    ...

 Starting with NatSpeak 5.01 Professional edition the registry is not
 used.  Instead the Applications subtree is stored in a file called
 nsapps.ini in the c:\NatSpeak\Program directory.  In order to find the
 NatSpeak directory you can look in the following file:

    c:\WinNT\Dragon\nsinstalled.ini

 (Although the Windows directory will vary based on the OS.)

 That file will have a series of entries like:

     [NaturallySpeaking 5.0]
     Install=C:\NATSPE~1\Program

 ------

 To enable NatLink macros, we need to create two entries in the registry
 or inifile.  These entries are:

 For registry (NatSpeak 5.0 Preferred and earlier)

    HKEY_LOCAL_MACHINE
	  Software
	    Dragon Systems
 	      NaturallySpeaking 
	        Preferred 4.0
	    	  Applications
			*   .NatLink    
			*     Settings
			*	    "App Support GUID" = "{dd990001-bb89-11d2-b031-0060088dc929}"
			  System
			    Global Clients
			*	  ".NatLink" = "Python Macro Subsystem"

   (lines marked with asterisk are new)

 For nsapps.ini (NatSpeak 5.0 Professional)

     [.Global]
     VoiceCommands File=global.dvc
     App Support GUID={dd100103-6205-11cf-ae61-0000e8a28647}
	 
   * [.NatLink]
   * App Support GUID={dd100103-6205-11cf-ae61-0000e8a28647}

 For nssystem.ini (NatSpeak 5.0 Professional)

     [Global Clients]
     .Global=Default
   * .NatLink=Python Macro Subsystem

*/

#include "stdafx.h"
#include "EnableNL.h"
#include "EnableNLDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

// Subdirectory names for path
#define MACROSYSTEM "MacroSystem"
#define MISCSCRIPTS "MiscScripts"
#define NATLINK_CLSID "{dd990001-bb89-11d2-b031-0060088dc929}"

//---------------------------------------------------------------------------
// Here we search for versions of Dragon NaturallySpeaking.  We return a
// linked list of data structures which contain the relevant information.
//
// Returns NULL is nothing is found.
//
// Caller must free returned data structure.

class InstallData
{
 public:
	InstallData(InstallData * pNext = NULL) : m_pNext(pNext) {}
	~InstallData() { if(m_pNext) delete m_pNext; }
	
	CString m_prettyName;	// name to display in the list box
	CString m_regKeyName;	// registry key name for NatSpeak 5.0 Preferred
							// and earlier; blank otherwise
	CString m_natspeakDir;	// natspeak directory name for NatSpeak 5.0
							// Profressional and later; blank otherwise
	BOOL m_isEnabled;		// indicates whether Python macros are enabled
	BOOL m_wasEnabled;		// original state of Python macros

	InstallData * m_pNext;	// linked list chain pointer

	// Useful for treating this like an array; returns a pointer to the Nth
	// entry in a linked list.
	InstallData * getIndex(int index)
	{
		return ( index < 1 || m_pNext == NULL ) ? 
			this : m_pNext->getIndex(index-1);
	}
};

InstallData * CEnableNLDlg::loadVersions()
{
	InstallData * pTopFound = NULL;

	// Step 1: enumate registry entries from pre-version 5.0

	HKEY hKey;
	HRESULT rc;
	TCHAR szKeyName[ _MAX_PATH ];

	rc = RegOpenKeyEx(
		HKEY_LOCAL_MACHINE,
		"Software\\Dragon Systems\\NaturallySpeaking",
		0, KEY_READ | KEY_WRITE, &hKey );
	
	if( rc == ERROR_SUCCESS )
	{
		for( DWORD dwIndex = 0; TRUE; dwIndex += 1 )
		{
			// get a specific version
			rc = RegEnumKey( hKey, dwIndex, szKeyName, sizeof(szKeyName) );
			if( rc != ERROR_SUCCESS ) break;
	
			// make sure we have a global clients subkey
			CString csSubKey = szKeyName;
			csSubKey += "\\System\\Global Clients";

			HKEY hSubKey;
			
			rc = RegOpenKeyEx(
				hKey, csSubKey, 0, KEY_READ | KEY_WRITE, &hSubKey );
			if( rc != ERROR_SUCCESS ) continue;

			// if we get here then we have an appropiate candidate
			pTopFound = new InstallData( pTopFound );
			pTopFound->m_prettyName = szKeyName;
			pTopFound->m_regKeyName = 
				"Software\\Dragon Systems\\NaturallySpeaking\\";
			pTopFound->m_regKeyName += szKeyName;

			// figure out if macros are enabled
			rc = RegQueryValueEx( hSubKey, ".NatLink", 0, NULL, NULL, NULL );
			pTopFound->m_isEnabled = ( rc == ERROR_SUCCESS );
			pTopFound->m_wasEnabled = pTopFound->m_isEnabled;

			RegCloseKey( hSubKey );
		}

		RegCloseKey( hKey );
	}
	
	// Step 2: look for the NatSpeak 5.0 non-Professional entry

	rc = RegOpenKeyEx(
		HKEY_LOCAL_MACHINE,
		"Software\\Dragon Systems\\NaturallySpeaking 5.0",
		0, KEY_READ | KEY_WRITE, &hKey );
	
	if( rc == ERROR_SUCCESS )
	{
		// make sure we have a global clients subkey
		HKEY hSubKey;

		rc = RegOpenKeyEx(
			hKey,
			"Install\\System\\Global Clients",
			0, KEY_READ | KEY_WRITE, &hSubKey );
		
		if( rc == ERROR_SUCCESS )
		{
			// if we get here then we have an appropiate candidate
			pTopFound = new InstallData( pTopFound );
			pTopFound->m_prettyName = "NaturallySpeaking 5.0 (retail)";
			pTopFound->m_regKeyName =
	   		    "Software\\Dragon Systems\\NaturallySpeaking 5.0\\Install";

			// figure out if macros are enabled
			rc = RegQueryValueEx( hSubKey, ".NatLink", 0, NULL, NULL, NULL );
			pTopFound->m_isEnabled = ( rc == ERROR_SUCCESS );
			pTopFound->m_wasEnabled = pTopFound->m_isEnabled;

			RegCloseKey( hSubKey );
		}
		
		RegCloseKey( hKey );
	}

	// Step 3: look for NatSpeak 5.0 Professional and greater
	TCHAR szFileName[ _MAX_PATH ];

	rc = GetWindowsDirectory( szFileName, sizeof(szFileName) );
	if( rc > 2 )
	{
		// Append a slash if necessary; then append the directory and
		// filename of the NatSpeak installation log
		if( szFileName[ _tcslen(szFileName)-1 ] != '\\' )
		{
			_tcscat( szFileName, "\\");
		}
		_tcscat( szFileName, "Speech\\Dragon\\nsinstalled.ini" );

		// Get all of the section names in this file.  This returns a
		// concatenated series of strings with an empty string at the end.
		TCHAR szSections[ 4096 ];
		rc = GetPrivateProfileSectionNames(
			szSections, sizeof(szSections), szFileName );
		if( rc > 2 )
		{
			for( TCHAR * pSectionName = szSections;
				 *pSectionName;
				 pSectionName += _tcslen(pSectionName) + 1)
			{
				// Get all the installed versions with this name.  Returns a
				// concatenated set of strings of the form XXX=YYY where YYY
				// is the directory name.
				TCHAR szInstalls[ 4096 ];
				rc = GetPrivateProfileSection(
					pSectionName, szInstalls,
					sizeof(szInstalls), szFileName );
				if( rc < 2 ) continue;

				for( TCHAR * pInstallName = szInstalls;
					 *pInstallName;
					 pInstallName += _tcslen(pInstallName) + 1)
				{
					// extract the directory name
					TCHAR * pDirName = _tcschr(pInstallName, '=');
					if( pDirName == NULL ) continue;
					pDirName += 1;

					CString csIniName = pDirName;
					csIniName += "\\nssystem.ini";

					// make sure the global section exists
					TCHAR szBuffer[ 128 ];
					rc = GetPrivateProfileString(
						"Global Clients",
						".Global",
						"", 		// default value
						szBuffer, sizeof(szBuffer),
						csIniName );
					if( rc < 2 ) 
					{
                        // In version 7 the file is stored in a different place
						pDirName = "C:/Documents and Settings/All Users/Application Data/ScanSoft/NaturallySpeaking";
						csIniName = pDirName;
                        csIniName += "\\nssystem.ini";
						rc = GetPrivateProfileString(
						"Global Clients",
						".Global",
						"", 		// default value
						szBuffer, sizeof(szBuffer),
						csIniName );
					}
					if( rc < 2 ) 	continue;
					CString pname = pSectionName;
				
					// if we get here then we have an appropiate candidate
					pTopFound = new InstallData( pTopFound );
					pTopFound->m_prettyName = pname + " (in ";
					pTopFound->m_prettyName += pDirName;
					pTopFound->m_prettyName += ")";
					pTopFound->m_natspeakDir = pDirName;

					// figure out if macros are enabled
					rc = GetPrivateProfileString(
						"Global Clients",
						".NatLink",
						"", 		// default value
						szBuffer, sizeof(szBuffer),
						csIniName );
					pTopFound->m_isEnabled = ( rc > 2 );
					pTopFound->m_wasEnabled = pTopFound->m_isEnabled;
				}
			}
		}
	}

	return pTopFound;
}

/////////////////////////////////////////////////////////////////////////////
// CEnableNLDlg dialog

CEnableNLDlg::CEnableNLDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CEnableNLDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CEnableNLDlg)
	m_checkBox = FALSE;
	m_csVersion = _T("");
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CEnableNLDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CEnableNLDlg)
	DDX_Control(pDX, IDC_VERLIST, m_verList);
	DDX_Check(pDX, IDC_ENABLE, m_checkBox);
	DDX_Text(pDX, IDC_VERSION, m_csVersion);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CEnableNLDlg, CDialog)
	//{{AFX_MSG_MAP(CEnableNLDlg)
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_LBN_SELCHANGE(IDC_VERLIST, OnSelChangeVerList)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CEnableNLDlg message handlers

BOOL CEnableNLDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon

	// pythonVersion is "1.5" or "2.0"
	CString pythonVersion = getPythonVersion();
	if( *pythonVersion )
	{
		m_csVersion = pythonVersion;
		UpdateData(FALSE);

		setPythonPath(pythonVersion);
		copyModules(pythonVersion);
	}
	else
	{
		EndDialog( IDCANCEL );
		return TRUE;
	}

	registerNatlink();

	m_nOldSelection = LB_ERR;
	
	m_pVersions = loadVersions();
	if( m_pVersions == NULL )
	{
		AfxMessageBox(
			"Error: no appropiate versions of NatSpeak were found in the registry." );
		EndDialog( IDCANCEL );
	}
	for( InstallData * pVersion = m_pVersions;
		 pVersion;
		 pVersion = pVersion->m_pNext )
	{
		m_verList.AddString( pVersion->m_prettyName );
	}
	m_verList.SetCurSel( 0 );
	OnSelChangeVerList();
	
	return TRUE;  // return TRUE  unless you set the focus to a control
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CEnableNLDlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

// The system calls this to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CEnableNLDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

void CEnableNLDlg::OnSelChangeVerList() 
{
	// read current checkbox value
	if( m_nOldSelection != LB_ERR )
	{
		UpdateData( TRUE );
		m_pVersions->getIndex(m_nOldSelection)->m_isEnabled = m_checkBox;
	}

	m_nOldSelection = m_verList.GetCurSel();

	// set the checkbox value
	if( m_nOldSelection != LB_ERR )
	{
		m_checkBox = m_pVersions->getIndex(m_nOldSelection)->m_isEnabled;
		UpdateData( FALSE );
	}
}

void CEnableNLDlg::OnOK() 
{
	OnSelChangeVerList();

	enableVersions();

	delete m_pVersions;
	CDialog::OnOK();
}

//---------------------------------------------------------------------------
// In the following registry key:
//
//	  HKEY_LOCAL_MACHINE\Software\Python\PythonCore\XXX\PythonPath\NatLink
//			XXX = Python version "1.5" or "2.0"
//
// we want to set the following default value:
//
//	  "***\MacroSystem;***\MiscScripts"
//
// where *** is the current path to the NatLink subsystem.  We find the path
// by looking at the module name of this program which should be installed
// in the ***\MacroSystem directory.

void CEnableNLDlg::setPythonPath( const char * pythonVersion )
{
	HRESULT rc;

	// Compute the registry string to use
	CString registryPath;
	registryPath = "Software\\Python\\PythonCore\\";
	registryPath += pythonVersion;
	registryPath += "\\PythonPath";

	// compute the path string to use
	CString csParentDir;
	CString csSubDir;
	getDirectory( csParentDir, csSubDir );
	
	if( 0 != csSubDir.CompareNoCase( MACROSYSTEM ) )
	{
		AfxMessageBox(
			"Error: this program should be run from a subdirectory called "
			MACROSYSTEM " which is where natlink.dll, natlinkmain.py, etc. "
			"are located" );
		EndDialog( IDCANCEL );
		return;
	}

	CString csValue;
	csValue = csParentDir;
	csValue += "\\" MACROSYSTEM ";";
	csValue += csParentDir;
	csValue += "\\" MISCSCRIPTS;

	// We handle multiple possible version of Python.  Look for the latest version.

	HKEY hKey;
	rc = RegOpenKeyEx(
		HKEY_LOCAL_MACHINE, registryPath,
		0, KEY_READ | KEY_WRITE, &hKey );
	if( rc != ERROR_SUCCESS )
	{
		AfxMessageBox(
			"Error: Unable to find the registry path for Python.  "
			"Python may not be properly installed" );
		EndDialog( IDCANCEL );
		return;
	}

	HKEY hSubKey;
	rc = RegCreateKeyEx(
		hKey, "NatLink", 0, NULL, REG_OPTION_NON_VOLATILE,
		KEY_ALL_ACCESS, NULL, &hSubKey, NULL );
	if( rc == ERROR_SUCCESS )
	{
		rc = RegSetValueEx(
			hSubKey, "", 0, REG_SZ,
			(const BYTE *)(const char *)csValue, csValue.GetLength()+1 );
		RegCloseKey( hSubKey );
	}

	RegCloseKey( hKey );

	if( rc != ERROR_SUCCESS )
	{
		AfxMessageBox(
			"Error: An unknown error occurred trying to set the Python path "
			"variable in the registry." );
		EndDialog( IDCANCEL );
	}
}

//---------------------------------------------------------------------------
// From the module file name compute the parent directory and its
// subdirectory from which this program is run.  If run from:
//
//	  c:\NatLink\MacroSystem
//
// This function will compute:
//
//	  csParentDir = "c:\NatLink"
//	  csSubKey = "MacroSystem"

void CEnableNLDlg::getDirectory( CString & csParentDir, CString & csSubDir )
{
	csParentDir.Empty();
	csSubDir.Empty();

	size_t buflen = 256;
	while( TRUE )
	{
		char * psz = csParentDir.GetBuffer( buflen );
		DWORD dwCount = GetModuleFileName(
			AfxGetInstanceHandle(), psz, buflen );
		csParentDir.ReleaseBuffer();

		if( dwCount < buflen - 1 )
		{
			break;
		}
		buflen += 256;
	}

	// first strip off the module itself
	int nSlash = csParentDir.ReverseFind( '\\' );
	if( nSlash <= 0 )
	{
		return;
	}
	csParentDir = csParentDir.Left( nSlash );

	// now strip off the directory
	nSlash = csParentDir.ReverseFind( '\\' );
	if( nSlash <= 0 )
	{
		return;
	}
	csSubDir = csParentDir.Mid( nSlash+1 );
	csParentDir = csParentDir.Left( nSlash );
}

//---------------------------------------------------------------------------
// Register the NatLink DLL server by adding a CLSID to the registery.

BOOL CEnableNLDlg::registerNatlink()
{
	HRESULT rc;
	
	HKEY hKey;
	rc = RegOpenKeyEx( HKEY_CLASSES_ROOT, "CLSID", 0, KEY_READ | KEY_WRITE, &hKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	HKEY hGUIDKey;
	rc = RegCreateKeyEx(
		hKey, NATLINK_CLSID, 0, NULL, REG_OPTION_NON_VOLATILE,
		KEY_ALL_ACCESS, NULL, &hGUIDKey, NULL );
	RegCloseKey( hKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	CString csValue = "Python Subsystem for NatSpeak";
	rc = RegSetValueEx(
		hGUIDKey, "", 0, REG_SZ,
		(const BYTE *)(const char *)csValue, csValue.GetLength()+1 );
	if( rc != ERROR_SUCCESS )
	{
		RegCloseKey( hGUIDKey );
		return FALSE;
	}

	HKEY hInprocKey;
	rc = RegCreateKeyEx(
		hGUIDKey, "InprocServer32", 0, NULL, REG_OPTION_NON_VOLATILE,
		KEY_ALL_ACCESS, NULL, &hInprocKey, NULL );
	RegCloseKey( hGUIDKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	// get this module name
	CString csSubDir;
	getDirectory( csValue, csSubDir ); 
	csValue += "\\";
	csValue += csSubDir;
	csValue += "\\natlink.dll";

	rc = RegSetValueEx(
		hInprocKey, "", 0, REG_SZ,
		(const BYTE *)(const char *)csValue, csValue.GetLength()+1 );
	if( rc != ERROR_SUCCESS )
	{
		RegCloseKey( hInprocKey );
		return FALSE;
	}

	csValue = "Apartment";
	rc = RegSetValueEx(
		hInprocKey, "ThreadingModel", 0, REG_SZ,
		(const BYTE *)(const char *)csValue, csValue.GetLength()+1 );
	RegCloseKey( hInprocKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	return TRUE;
}

//---------------------------------------------------------------------------
// Remove the registry value:
//
//	HKEY_LOCAL_MACHINE
//	  regKeyName
//		System\Global Clients
//		  ".Natlink" = "xxx"
//

BOOL removeRegKey( const TCHAR * regKeyName )
{
	HKEY hKey;
	HRESULT rc;

	CString csKeyName = regKeyName;
	csKeyName += "\\System\\Global Clients";

	rc = RegOpenKeyEx(
		HKEY_LOCAL_MACHINE,
		csKeyName,
		0, KEY_READ | KEY_WRITE, &hKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	rc = RegDeleteValue( hKey, ".NatLink" );
	RegCloseKey( hKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	return TRUE;
}

//---------------------------------------------------------------------------
// Add two values to the registry:
//
//  HKEY_LOCAL_MACHINE
//	  regKeyName
//		Applications
//	      .NatLink
//		    Settings
//			  "App Support GUID" = "{dd990001-bb89-11d2-b031-0060088dc929}"
//
//	HKEY_LOCAL_MACHINE
//	  regKeyName
//		System\Global Clients
//		  ".Natlink" = "Python Macro Subsystem"
//

BOOL addRegKey( const TCHAR * regKeyName )
{
	HRESULT rc;

	CString csKeyName = regKeyName;
	csKeyName += "\\Applications";

	HKEY hAppKey;
	rc = RegOpenKeyEx(
		HKEY_LOCAL_MACHINE, csKeyName, 0, KEY_READ | KEY_WRITE, &hAppKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	HKEY hNatKey;
	rc = RegCreateKeyEx(
		hAppKey, ".NatLink", 0, NULL, REG_OPTION_NON_VOLATILE,
		KEY_ALL_ACCESS, NULL, &hNatKey, NULL );
	RegCloseKey( hAppKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	HKEY hSetKey;
	rc = RegCreateKeyEx(
		hNatKey, "Settings", 0, NULL, REG_OPTION_NON_VOLATILE,
		KEY_ALL_ACCESS, NULL, &hSetKey, NULL );
	RegCloseKey( hNatKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	CString csValue = NATLINK_CLSID;
	rc = RegSetValueEx(
		hSetKey, "App Support GUID", 0, REG_SZ,
		(const BYTE *)(const char *)csValue, csValue.GetLength()+1 );
	RegCloseKey( hSetKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	csKeyName = regKeyName;
	csKeyName += "\\System\\Global Clients";

	HKEY hKey;
	rc = RegOpenKeyEx(
		HKEY_LOCAL_MACHINE,
		csKeyName,
		0, KEY_READ | KEY_WRITE, &hKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	csValue = "Python Macro Subsystem";
	rc = RegSetValueEx(
		hKey, ".NatLink", 0, REG_SZ,
		(const BYTE *)(const char *)csValue, csValue.GetLength()+1 );
	RegCloseKey( hKey );
	if( rc != ERROR_SUCCESS )
	{
		return FALSE;
	}

	return TRUE;
}

//---------------------------------------------------------------------------
// Remove one line from nssystem.ini:
//
// 	[Global Clients]
// 	.NatLink=Python Macro Subsystem		<-- delete this line
//

BOOL removeIniEntry( const TCHAR * natspeakDir )
{
	HRESULT rc;
	
	CString csFileName = natspeakDir;
	csFileName += "\\nssystem.ini";

	rc = WritePrivateProfileString(
		"Global Clients", ".NatLink", NULL, csFileName );
	if( rc == FALSE )
	{
		return FALSE;
	}

	return TRUE;
}

//---------------------------------------------------------------------------
// In nsapps.ini add the these two lines:
//
//   [.NatLink]
//   App Support GUID={dd100103-6205-11cf-ae61-0000e8a28647}
//
// In nssystem.ini add the indicated lines:
//
//   [Global Clients]
//   .NatLink=Python Macro Subsystem	<-- add this line

BOOL addIniEntry( const TCHAR * natspeakDir )
{
	HRESULT rc;
	
	CString csFileName = natspeakDir;
	csFileName += "\\nsapps.ini";

	rc = WritePrivateProfileString(
		".NatLink", "App Support GUID", NATLINK_CLSID, csFileName );
	if( rc == FALSE )
	{
		return FALSE;
	}

	csFileName = natspeakDir;
	csFileName += "\\nssystem.ini";

	rc = WritePrivateProfileString(
		"Global Clients", ".NatLink", "Python Macro System", csFileName );
	if( rc == FALSE )
	{
		return FALSE;
	}

	return TRUE;
}

//---------------------------------------------------------------------------
// Enables or disables registry entries for Natlink for each version of
// NatSpeak which is installed.

void CEnableNLDlg::enableVersions()
{
	BOOL bSuccess;
	
	for( InstallData * pVersion = m_pVersions;
		 pVersion != NULL;
		 pVersion = pVersion->m_pNext )
	{
		if( pVersion->m_isEnabled == pVersion->m_wasEnabled )
		{
			continue;
		}
		
		if( !pVersion->m_isEnabled )
		{
			if( pVersion->m_natspeakDir.IsEmpty() )
			{
				bSuccess = removeRegKey( pVersion->m_regKeyName );
			}
			else
			{
				bSuccess = removeIniEntry( pVersion->m_natspeakDir );
			}
			if( !bSuccess )
			{
				AfxMessageBox(
					"Error: cannot delete appropiate registry key, unable to disable macros" );
			}
		}
		else
		{
			if( pVersion->m_natspeakDir.IsEmpty() )
			{
				bSuccess = addRegKey( pVersion->m_regKeyName );
			}
			else
			{
				bSuccess = addIniEntry( pVersion->m_natspeakDir );
			}
			if( !bSuccess )
			{
				AfxMessageBox(
					"Error: cannot add appropiate registry key, unable to enable macros" );
			}
		}
	}
}

//---------------------------------------------------------------------------
// Returns "1.5" or "2.0".
//
// Currently I get the Python version by launching the Python interpreter,
// with a simple script that prints the version, and then parsing the output.

CString CEnableNLDlg::getPythonVersion()
{
	CString pythonVersion;

	char pythonScriptName[ MAX_PATH ];
	tmpnam( pythonScriptName );

	char pythonOutputName[ MAX_PATH ];
	tmpnam( pythonOutputName );

	try
	{
		CStdioFile scriptFile( pythonScriptName, CFile::modeCreate | CFile::modeWrite );
		scriptFile.WriteString( 
			"import sys\n"
			"open(sys.argv[1],'w').write(sys.version[:3])\n" );
		scriptFile.Close();

		int rc = _spawnlp( 
			_P_WAIT,		// mode
			"pythonw.exe",	// cmdname, 
			"pythonw.exe",	// arg0
			pythonScriptName,	// arg1
			pythonOutputName,	// arg2
			NULL );
		if( rc == -1 )
		{
			// Python is probably not on the path
			_unlink( pythonScriptName );
			return getPythonVersionFallback();
		}

		CStdioFile outputFile( pythonOutputName, CFile::modeRead );
		outputFile.ReadString( pythonVersion );
		outputFile.Close();
	}
	catch( CFileException * )
	{
		// Unknown file error has occurred
		return getPythonVersionFallback();
	}

	_unlink( pythonScriptName );
	_unlink( pythonOutputName );

	return pythonVersion;
}

//---------------------------------------------------------------------------
// An alternative for getPythonVersionFronPython that uses the registry
// instead.  Look for the Python registry key for the highest version
// number.

CString CEnableNLDlg::getPythonVersionFallback()
{
	CString pythonVersion;

	HRESULT rc;

	const char * const VERSIONLIST[] = { "2.2", "2.0", "1.5", "" };

	for( int i = 0; *VERSIONLIST[i]; i++ )
	{
		// Compute the registry string to use
		CString registryPath;
		registryPath = "Software\\Python\\PythonCore\\";
		registryPath += VERSIONLIST[i];
		registryPath += "\\PythonPath";

		HKEY hKey;
		rc = RegOpenKeyEx(
			HKEY_LOCAL_MACHINE, registryPath,
			0, KEY_READ | KEY_WRITE, &hKey );
		RegCloseKey( hKey );

		if( rc == ERROR_SUCCESS )
		{
			return VERSIONLIST[i];
		}
	}

	AfxMessageBox(
		"Error: Unable to find the Python version number in the registry "
		"or by calling the Python interpreter.  Make sure that a supported "
		"version of Python is installed on your computer." );
	return "";
}

//---------------------------------------------------------------------------

void CEnableNLDlg::copyModules( const char * pythonVersion )
{
	CString csBaseName;
	CString csSubDir;
	getDirectory( csBaseName, csSubDir ); 
	csBaseName += "\\";
	csBaseName += csSubDir;
	csBaseName += "\\";

	const char * const NAMESTOCOPY[] = { "natlink", "mobiletools", "" };

	for( int i = 0; *NAMESTOCOPY[i]; i++ )
	{
		CString csSource;
		csSource = csBaseName;
		csSource += NAMESTOCOPY[i];
		csSource += pythonVersion[0];
		csSource += pythonVersion[2];
		csSource += ".dll";

		CString csDest;
		csDest = csBaseName;
		csDest += NAMESTOCOPY[i];
		csDest += ".dll";

		try
		{
			CFile sourceFile( csSource, CFile::modeRead | CFile::typeBinary );
			CFile destFile( csDest, CFile::modeCreate | CFile::modeWrite | CFile::typeBinary );

			UINT count;
			char buffer[1024];
			while( (count=sourceFile.Read(buffer,1024)) > 0 )
			{
				destFile.Write(buffer,count);
			}
			sourceFile.Close();
			destFile.Close();
		}
		catch( CFileException * )
		{
			CString csError;
			csError.Format(
				"Error: unable to perform a file copy from\n %s  to\n  %s.",
				(const char *)csSource,	(const char *)csDest );
			AfxMessageBox( csError );
			EndDialog( IDCANCEL );
		}
	}
}

