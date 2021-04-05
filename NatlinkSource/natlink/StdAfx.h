/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 stdafx.h
	Include file for standard system include files, or project specific
	include files that are used frequently, but are changed infrequently.
*/
//#define _CRT_SECURE_NO_WARNINGS
#pragma once

// Dragon 12 switched to unicode
#if DRAGON_VERSION >= 12
#define UNICODE
#endif

#define STRICT
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500

//#define _WIN32_WINNT 0x0403
#define _ATL_APARTMENT_THREADED


//You may derive a class from CComModule and use it if you want to override
//something, but do not change the name of _Module
#include <atlbase.h>
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

#include "COM/speech.h"
#include "COM/dspeech.h"
#include "COM/comsupp.h"

