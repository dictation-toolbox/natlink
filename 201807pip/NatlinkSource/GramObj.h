/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 gramobj.h
	This file contains the grammar object functions which can be called from
	Python. These functions are referenced but not defined in the
	PythWrap.cpp
*/

class CDragonCode;

//---------------------------------------------------------------------------
// This is a struct not a class to make sure we are compatibile with Python
// since Python directly access this data structure (using the variables
// defined in the PyObject_HEAD macro).

struct CGramObj
{
	// this must be first, it is the Python header data
	PyObject_HEAD

	// this is a pointer to the function set with setBeginCallback; it is
	// NULL to avoid any callback
	PyObject *m_pBeginCallback;

	// this is a pointer to the function set with setResultsCallback; it is
	// NULL to avoid any callback
	PyObject *m_pResultsCallback;

	// this is a pointer to the function set with setHypothesisCallback; it
	// is NULL to avoid any callback
	PyObject *m_pHypothesisCallback;

	// this flag corresponds to the value of the allResults flag passes to
	// the load function.  When set we return results in the results
	// callback when when they correspond to other grammars or rejections
	BOOL m_bAllResults;

	// these are pointers to the COM grammar object; this is NOT a smart
	// pointer since we can not guarentee the class constructor/destructor
	ISRGramCommon * m_pISRGramCommon;

	// this is a pointer to the CDragonCode object; we need this to access the
	// shared COM interfaces
	CDragonCode * m_pDragCode;

	// the CDragonCode class keeps a linked list of all grammar objects
	// which have active interfaces; this is the "next" pointer for that
	// linked list
	CGramObj * m_pNextGramObj;

	//-----
	// functions
	
	// we can not count on the constructor being called so this function
	// should be called after the object is created
	void create( CDragonCode * pDragCode );

	// we also can not really count on the destructor being called so this
	// function should be called before the object is destroyed
	void destroy();

	// Each of these represents a function called from Python through
	// wrapper code in PythWrap.cpp.  If there is no return value, we
	// return TRUE on success or FALSE on error.  Otherwise, we return
	// a Python object on success or NULL on error.
	BOOL load( BYTE * pData, DWORD dwSize, BOOL bAllResults, BOOL bHypothesis );
	BOOL unload();
	BOOL setBeginCallback( PyObject *pCallback );
	BOOL setResultsCallback( PyObject *pCallback );
	BOOL setHypothesisCallback( PyObject *pCallback );
	BOOL activate( char * ruleName, HWND hWnd );
	BOOL deactivate( char * ruleName );
	BOOL emptyList( char * listName );
	BOOL appendList( char * listName, char * word );
	BOOL setExclusive( BOOL bState );
	BOOL setContext( char * beforeText, char * afterText );
	BOOL setSelectText( char * text );
	BOOL changeSelectText( char * text, int start, int end );
	
	PyObject * getSelectText();

	// callback from the grammar notify sink
	BOOL PhraseFinish(
		DWORD dwFlags, PSRPHRASE pSRPhrase, LPUNKNOWN pIUnknown );
	BOOL PhraseHypothesis(
		DWORD dwFlags, PSRPHRASE pSRPhrase );

	// This is called from the result object to get the GUID for this
	// grammar.  It will return FALSE in the case of an error which
	// is already reported to Python.
	BOOL getGrammarGuid( GUID * pGrammarGuid );
};
