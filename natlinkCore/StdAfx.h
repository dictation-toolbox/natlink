#pragma once

#define WIN32_LEAN_AND_MEAN //Exclude rarely-used stuff from 
                                        // Windows headers

//#define USE_MANWRAP_DLL
#undef USE_MANWRAP_DLL
#ifdef USE_MANWRAP_DLL
#include <atlstr.h>
#define CAtlString CString
#endif

#include <windows.h>
#include <shellapi.h>
//#define AFX_STDAFX_H__9A6ACE74_B9DB_11D2_B031_0060088DC929__INCLUDED_
//#define _ATL_APARTMENT_THREADED

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


