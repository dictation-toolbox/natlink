/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 resobj.h
	Implementation of the CResObj class which encapulates a SAPI result
	and is exposed in Python as a ResObj.
*/

class CDragonCode;
struct CGramObj;

#ifdef INHOUSE
#include "inhouse.h"
#endif

//---------------------------------------------------------------------------
// This is a struct not a class to make sure we are compatibile with Python
// since Python directly access this data structure (using the variables
// defined in the PyObject_HEAD macro).

struct CResObj
{
	// this must be first, it is the Python header data
	PyObject_HEAD

	// these are pointers to the COM grammar object; this is NOT a smart
	// pointer since we can not guarentee the class constructor/destructor
	ISRResBasic * m_pISRResBasic;

	// this is a pointer to the CDragonCode object; we need this to access the
	// shared COM interfaces
	CDragonCode * m_pDragCode;

	// the CDragonCode class keeps a linked list of all results objects
	// which have active interfaces; this is the "next" pointer for that
	// linked list
	CResObj * m_pNextResObj;

	//-----
	// functions

	// we can not count on the constructor being called so this function
	// should be called after the object is created.  Returns TRUE on
	// success and FALSE on failure
	BOOL create( CDragonCode * pDragCode, LPUNKNOWN pIUnknown );

	// we also can not really count on the destructor being called so this
	// function should be called before the object is destroyed
	void destroy();

	// Each of these represents a function called from Python through
	// wrapper code in PythWrap.cpp.  If there is no return value, we
	// return TRUE on success or FALSE on error.  Otherwise, we return
	// a Python object on success or NULL on error.
	PyObject * getResults( int nChoice );
	PyObject * getWords( int nChoice );
	PyObject * correction( PCCHAR * ppWords );
	PyObject * getWave();
	PyObject * getWordInfo( int nChoice );
	PyObject * getSelectInfo( CGramObj * pGrammar, int nChoice );
	
#ifdef INHOUSE
	INH_RESOBJ_CLASS
#endif
};
