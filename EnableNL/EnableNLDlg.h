/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 EnableNLDlg.h
	This file declares the EnableNL dialog box
*/

#if !defined(AFX_ENABLENLDLG_H__C50695E6_0C4B_11D3_9240_00104B60CF64__INCLUDED_)
#define AFX_ENABLENLDLG_H__C50695E6_0C4B_11D3_9240_00104B60CF64__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

/////////////////////////////////////////////////////////////////////////////
// CEnableNLDlg dialog

class CEnableNLDlg : public CDialog
{
// Construction
public:
	CEnableNLDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CEnableNLDlg)
	enum { IDD = IDD_ENABLENL_DIALOG };
	CListBox	m_verList;
	BOOL	m_checkBox;
	CString	m_csVersion;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CEnableNLDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CEnableNLDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnSelChangeVerList();
	virtual void OnOK();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()

	// This is a linked list of installed version
	class InstallData * m_pVersions;

	// This looks up existing versions of NatSpeak in the registry
	class InstallData * loadVersions();

	// This enables or disables NatLink for existing versions
	void enableVersions();

	// This is the previous selection in the list box, the one for which the
	// checkbox applies
	int m_nOldSelection;

	// This registers the natlink.dll.  It is equivelent to calling
	// regsvr32 on natlink.dll
	BOOL registerNatlink();

	// This sets the Python path variables
	void setPythonPath( const char * pythonVersion );

	// This figures out the parent directory from which this program is run.
	void getDirectory( CString & csParentDir, CString & csSubDir );

	// Returns "1.5" or "2.0"
	CString getPythonVersion();
	CString getPythonVersionFallback();

	// Copies natlinkXX.dll into natlink.dll
	void copyModules( const char * pythonVersion );
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Developer Studio will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ENABLENLDLG_H__C50695E6_0C4B_11D3_9240_00104B60CF64__INCLUDED_)
