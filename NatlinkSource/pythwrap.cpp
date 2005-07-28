/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 PythWrap.cpp
	This file contains the Python wrapper code.  I used the book "Programming
	Python" by Mark Lutz, published by O'Reilly, as the basic reference for
	how to connect Python and C since the Python documentation was not as
	explicit.
*/

#include "stdafx.h"
#include "DragCode.h"
#include "GramObj.h"
#include "ResObj.h"
#include "dictobj.h"
#include "Excepts.h"

#ifdef INHOUSE
#include "inhouse.h"
#endif

// this is the global CDragonCode class
CDragonCode cDragon;

//---------------------------------------------------------------------------
// This utility subroutine takes a PyObject which reprents the arguments
// passed to a Python routine and fills in an array of strings with the
// strings extracted from the Python argument.  The last entry in the array
// will be a NULL pointer.
//
// The caller must delete the array.  This function returns 0 on error (in
// which case the array does not need to be deleted).

PCCHAR * parseStringArray( const char * funcName, PyObject * args )
{
	char szBuffer[256];

	PCCHAR * ppWords = NULL;

	// make sure that we have at least one parameter
	
	int len = PyTuple_Size( args );
	if( len == 0 )
	{
		sprintf( szBuffer, "%s requires at least 1 argument", funcName );
		PyErr_SetString( PyExc_TypeError, szBuffer );
		return NULL;
	}

	// if we are passed exactly one list then we use the contents of that
	// list instead of the passed tuple

	BOOL bList = FALSE;
	
	if( len == 1 )
	{
		PyObject * pFirst = PyTuple_GetItem( args, 0 );
		if( PyList_Check( pFirst ) && PyList_Size( pFirst ) )
		{
			bList = TRUE;
			args = pFirst;
			len = PyList_Size( args );
		}
	}

	// now we extract the strings

	ppWords = new PCCHAR[ len + 1 ];
	ppWords[len] = 0;

	for( int i = 0; i < len; i++ )
	{
		PyObject * pyWord =
			bList ? PyList_GetItem( args, i ) :
					PyTuple_GetItem( args, i );
					
		if( !pyWord || !PyString_Check( pyWord ) )
		{
			sprintf(
				szBuffer, "all arguments passed to %s must be strings",
				funcName );
			PyErr_SetString( PyExc_TypeError, szBuffer );
			delete [] ppWords;
			ppWords = NULL;
			return 0;
		}
		
		ppWords[i] = PyString_AsString( pyWord );
	}

	return ppWords;
}

//---------------------------------------------------------------------------
// This utility subroutine takes a PyObject which should be a list of
// integers or pairs of integers and returns an allocated array of
// integers. will be a NULL pointer.
//
// The caller must delete the array.  This function returns 0 on error (in
// which case the array does not need to be deleted).  If the count is also
// zero then this is not an error but an empty list.

DWORD * parsePlayList(
	const char * funcName, PyObject * pyList, DWORD * pdwCount )
{
	char szBuffer[256];

	// in case of error, we set the count to one because a count of zero
	// means that we have a legal list
	*pdwCount = 1;

	// make sure we get a list

	BOOL bList;

	if( PyTuple_Check( pyList ) )
	{
		bList = FALSE;
	}
	else
	if( PyList_Check( pyList ) )
	{
		bList = TRUE;
	}
	else
	{
		sprintf( szBuffer, "%s requires a play list of integers", funcName );
		PyErr_SetString( PyExc_TypeError, szBuffer );
		return NULL;
	}

	// get the size and allocate an array

	int len = bList ? PyList_Size( pyList ) : PyTuple_Size( pyList );
	if( !len )
	{
		// this is a legal non-error case
		*pdwCount = 0;
		return NULL;
	}

	DWORD * adwList = new DWORD[len*2];

	// now we extract the integers

	for( int i = 0; i < len; i++ )
	{
		PyObject * pyElement =
			bList ? PyList_GetItem( pyList, i ) : PyTuple_GetItem( pyList, i );

		// if the list element is a tuple of two integers then we parse out
		// a range
		
		if( PyTuple_Check( pyElement ) && PyTuple_Size( pyElement ) == 2 )
		{
			PyObject * pyStart = PyTuple_GetItem( pyElement, 0 );
			PyObject * pyEnd = PyTuple_GetItem( pyElement, 1 );
			
			if( !pyStart || !PyInt_Check( pyStart ) ||
				!pyEnd || !PyInt_Check( pyEnd ) )
			{
				sprintf(
					szBuffer,
					"the ranges in the play list passed to %s must contain integers",
					funcName );
				PyErr_SetString( PyExc_TypeError, szBuffer );
				delete [] adwList;
				return 0;
			}
			
			adwList[2*i] = PyInt_AsLong( pyStart );
			adwList[2*i+1] = PyInt_AsLong( pyEnd );

			if( adwList[2*i] > adwList[2*i+1] )
			{
				sprintf(
					szBuffer,
					"end point less than start point in the play list passed to %s",
					funcName );
				PyErr_SetString( PyExc_TypeError, szBuffer );
				delete [] adwList;
				return 0;
			}
			
			continue;
		}

		// otherwise we parse out a single integer
		
		if( !pyElement || !PyInt_Check( pyElement ) )
		{
			sprintf(
				szBuffer, "the play list passed to %s must contain integers",
				funcName );
			PyErr_SetString( PyExc_TypeError, szBuffer );
			delete [] adwList;
			return 0;
		}
		
		adwList[2*i] = adwList[2*i+1] = PyInt_AsLong( pyElement );
	}

	*pdwCount = len;
	return adwList;
}

//---------------------------------------------------------------------------
// natlink.isNatSpeakRunning() from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_isNatSpeakRunning( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	BOOL bRunning = cDragon.isNatSpeakRunning();

	return Py_BuildValue( "i", bRunning );
}

//---------------------------------------------------------------------------
// natlink.natConnect() from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_natConnect( PyObject *self, PyObject *args )
{
	int bUseThreads = FALSE;
	if( !PyArg_ParseTuple( args, "|i:natConnect", &bUseThreads ) )
	{
		return NULL;
	}

	if( !cDragon.natConnect( NULL, bUseThreads!=0 ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.natDisconnect() from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_natDisconnect( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	if( !cDragon.natDisconnect() )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.setBeginCallBack( pCallback ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_setBeginCallback( PyObject *self, PyObject *args )
{
	PyObject *pFunc;
	if( !PyArg_ParseTuple( args, "O:setBeginCallback", &pFunc ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "parameter must be callable" );
		return NULL;        
	}

	if( !cDragon.setBeginCallback( pFunc ) )
	{
		return NULL;
	}
	
	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.setChangeCallBack( pCallback ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_setChangeCallback( PyObject *self, PyObject *args )
{
	PyObject *pFunc;
	if( !PyArg_ParseTuple( args, "O:setChangeCallback", &pFunc ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "parameter must be callable" );
		return NULL;        
	}

	if( !cDragon.setChangeCallback( pFunc ) )
	{
		return NULL;
	}
	
	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.waitForSpeech( timeout ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_waitForSpeech( PyObject *self, PyObject *args )
{
	int nTimeout = 0;
	if( !PyArg_ParseTuple( args, "|i:waitForSpeech", &nTimeout ) )
	{
		return NULL;
	}

	if( !cDragon.waitForSpeech( nTimeout ) )
	{
		return NULL;
	}
		
	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.playString( keys, flags ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_playString( PyObject *self, PyObject *args )
{
	char *pKeys;
	DWORD dwFlags = 0;
	if( !PyArg_ParseTuple( args, "s|i:playString", &pKeys, &dwFlags ) )
	{
		return NULL;
	}

	if( !cDragon.playString( pKeys, dwFlags ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.displayText( text, isError, logText ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_displayText( PyObject *self, PyObject *args )
{
	char *pText;
	int nError;
	int nLogText = 0;
	if( !PyArg_ParseTuple( args, "si|i:displayText", &pText, &nError, &nLogText ) )
	{
		return NULL;
	}

	if( !cDragon.displayText( pText, nError != FALSE, nLogText != FALSE ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.getClipboard()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getClipboard( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getClipboard();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.getCurrentModule()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getCurrentModule( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getCurrentModule();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.getCurrentUser()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getCurrentUser( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getCurrentUser();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.getMicState()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getMicState( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getMicState();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.setMicState()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_setMicState( PyObject *self, PyObject *args )
{
	char * pState;
	if( !PyArg_ParseTuple( args, "s:setMicState", &pState ) )
	{
		return NULL;
	}

	if( !cDragon.setMicState( pState ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.getCallbackDepth()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getCallbackDepth( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getCallbackDepth();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.execScript()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_execScript( PyObject *self, PyObject *args )
{
	char * pScript;
	PyObject * pList = NULL;
	char * pComment = NULL;
	if( !PyArg_ParseTuple( args, "s|Os:execScript", &pScript, &pList, &pComment ) )
	{
		return NULL;
	}

	// if there is a second argument then it should be a list of strings

	PCCHAR * ppWords = NULL;
	
	if( pList )
	{
		if( !PyList_Check( pList ) )
		{
			PyErr_SetString(
				PyExc_TypeError,
				"the second argument to execScript must be a list of words" );
			return NULL;
		}

		int len = PyList_Size( pList );
		ppWords = new PCCHAR[ len + 1 ];
		ppWords[len] = 0;

		for( int i = 0; i < len; i++ )
		{
			PyObject * pyWord = PyList_GetItem( pList, i );

			if( !pyWord || !PyString_Check( pyWord ) )
			{
				PyErr_SetString(
					PyExc_TypeError,
					"the second argument to execScript must be a list of words" );
				delete [] ppWords;
				return NULL;
			}

			ppWords[i] = PyString_AsString( pyWord );
		}
	}

	// here we perfomr the actual work
	
	if( !cDragon.execScript( pScript, ppWords, pComment ) )
	{
		if( ppWords )
		{
			delete [] ppWords;
		}
		return NULL;
	}

	if( ppWords )
	{
		delete [] ppWords;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.recognitionMimic()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_recognitionMimic( PyObject *self, PyObject *args )
{
	PCCHAR * ppWords = parseStringArray( "recognitionMimic", args );
	if( ppWords == NULL )
	{
		return NULL;
	}

	if( !cDragon.recognitionMimic( ppWords ) )
	{
		return NULL;
	}

	delete [] ppWords;
	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.playEvents()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_playEvents( PyObject *self, PyObject *args )
{
	PyObject * pList = NULL;
	if( !PyArg_ParseTuple( args, "O:execScript", &pList ) )
	{
		return NULL;
	}
	
	if( !PyList_Check( pList ) )
	{
		PyErr_SetString(
			PyExc_TypeError,
			"the argument to playEvents must be a list of tuples" );
		return NULL;
	}

	// the argument should be a list of tuples of three integers; we fill in
	// the HOOK_EVENTMSG data structure with the data we parsed from the
	// input.

	DWORD dwCount = PyList_Size( pList );
	HOOK_EVENTMSG * pEvents = new HOOK_EVENTMSG[ dwCount ];

	for( DWORD i = 0; i < dwCount; i++ )
	{
		PyObject * pTuple = PyList_GetItem( pList, i );
		if( !PyTuple_Check( pTuple ) )
		{
			PyErr_SetString(
				PyExc_TypeError,
				"the list passed to playEvents must contain tuples" );
			delete [] pEvents;
			return NULL;
		}

		DWORD message = 0;
		DWORD paramL = 0;
		DWORD paramH = 0;
		if( !PyArg_ParseTuple(
			pTuple, "l|ll:execScript", &message, &paramL, &paramH ) )
		{
			return NULL;
		}

		pEvents[i].message = message;
		pEvents[i].paramL = paramL;
		pEvents[i].paramH = paramH;
	}
	
	// here we perform the actual work

	if( !cDragon.playEvents( dwCount, pEvents ) )
	{
		delete [] pEvents;
		return NULL;
	}

	delete [] pEvents;

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.getCursorPos()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getCursorPos( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getCursorPos();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.getScreenSize()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getScreenSize( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getScreenSize();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.inputFromFile( fileName, realTime, playList )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_inputFromFile( PyObject *self, PyObject *args )
{
	char * pszFileName;
	int bRealTime = 0;
	PyObject * pyList = NULL;
	int nUttDetect = -1;
	if( !PyArg_ParseTuple( args, "s|iOi:inputFromFile",
			&pszFileName, &bRealTime, &pyList, &nUttDetect ) )
	{
		return NULL;
	}

	DWORD dwPlayList = 0;
	DWORD * adwPlayList = NULL;
	if( pyList && pyList!=Py_None )
	{
		adwPlayList = parsePlayList( "inputFromFile", pyList, &dwPlayList );
		if( !adwPlayList && dwPlayList )
		{
			return NULL;
		}
	}
	
	if( !cDragon.inputFromFile(
			pszFileName, bRealTime, dwPlayList, adwPlayList, nUttDetect ) )
	{
		if( adwPlayList ) { delete [] adwPlayList; }
		return NULL;
	}

	if( adwPlayList ) { delete [] adwPlayList; }
	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.setTimerCallback( pCallback, nMilliseconds ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_setTimerCallback( PyObject *self, PyObject *args )
{
	PyObject *pFunc;
	int nMilliseconds = 50;
	if( !PyArg_ParseTuple( args, "O|i:setTimerCallback", &pFunc, &nMilliseconds ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "parameter must be callable" );
		return NULL;        
	}

	if( !cDragon.setTimerCallback( pFunc, nMilliseconds ) )
	{
		return NULL;
	}
	
	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.getTrainingMode()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getTrainingMode( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getTrainingMode();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.startTraining( mode )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_startTraining( PyObject *self, PyObject *args )
{
	char * pMode;
	if( !PyArg_ParseTuple( args, "s:startTraining", &pMode ) )
	{
		return NULL;
	}

	if( !cDragon.startTraining( pMode ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.finishTraining( bProcess )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_finishTraining( PyObject *self, PyObject *args )
{
	int bProcess = 1;
	if( !PyArg_ParseTuple( args, "|i:finishTraining", &bProcess ) )
	{
		return NULL;
	}

	if( !cDragon.finishTraining( bProcess != 0 ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.createUser( userName, baseModel, baseTopic )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_createUser( PyObject *self, PyObject *args )
{
	char * userName;
	char * baseModel = NULL;
	char * baseTopic = NULL;
	if( !PyArg_ParseTuple(
			args, "s|ss:createUser", &userName, &baseModel, &baseTopic ) )
	{
		return NULL;
	}

	if( !cDragon.createUser( userName, baseModel, baseTopic ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.openUser( userName )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_openUser( PyObject *self, PyObject *args )
{
	char * userName;
	if( !PyArg_ParseTuple( args, "s:openUser", &userName ) )
	{
		return NULL;
	}

	if( !cDragon.openUser( userName ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.saveUser()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_saveUser( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	if( !cDragon.saveUser() )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// natlink.getUserTraining()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getUserTraining( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getUserTraining();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.getAllUsers()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getAllUsers( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getAllUsers();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.getWordInfo()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_getWordInfo( PyObject *self, PyObject *args )
{
	char * wordName;
	int flags = 0;
	if( !PyArg_ParseTuple( args, "s|i:getWordInfo", &wordName, &flags ) )
	{
		return NULL;
	}

	PyObject * pRetn = cDragon.getWordInfo( wordName, flags );
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.deleteWord( word )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_deleteWord( PyObject *self, PyObject *args )
{
	char * wordName;
	if( !PyArg_ParseTuple( args, "s:deleteWord", &wordName ) )
	{
		return NULL;
	}

	if( !cDragon.deleteWord( wordName ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// bAdded = natlink.addWord( word, wordInfo )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_addWord( PyObject *self, PyObject *args )
{
	char * wordName;
	DWORD wordInfo = 0x00000001;
	PyObject * pyProns = NULL;
	if( !PyArg_ParseTuple( args, "s|iO:addWord", &wordName, &wordInfo, &pyProns ) )
	{
		return NULL;
	}

	// Decode the pronunciations which is either mussing, a single string or
	// a list of strings.
	
	PCCHAR * ppProns = NULL;
	if( pyProns )
	{
		pyProns = Py_BuildValue( "(O)", pyProns );
		ppProns = parseStringArray( "addWord", pyProns );
		Py_XDECREF( pyProns );
		if( ppProns == NULL )
		{
			return NULL;
		}
	}

	PyObject * pRetn = cDragon.addWord( wordName, wordInfo, ppProns );
	if( ppProns != NULL )
	{
		delete [] ppProns;
	}
	return pRetn;
}

//---------------------------------------------------------------------------
// natlink.setWordInfo( word, info )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_setWordInfo( PyObject *self, PyObject *args )
{
	char * wordName;
	DWORD wordInfo;
	if( !PyArg_ParseTuple( args, "si:setWordInfo", &wordName, &wordInfo ) )
	{
		return NULL;
	}

	if( !cDragon.setWordInfo( wordName, wordInfo ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" PyObject *
natlink_getWordProns( PyObject *self, PyObject *args )
{
	char * wordName;
	if( !PyArg_ParseTuple( args, "s:getWordProns", &wordName ) )
	{
		return NULL;
	}

	return cDragon.getWordProns( wordName );
}

//---------------------------------------------------------------------------
// natlink.setTrayIcon( iconName, toolTip, callback )
//
// See natlink.txt for documentation.

extern "C" static PyObject *
natlink_setTrayIcon( PyObject *self, PyObject *args )
{
	char * iconName = "";
	char * toolTip = "NatLink Python macro system";
	PyObject * pFunc = Py_None;
	
	if( !PyArg_ParseTuple( args, "|ssO:setTrayIcon", &iconName, &toolTip, &pFunc ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "third parameter must be callable" );
		return NULL;        
	}

	if( !cDragon.setTrayIcon( iconName, toolTip, pFunc ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

/////////////////////////////////////////////////////////////////////////////

//---------------------------------------------------------------------------
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_load( PyObject *self, PyObject *args )
{
	char *pData;
	int nData;
	int bAllResults = 0;
	int bHypothesis = 0;
	if( !PyArg_ParseTuple( args, "s#|ii:load", &pData, &nData, &bAllResults, &bHypothesis ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->load( (BYTE *)pData, (DWORD)nData, bAllResults != 0, bHypothesis != 0 ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.unload() from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_unload( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->unload() )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.activate( ruleName, window ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_activate( PyObject *self, PyObject *args )
{
	char *pName;
	HWND hWnd;
	if( !PyArg_ParseTuple( args, "si:activate", &pName, &hWnd ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->activate( pName, hWnd ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.deactivate( ruleName ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_deactivate( PyObject *self, PyObject *args )
{
	char *pName;
	if( !PyArg_ParseTuple( args, "s:deactivate", &pName ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->deactivate( pName ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.setBeginCallback( pCallback ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_setBeginCallback( PyObject *self, PyObject *args )
{
	PyObject *pFunc;
	if( !PyArg_ParseTuple( args, "O:setBeginCallback", &pFunc ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "parameter must be callable" );
		return NULL;        
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->setBeginCallback( pFunc ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.setResultsCallback( pCallback ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_setResultsCallback( PyObject *self, PyObject *args )
{
	PyObject *pFunc;
	if( !PyArg_ParseTuple( args, "O:setResultsCallback", &pFunc ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "parameter must be callable" );
		return NULL;        
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->setResultsCallback( pFunc ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.setHypothesisCallback( pCallback ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_setHypothesisCallback( PyObject *self, PyObject *args )
{
	PyObject *pFunc;
	if( !PyArg_ParseTuple( args, "O:setHypothesisCallback", &pFunc ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "parameter must be callable" );
		return NULL;        
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->setHypothesisCallback( pFunc ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.emptyList( listName ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_emptyList( PyObject *self, PyObject *args )
{
	char * pName;
	if( !PyArg_ParseTuple( args, "s:emptyList", &pName ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->emptyList( pName ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.appendList( listName, word ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_appendList( PyObject *self, PyObject *args )
{
	char *pName;
	char *pWord;
	if( !PyArg_ParseTuple( args, "ss:appendList", &pName, &pWord ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->appendList( pName, pWord ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.setExclusive( state ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_setExclusive( PyObject *self, PyObject *args )
{
	int bState;
	if( !PyArg_ParseTuple( args, "i:setExclusive", &bState ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->setExclusive( bState ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj.setContext( beforeText, afterText ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_setContext( PyObject *self, PyObject *args )
{
	char * beforeText = "";
	char * afterText = "";
	if( !PyArg_ParseTuple( args, "|ss:setContext", &beforeText, &afterText ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->setContext( beforeText, afterText ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj.setSelectText( text ) from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_setSelectText( PyObject *self, PyObject *args )
{
	char * text;
	if( !PyArg_ParseTuple( args, "s:setSelectText", &text ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	if( !pObj->setSelectText( text ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------
// gramObj.getSelectText() from Python
//
// See natlink.txt for documentation.

extern "C" static PyObject *
gramobj_getSelectText( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	CGramObj * pObj = (CGramObj *)self;
	return pObj->getSelectText();
}

//---------------------------------------------------------------------------
// These are the various named methods for a GramObj accessible from Python

static struct PyMethodDef gramobj_methods[] = {
	{ "load", gramobj_load, METH_VARARGS },
	{ "unload", gramobj_unload, METH_VARARGS },
	{ "activate", gramobj_activate, METH_VARARGS },
	{ "deactivate", gramobj_deactivate, METH_VARARGS },
	{ "setBeginCallback", gramobj_setBeginCallback, METH_VARARGS },
	{ "setResultsCallback", gramobj_setResultsCallback, METH_VARARGS },
	{ "setHypothesisCallback", gramobj_setHypothesisCallback, METH_VARARGS },
	{ "emptyList", gramobj_emptyList, METH_VARARGS },
	{ "appendList", gramobj_appendList, METH_VARARGS },
	{ "setExclusive", gramobj_setExclusive, METH_VARARGS },
	{ "setContext", gramobj_setContext, METH_VARARGS },
	{ "setSelectText", gramobj_setSelectText, METH_VARARGS },
	{ "getSelectText", gramobj_getSelectText, METH_VARARGS },
	{ NULL, NULL }
};

//---------------------------------------------------------------------------
// gramObj = natlink.GramObj(); gramObj.XXX from Python
//
// This looks up the function named XXX.

extern "C" static PyObject *
gramobj_getattr( PyObject *self, char *name )
{
	return Py_FindMethod( gramobj_methods, self, name );
}

//---------------------------------------------------------------------------
// Called from Python when the reference count on a GramObj reaches zero.
//
// We tell the object to cleanup since we can never be sure that the
// destructor will be properly called from PyMem_DEL.

extern "C" static void
gramobj_dealloc(PyObject *self)
{
	CGramObj * pObj = (CGramObj *)self;
	pObj->destroy();
	
	PyMem_DEL( self );
}

//---------------------------------------------------------------------------
// This datastructure tells Python which methods for a new class (GramObj in
// this casze) are defined.  We actually define very few methods since we
// are not creating a number or sequence-type object.

static PyTypeObject gramobj_stackType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,						// ob_size
	"GramObj",				// tp_name
	sizeof(CGramObj),		// tp_basicsize
	0,						// tp_itemsize
	gramobj_dealloc,		// tp_dealloc
	0,						// tp_print
	gramobj_getattr,		// tp_getattr
	0,						// tp_setattr
	0,						// tp_compare
	0,						// tp_repr
	0,						// tp_as_number
	0,						// tp_as_sequence
	0,						// tp_as_mapping
	
	// remainder of fields are NULL
};

//---------------------------------------------------------------------------
// gramObj = GramObj() from Python
//
// This function is called when we create a new GramObj instance.  We have
// to call CGramObj::create to initialize the object since we can not rely
// on the constructor being called.

extern "C" PyObject *
gramobj_new( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	CGramObj * pObj = PyObject_NEW( CGramObj, &gramobj_stackType );
	if( pObj == NULL )
	{
		return NULL;
	}

	pObj->create( &cDragon );
	return (PyObject *)pObj;
}

/////////////////////////////////////////////////////////////////////////////

//---------------------------------------------------------------------------
// ResObj.getResults()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
resobj_getResults( PyObject *self, PyObject *args )
{
	int nChoice;
	if( !PyArg_ParseTuple( args, "|i:getResults", &nChoice ) )
	{
		return NULL;
	}

	CResObj * pObj = (CResObj *)self;
	PyObject * pRetn = pObj->getResults( nChoice );
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// ResObj.getWords()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
resobj_getWords( PyObject *self, PyObject *args )
{
	int nChoice;
	if( !PyArg_ParseTuple( args, "|i:getWords", &nChoice ) )
	{
		return NULL;
	}

	CResObj * pObj = (CResObj *)self;
	PyObject * pRetn = pObj->getWords( nChoice );
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// ResObj.correction()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
resobj_correction( PyObject *self, PyObject *args )
{
	PCCHAR * ppWords = parseStringArray( "correction", args );
	if( ppWords == NULL )
	{
		return NULL;
	}

	CResObj * pObj = (CResObj *)self;
	PyObject * pRetn = pObj->correction( ppWords );
	if( pRetn == NULL )
	{
		return NULL;
	}

	delete [] ppWords;
	return pRetn;
}

//---------------------------------------------------------------------------
// ResObj.getWords()
//
// See natlink.txt for documentation.

extern "C" static PyObject *
resobj_getWave( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	CResObj * pObj = (CResObj *)self;
	PyObject * pRetn = pObj->getWave();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------

extern "C" PyObject *
resobj_getWordInfo( PyObject *self, PyObject *args )
{
	int nChoice = 0;
	if( !PyArg_ParseTuple( args, "|i:getWordInfo", &nChoice ) )
	{
		return NULL;
	}

	CResObj * pObj = (CResObj *)self;
	return pObj->getWordInfo( nChoice );
}

//---------------------------------------------------------------------------

extern "C" PyObject *
resobj_getSelectInfo( PyObject *self, PyObject *args )
{
	PyObject * pGrammar;
	int nChoice = 0;
	if( !PyArg_ParseTuple( args, "O|i:getSelectInfo", &pGrammar, &nChoice ) )
	{
		return NULL;
	}

	// this code makes sure that the first parameter is a GramObj class
	PyObject * pyName = NULL;
	PyObject * pyType = PyObject_Type(pGrammar);
	if( pyType != NULL )
	{
		PyObject * strName = Py_BuildValue( "s", "__name__" );
		pyName = PyObject_GetAttr( pyType, strName );
		Py_XDECREF( strName );
	}
	if( pyName == NULL || !PyString_Check( pyName ) ||
		0 != strcmp( PyString_AsString( pyName ), "GramObj" ) )
	{
		PyErr_SetString( PyExc_TypeError, "first parameter must be a GramObj instance" );
		return NULL;
	}
	
	CResObj * pObj = (CResObj *)self;
	return pObj->getSelectInfo( (CGramObj *)pGrammar, nChoice );
}

//---------------------------------------------------------------------------
// These are the various named methods for a ResObj accessible from Python

static struct PyMethodDef resobj_methods[] = {
	{ "getResults", resobj_getResults, METH_VARARGS },
	{ "getWords", resobj_getWords, METH_VARARGS },
	{ "correction", resobj_correction, METH_VARARGS },
	{ "getWave", resobj_getWave, METH_VARARGS },
	{ "getWordInfo", resobj_getWordInfo, METH_VARARGS },
	{ "getSelectInfo", resobj_getSelectInfo, METH_VARARGS },
#ifdef INHOUSE
	INH_RESOBJ_METHODS
#endif
	{ NULL, NULL }
};

//---------------------------------------------------------------------------
// resObj = natlink.ResObj(); resObj.XXX from Python
//
// This looks up the function named XXX.

extern "C" static PyObject *
resobj_getattr( PyObject *self, char *name )
{
	return Py_FindMethod( resobj_methods, self, name );
}

//---------------------------------------------------------------------------
// Called from Python when the reference count on a ResObj reaches zero.
//
// We tell the object to cleanup since we can never be sure that the
// destructor will be properly called from PyMem_DEL.

extern "C" static void
resobj_dealloc(PyObject *self)
{
	CResObj * pObj = (CResObj *)self;
	pObj->destroy();
	
	PyMem_DEL( self );
}

//---------------------------------------------------------------------------
// This datastructure tells Python which methods for a new class (ResObj in
// this casze) are defined.  We actually define very few methods since we
// are not creating a number or sequence-type object.

static PyTypeObject resobj_stackType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,						// ob_size
	"ResObj",				// tp_name
	sizeof(CResObj),		// tp_basicsize
	0,						// tp_itemsize
	resobj_dealloc,			// tp_dealloc
	0,						// tp_print
	resobj_getattr,			// tp_getattr
	0,						// tp_setattr
	0,						// tp_compare
	0,						// tp_repr
	0,						// tp_as_number
	0,						// tp_as_sequence
	0,						// tp_as_mapping
	
	// remainder of fields are NULL
};

//---------------------------------------------------------------------------
// Create a new ResObj.  This is not called from Python.  Instead it is
// called from GramObj.cpp

CResObj * resobj_new()
{
	return PyObject_NEW( CResObj, &resobj_stackType );
}

/////////////////////////////////////////////////////////////////////////////

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_activate( PyObject *self, PyObject *args )
{
	HWND hWnd;
	if( !PyArg_ParseTuple( args, "i:activate", &hWnd ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	if( !pObj->activate( hWnd ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_deactivate( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, ":deactivate" ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	if( !pObj->deactivate() )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_setBeginCallback( PyObject *self, PyObject *args )
{
	PyObject * pFunc;
	if( !PyArg_ParseTuple( args, "O:setBeginCallback", &pFunc ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "parameter must be callable" );
		return NULL;        
	}

	CDictObj * pObj = (CDictObj *)self;
	if( !pObj->setBeginCallback( pFunc ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_setChangeCallback( PyObject *self, PyObject *args )
{
	PyObject * pFunc;
	if( !PyArg_ParseTuple( args, "O:setChangeCallback", &pFunc ) )
	{
		return NULL;
	}

	if( pFunc != Py_None && !PyCallable_Check( pFunc ) )
	{
		PyErr_SetString( PyExc_TypeError, "parameter must be callable" );
		return NULL;        
	}

	CDictObj * pObj = (CDictObj *)self;
	if( !pObj->setChangeCallback( pFunc ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_setLock( PyObject *self, PyObject *args )
{
	int nState;
	if( !PyArg_ParseTuple( args, "i:setLock", &nState ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	if( !pObj->setLock( nState != 0 ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_setText( PyObject *self, PyObject *args )
{
	int nStart;
	int nEnd = 0x7FFFFFFF;
	char * pText;
	if( !PyArg_ParseTuple( args, "si|i:setText", &pText, &nStart, &nEnd ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	if( !pObj->setText( pText, nStart, nEnd ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_setTextSel( PyObject *self, PyObject *args )
{
	int nStart;
	int nEnd = 0x7FFFFFFF;
	if( !PyArg_ParseTuple( args, "i|i:setTextSel", &nStart, &nEnd ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	if( !pObj->setTextSel( nStart, nEnd ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_setVisibleText( PyObject *self, PyObject *args )
{
	int nStart;
	int nEnd = 0x7FFFFFFF;
	if( !PyArg_ParseTuple( args, "i|i:setVisibleText", &nStart, &nEnd ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	if( !pObj->setVisibleText( nStart, nEnd ) )
	{
		return NULL;
	}

	Py_INCREF( Py_None );
	return Py_None;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_getLength( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, ":getLength" ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	PyObject * pRetn = pObj->getLength();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_getText( PyObject *self, PyObject *args )
{
	int nStart;
	int nEnd = 0x7FFFFFFF;
	if( !PyArg_ParseTuple( args, "i|i:getText", &nStart, &nEnd ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	PyObject * pRetn = pObj->getText( nStart, nEnd );
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_getTextSel( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, ":getTextSel" ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	PyObject * pRetn = pObj->getTextSel();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------

extern "C" static PyObject *
dictobj_getVisibleText( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, ":getVisibleText" ) )
	{
		return NULL;
	}

	CDictObj * pObj = (CDictObj *)self;
	PyObject * pRetn = pObj->getVisibleText();
	if( pRetn == NULL )
	{
		return NULL;
	}

	return pRetn;
}

//---------------------------------------------------------------------------
// These are the various named methods for a DictObj accessible from Python

static struct PyMethodDef dictobj_methods[] = {
	{ "activate", dictobj_activate, METH_VARARGS },
	{ "deactivate", dictobj_deactivate, METH_VARARGS },
	{ "setBeginCallback", dictobj_setBeginCallback, METH_VARARGS },
	{ "setChangeCallback", dictobj_setChangeCallback, METH_VARARGS },
	{ "setLock", dictobj_setLock, METH_VARARGS },
	{ "setText", dictobj_setText, METH_VARARGS },
	{ "setTextSel", dictobj_setTextSel, METH_VARARGS },
	{ "setVisibleText", dictobj_setVisibleText, METH_VARARGS },
	{ "getLength", dictobj_getLength, METH_VARARGS },
	{ "getText", dictobj_getText, METH_VARARGS },
	{ "getTextSel", dictobj_getTextSel, METH_VARARGS },
	{ "getVisibleText", dictobj_getVisibleText, METH_VARARGS },
	{ NULL, NULL }
};

//---------------------------------------------------------------------------
// dictObj = natlink.DictObj(); dictObj.XXX from Python
//
// This looks up the function named XXX.

extern "C" static PyObject *
dictobj_getattr( PyObject *self, char *name )
{
	return Py_FindMethod( dictobj_methods, self, name );
}

//---------------------------------------------------------------------------
// Called from Python when the reference count on a DictObj reaches zero.
//
// We tell the object to cleanup since we can never be sure that the
// destructor will be properly called from PyMem_DEL.

extern "C" static void
dictobj_dealloc(PyObject *self)
{
	CDictObj * pObj = (CDictObj *)self;
	pObj->destroy();
	
	PyMem_DEL( self );
}

//---------------------------------------------------------------------------
// This datastructure tells Python which methods for a new class (DictObj in
// this casze) are defined.  We actually define very few methods since we
// are not creating a number or sequence-type object.

static PyTypeObject dictobj_stackType = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,						// ob_size
	"DictObj",				// tp_name
	sizeof(CDictObj),		// tp_basicsize
	0,						// tp_itemsize
	dictobj_dealloc,		// tp_dealloc
	0,						// tp_print
	dictobj_getattr,		// tp_getattr
	0,						// tp_setattr
	0,						// tp_compare
	0,						// tp_repr
	0,						// tp_as_number
	0,						// tp_as_sequence
	0,						// tp_as_mapping
	
	// remainder of fields are NULL
};

//---------------------------------------------------------------------------
// dictObj = DictObj() from Python
//
// This function is called when we create a new DictObj instance.  We have
// to call CDictObj::create to initialize the object since we can not rely
// on the constructor being called.

extern "C" PyObject *
dictobj_new( PyObject *self, PyObject *args )
{
	if( !PyArg_ParseTuple( args, "" ) )
	{
		return NULL;
	}

	CDictObj * pObj = PyObject_NEW( CDictObj, &dictobj_stackType );
	if( pObj == NULL )
	{
		return NULL;
	}

	if( !pObj->create( &cDragon ) )
	{
		pObj->destroy();
		PyMem_DEL( self );
		return NULL;
	}
	
	return (PyObject *)pObj;
}

/////////////////////////////////////////////////////////////////////////////

//---------------------------------------------------------------------------
// These are the Python functions visible in this module.

static struct PyMethodDef natlink_methods[] = {
	{ "isNatSpeakRunning", natlink_isNatSpeakRunning, METH_VARARGS },
	{ "natConnect", natlink_natConnect, METH_VARARGS },
	{ "natDisconnect", natlink_natDisconnect, METH_VARARGS },
	{ "setBeginCallback", natlink_setBeginCallback, METH_VARARGS },
	{ "waitForSpeech", natlink_waitForSpeech, METH_VARARGS },
	{ "playString", natlink_playString, METH_VARARGS },
	{ "displayText", natlink_displayText, METH_VARARGS },
	{ "getClipboard", natlink_getClipboard, METH_VARARGS },
	{ "getCurrentModule", natlink_getCurrentModule, METH_VARARGS },
	{ "getCurrentUser", natlink_getCurrentUser, METH_VARARGS },
	{ "setChangeCallback", natlink_setChangeCallback, METH_VARARGS },
	{ "getMicState", natlink_getMicState, METH_VARARGS },
	{ "setMicState", natlink_setMicState, METH_VARARGS },
	{ "getCallbackDepth", natlink_getCallbackDepth, METH_VARARGS },
	{ "execScript", natlink_execScript, METH_VARARGS },
	{ "recognitionMimic", natlink_recognitionMimic, METH_VARARGS },
	{ "playEvents", natlink_playEvents, METH_VARARGS },
	{ "getCursorPos", natlink_getCursorPos, METH_VARARGS },
	{ "getScreenSize", natlink_getScreenSize, METH_VARARGS },
	{ "inputFromFile", natlink_inputFromFile, METH_VARARGS },
	{ "setTimerCallback", natlink_setTimerCallback, METH_VARARGS },
	{ "getTrainingMode", natlink_getTrainingMode, METH_VARARGS },
	{ "startTraining", natlink_startTraining, METH_VARARGS },
	{ "finishTraining", natlink_finishTraining, METH_VARARGS },
	{ "createUser", natlink_createUser, METH_VARARGS },
	{ "openUser", natlink_openUser, METH_VARARGS },
	{ "saveUser", natlink_saveUser, METH_VARARGS },
	{ "getUserTraining", natlink_getUserTraining, METH_VARARGS },
	{ "getAllUsers", natlink_getAllUsers, METH_VARARGS },
	{ "getWordInfo", natlink_getWordInfo, METH_VARARGS },
	{ "deleteWord", natlink_deleteWord, METH_VARARGS },
	{ "addWord", natlink_addWord, METH_VARARGS },
	{ "setWordInfo", natlink_setWordInfo, METH_VARARGS },
	{ "getWordProns", natlink_getWordProns, METH_VARARGS },
	{ "setTrayIcon", natlink_setTrayIcon, METH_VARARGS },
	{ "GramObj", gramobj_new, METH_VARARGS },
	{ "DictObj", dictobj_new, METH_VARARGS },
#ifdef INHOUSE
	INH_NATLINK_METHODS
#endif
	{ NULL, NULL }
};

//---------------------------------------------------------------------------
// import natlink from Python
//
// We tell Python about our functions and also create an error type.

extern "C"
void initnatlink()
{
	PyObject *pMod;

	CoInitialize( NULL );

	pMod = Py_InitModule( "natlink", natlink_methods );
	initExceptions( pMod );

	if( PyErr_Occurred() )
	{
		Py_FatalError( "Can't initialize natlink module" );
	}
}

//---------------------------------------------------------------------------
// This is our internal Python initialization function

CDragonCode * initModule()
{
	initnatlink();
	return &cDragon;
}
