/*----------------------------------------------------------------------
   John Robbins - Feb '99 Microsoft Systems Journal Bugslayer Column
------------------------------------------------------------------------
Plays some keys!
----------------------------------------------------------------------*/

#include "stdafx.h"
#include "PlayKeys.h"
#include "ParsePlayKeysString.h"

/*//////////////////////////////////////////////////////////////////////
                    File Scope Constants and Defines
//////////////////////////////////////////////////////////////////////*/

/*//////////////////////////////////////////////////////////////////////
                            File Scope Types
//////////////////////////////////////////////////////////////////////*/
// The SendInput prototype.
/*//////////////////////////////////////////////////////////////////////
                           File Scope Globals
//////////////////////////////////////////////////////////////////////*/
/*//////////////////////////////////////////////////////////////////////
                         File Scope Prototypes
//////////////////////////////////////////////////////////////////////*/

/*//////////////////////////////////////////////////////////////////////
                      Implementation starts here.
//////////////////////////////////////////////////////////////////////*/

// See PlayKeys.h
UINT PlayKeys ( LPCTSTR szString  ,
                                                 LPUINT  puiErrPos  )
{
    // Do the usual parameter validation happiness.
    ASSERT ( FALSE == IsBadStringPtr ( szString , 2000 ) ) ;
    ASSERT ( FALSE == IsBadWritePtr ( puiErrPos , sizeof ( UINT ) ) ) ;
    if ( ( NULL == szString                                       ) ||
         ( TRUE == IsBadWritePtr ( puiErrPos , sizeof ( UINT ) ) )   )
    {
        SetLastError ( ERROR_INVALID_PARAMETER ) ;
        return ( PK_INVALIDPARAMS ) ;
    }

    // Do I need to GetProcAddress SendInput?

    // The variables filled in by ParsePlayKeys.
    PINPUT pRetKeys = NULL ;
    UINT   uiCount  = 0 ;
    UINT   uiRet    = PK_SUCCESS ;

    __try
    {
        // Let ParsePlayKeysString have a crack at it.
        uiRet = ParsePlayKeysString ( szString   ,
                                      *puiErrPos ,
                                      pRetKeys   ,
                                      uiCount     ) ;
        if ( uiRet == PK_SUCCESS )
        {
            ASSERT ( NULL != pRetKeys ) ;
            ASSERT ( 0 != uiCount ) ;
            ASSERT ( FALSE ==
                     IsBadReadPtr ( pRetKeys , sizeof(INPUT)*uiCount)) ;

            // It is time to play.
            for (UINT k = 0; k < uiCount; ++k)
            {
                keybd_event((BYTE)pRetKeys[k].ki.wVk, (BYTE)pRetKeys[k].ki.wScan, pRetKeys[k].ki.dwFlags, pRetKeys[k].ki.dwExtraInfo);
            }

            // Get rid of the memory allocated in ParsePlayKeysString.
            delete [] pRetKeys ;
        }
    }
    __except ( EXCEPTION_EXECUTE_HANDLER )
    {
        // Surely not good.
        SUPERASSERT ( FALSE ) ;
        uiRet = PK_CRASH ;
    }

    return ( uiRet ) ;
}

