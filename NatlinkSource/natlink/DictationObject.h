/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 dictovh.h
	This file contains the dictation object functions which can be called
	from Python. These functions are referenced but not defined in the
	PythWrap.cpp
*/

class CDragonCode;

//---------------------------------------------------------------------------
// This is a struct not a class to make sure we are compatibile with Python
// since Python directly access this data structure (using the variables
// defined in the PyObject_HEAD macro).

struct CDictationObject
{
	// this must be first, it is the Python header data
	PyObject_HEAD

	// this is a pointer to the function set with setBeginCallback; it is
	// NULL to avoid any callback
	PyObject *m_pBeginCallback;

	// this is a pointer to the function set with setChangeCallback; it is
	// NULL to avoid any callback
	PyObject *m_pChangeCallback;

	// this is a pointer to the VDct main object, this is not a smart
	// pointer since we can not guarentee the class constructor/destructor
	IVoiceDictation0 * m_pIVoiceDictation;
	IVDct0Text * m_pIVDctText;

	// this is a pointer to the CDragonCode object; we need this to access the
	// shared COM interfaces
	CDragonCode * m_pDragCode;

	// the CDragonCode class keeps a linked list of all grammar objects
	// which have active interfaces; this is the "next" pointer for that
	// linked list
	CDictationObject * m_pNextDictObj;

	// to make it easier to deal with the locking from Python, we keep an
	// internal copy of the lock count
	int m_nLockCount;

	//-----
	// functions

	// we can not count on the constructor being called so this function
	// should be called after the object is created
	BOOL create( CDragonCode * pDragCode );

	// we also can not really count on the destructor being called so this
	// function should be called before the object is destroyed
	void destroy();

	// Each of these represents a function called from Python through
	// wrapper code in PythWrap.cpp.  If there is no return value, we
	// return TRUE on success or FALSE on error.  Otherwise, we return
	// a Python object on success or NULL on error.
	BOOL activate( HWND hWnd );
	BOOL deactivate();
	BOOL setBeginCallback( PyObject * pCallback );
	BOOL setChangeCallback( PyObject * pCallback );
	BOOL setLock( BOOL bState );
	BOOL setText( const char * pText, int nStart, int nEnd );
	BOOL setTextSel( int nStart, int nEnd );
	BOOL setVisibleText( int nStart, int nEnd );

	PyObject * getLength();
	PyObject * getText( int nStart, int nEnd );
	PyObject * getTextSel();
	PyObject * getVisibleText();

	// callbacks from the dictation notify sinks (return value is ignored,
	// we only return something to make it easy to trap errors)
	BOOL TextChanged( DWORD dwReason );
	BOOL TextSelChanged();
	BOOL JITPause();

	// this is an internal function which returns the buffer length
	BOOL computeLength( int & nCount );

	// this is an internal function which converst passed start, end
	// parameters into a start, length
	BOOL computeRange( int & nStart, int & nEndCount );
};
