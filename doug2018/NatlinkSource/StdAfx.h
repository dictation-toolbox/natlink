/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 stdafx.h
	Include file for standard system include files, or project specific
	include files that are used frequently, but are changed infrequently.
*/

#if !defined(AFX_STDAFX_H__9A6ACE74_B9DB_11D2_B031_0060088DC929__INCLUDED_)
#define AFX_STDAFX_H__9A6ACE74_B9DB_11D2_B031_0060088DC929__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

#define STRICT

#define _WIN32_WINNT 0x0400
#define _ATL_APARTMENT_THREADED

#include <atlbase.h>
//You may derive a class from CComModule and use it if you want to override
//something, but do not change the name of _Module
extern CComModule _Module;
#include <atlcom.h>
#include <comdef.h>

// We always want the release version of Python even if we are building the
// debug version of our own code
#ifdef  _DEBUG
#define WAS_DEBUG
#undef  _DEBUG
#endif
#include <Python.h>
#ifdef  WAS_DEBUG
#define _DEBUG
#endif

#include <stdio.h>
#include <assert.h>

#include "speech.h"
#include "dspeech.h"
#include "comsupp.h"

//{{AFX_INSERT_LOCATION}}
// Microsoft Developer Studio will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_STDAFX_H__9A6ACE74_B9DB_11D2_B031_0060088DC929__INCLUDED)
