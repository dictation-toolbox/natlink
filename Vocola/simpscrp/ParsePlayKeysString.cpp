/*----------------------------------------------------------------------
   John Robbins - Feb '99 Microsoft Systems Journal Bugslayer Column
------------------------------------------------------------------------
The core code that processes a string passed to PlayKeys

I tried to make this ready for internationalization, but I have not
tested this with different keyboard layouts.  If you find that it is not
ready, I would appreciate if you would let me know!
----------------------------------------------------------------------*/

#include "stdafx.h"
#include <stdlib.h>
#include "SendInput.h"
#include "ParsePlayKeysString.h"

/*//////////////////////////////////////////////////////////////////////
                    File Scope Constants and Defines
//////////////////////////////////////////////////////////////////////*/
// The following flags indicate the current special key state.  These
//  are used in ProcessString and AddOEMChar.
#define k_STATE_CTRLDOWN        0x01
#define k_STATE_SHIFTDOWN       0x02
#define k_STATE_ALTDOWN         0x04

// Some helpful macros.
#define ISSTATECTRLDOWN(x) (k_STATE_CTRLDOWN == (k_STATE_CTRLDOWN & x))
#define ISSTATESHIFTDOWN(x)(k_STATE_SHIFTDOWN == (k_STATE_SHIFTDOWN&x))
#define ISSTATEALTDOWN(x)  (k_STATE_ALTDOWN == (k_STATE_ALTDOWN & x))

#define SETCTRLDOWNSTATE(x) (x |= k_STATE_CTRLDOWN)
#define SETSHIFTDOWNSTATE(x) (x |= k_STATE_SHIFTDOWN)
#define SETALTDOWNSTATE(x) (x |= k_STATE_ALTDOWN)

// A wrapper around MapVirtualKey.  The problem is that the input
//  structure defines scan codes as WORDs and MapVirtualKey returns them
//  as UINTS.
#define MVK_TO_SC(ch) ((WORD)MapVirtualKey(ch,0))

// The SEH exception that I will raise if there is a problem parsing.
//  I don't really use any objects in this file and since I don't want
//  to force whoever uses this file to mess with the synchronous
//  exception settings, I just use trusty SEH.
#define STATUS_PARSE_ERROR  0xE0000001

/*//////////////////////////////////////////////////////////////////////
                         File Scope Structures
//////////////////////////////////////////////////////////////////////*/
// The structure that defines the lookup table used to find the special
//  codes inside braces.  If the scan code is not zero, then the
//  character is converted with AddOEMChar.
typedef struct tag_BRACECODE
{
    LPCTSTR szString ;
    WORD    wVK      ;
    WORD    wScan    ;
} BRACECODE , * PBRACECODE ;

/*//////////////////////////////////////////////////////////////////////
                           File Scope Globals
//////////////////////////////////////////////////////////////////////*/
// The total size of the current buffer.
static UINT g_uiBuffSize = 20 ;
static UINT g_uiNextBuffSize = 20 * 2 ;

// The current buffer of converted keystrokes.
static PINPUT g_pRetKeys = NULL ;
// The current position in the g_pRetKeys array.
static UINT g_uiCount = 0 ;

// The special codes that appear inside braces.
static BRACECODE g_stParenCode[] =
{
    { _T ( "%" )          , 0           , _T ( '%' ) } ,
    { _T ( "(" )          , 0           , _T ( '(' ) } ,
    { _T ( ")" )          , 0           , _T ( ')' ) } ,
    { _T ( "+" )          , 0           , _T ( '+' ) } ,
    { _T ( "APPS" )       , VK_APPS     , 0          } ,
    { _T ( "BACKSPACE" )  , VK_BACK     , 0          } ,
    { _T ( "BKSP" )       , VK_BACK     , 0          } ,
    { _T ( "BREAK" )      , VK_PAUSE    , 0          } ,
    { _T ( "BS" )         , VK_BACK     , 0          } ,
    { _T ( "CAPSLOCK" )   , VK_CAPITAL  , 0          } ,
    { _T ( "DEL" )        , VK_DELETE   , 0          } ,
    { _T ( "DELETE" )     , VK_DELETE   , 0          } ,
    { _T ( "DOWN" )       , VK_DOWN     , 0          } ,
    { _T ( "END" )        , VK_END      , 0          } ,
    { _T ( "ENTER" )      , VK_RETURN   , 0          } ,
    { _T ( "ESC" )        , VK_ESCAPE   , 0          } ,
    { _T ( "F1" )         , VK_F1       , 0          } ,
    { _T ( "F10" )        , VK_F10      , 0          } ,
    { _T ( "F11" )        , VK_F11      , 0          } ,
    { _T ( "F12" )        , VK_F12      , 0          } ,
    { _T ( "F13" )        , VK_F13      , 0          } ,
    { _T ( "F14" )        , VK_F14      , 0          } ,
    { _T ( "F15" )        , VK_F15      , 0          } ,
    { _T ( "F16" )        , VK_F16      , 0          } ,
    { _T ( "F2" )         , VK_F2       , 0          } ,
    { _T ( "F3" )         , VK_F3       , 0          } ,
    { _T ( "F4" )         , VK_F4       , 0          } ,
    { _T ( "F5" )         , VK_F5       , 0          } ,
    { _T ( "F6" )         , VK_F6       , 0          } ,
    { _T ( "F7" )         , VK_F7       , 0          } ,
    { _T ( "F8" )         , VK_F8       , 0          } ,
    { _T ( "F9" )         , VK_F9       , 0          } ,
    { _T ( "HELP" )       , VK_HELP     , 0          } ,
    { _T ( "HOME" )       , VK_HOME     , 0          } ,
    { _T ( "INS" )        , VK_INSERT   , 0          } ,
    { _T ( "INSERT" )     , VK_INSERT   , 0          } ,
    { _T ( "LEFT" )       , VK_LEFT     , 0          } ,
    { _T ( "LWIN" )       , VK_LWIN     , 0          } ,
    { _T ( "NUMLOCK" )    , VK_NUMLOCK  , 0          } ,
    { _T ( "PGDN" )       , VK_NEXT     , 0          } ,
    { _T ( "PGUP" )       , VK_PRIOR    , 0          } ,
    { _T ( "PRTSC" )      , VK_SNAPSHOT , 0          } ,
    { _T ( "RIGHT" )      , VK_RIGHT    , 0          } ,
    { _T ( "RWIN" )       , VK_RWIN     , 0          } ,
    { _T ( "SCROLLLOCK" ) , VK_SCROLL   , 0          } ,
    { _T ( "TAB" )        , VK_TAB      , 0          } ,
    { _T ( "UP" )         , VK_UP       , 0          } ,
    { _T ( "[" )          , 0           , _T ( '[' ) } ,
    { _T ( "]" )          , 0           , _T ( ']' ) } ,
    { _T ( "^" )          , 0           , _T ( '^' ) } ,
    { _T ( "{" )          , 0           , _T ( '{' ) } ,
    { _T ( "}" )          , 0           , _T ( '}' ) } ,
    { _T ( "~" )          , 0           , _T ( '~' ) }
} ;

#define BRACECODE_COUNT (sizeof ( g_stParenCode ) / sizeof ( BRACECODE))

/*//////////////////////////////////////////////////////////////////////
                         File Scope Prototypes
//////////////////////////////////////////////////////////////////////*/
// Allocates a INPUT array.  This function keeps doubling the memory
//  for the array each time it is called.
static PINPUT AllocateBuffer ( void ) ;

// The main worker function that parses the string.
static DWORD ProcessString ( LPTSTR  szString   ,
                             UINT &  uiCurrPos  ,
                             BOOL    bRecursive  ) ;

// The only function that adds to the input array.
static void AddToKeyInputArray ( WORD   wVK         ,
                                 WORD   wScanCode   ,
                                 DWORD  dwFlags  = 0  ) ;
// Adds an OEM keystroke.
static void AddOEMChar ( TCHAR chChar ) ;

// Handles doing the "{xxx}" statements.
static void ProcessBraceStatement ( LPTSTR szString ,
                                    UINT & uiCurrPos ) ;

/*//////////////////////////////////////////////////////////////////////
                      Implementation starts here.
//////////////////////////////////////////////////////////////////////*/

// See ParsePlayKeysString.h for the description.
UINT ParsePlayKeysString ( IN  LPCTSTR  szString  ,
                           OUT UINT &   uiErrChar ,
                           OUT PINPUT & pRetKeys  ,
                           OUT UINT &   uiCount    )
{
    // Do some parameter validation.
    ASSERT ( FALSE == IsBadStringPtr ( szString , 2000 ) ) ;
    // Do real parameter validation.
    if ( ( NULL == szString ) || ( _T ( '\0' ) == *szString ) )
    {
        return ( PK_INVALIDPARAMS ) ;
    }

    // Initialize a few things.
    // The current position in the string.
    UINT uiCurrStPos = 0 ;
    // The return value.
    UINT uiRet = PK_SUCCESS ;

    // Initialize the input parameters.
    uiErrChar = 0 ;

    // Allocate the starting memory sizes.
    g_uiBuffSize = 20 ;
    g_uiNextBuffSize = 20 * 2 ;

    // g_uiCount is also the current location in g_pRetKeys.
    g_uiCount = 0 ;
    g_pRetKeys = AllocateBuffer ( ) ;

    // Duplicate the string because I poke at it a bit.
    LPTSTR szDup = _tcsdup ( szString ) ;

    // The return state from ProcessString.  This way I can reset the
    //  CTRL, ALT, or SHIFT keys if they are still down.  By doing this,
    //  I can handle strings such at ^+{END} that users might use.
    //  This is more user friendly.
    DWORD dwState ;

    __try
    {
        dwState = ProcessString ( szDup , uiCurrStPos , FALSE ) ;
        // Check the states.
        if ( TRUE == ISSTATESHIFTDOWN ( dwState ) )
        {
            AddToKeyInputArray ( VK_SHIFT               ,
                                 MVK_TO_SC ( VK_SHIFT ) ,
                                 KEYEVENTF_KEYUP         ) ;
        }
        if ( TRUE == ISSTATECTRLDOWN ( dwState ) )
        {
            AddToKeyInputArray ( VK_CONTROL               ,
                                 MVK_TO_SC ( VK_CONTROL ) ,
                                 KEYEVENTF_KEYUP           ) ;
        }
        if ( TRUE == ISSTATEALTDOWN ( dwState ) )
        {
            AddToKeyInputArray ( VK_MENU               ,
                                 MVK_TO_SC ( VK_MENU ) ,
                                 KEYEVENTF_KEYUP        ) ;
        }
    }
    __except ( STATUS_PARSE_ERROR == GetExceptionCode ( ) )
    {
        uiErrChar = uiCurrStPos + 1 ;
        uiRet = PK_PARSEERROR ;
        // Delete the memory allocated.
        delete [] g_pRetKeys ;
        g_pRetKeys = NULL ;

        g_uiCount = 0 ;

    }

    free ( szDup ) ;

    // Fill in the information that the user needs.
    uiCount = g_uiCount ;
    pRetKeys = g_pRetKeys ;

    // All OK, Jumpmaster!
    return ( uiRet ) ;
}


// Allocates a buffer of g_uiBuffSize size and doubles g_uiBuffSize so
//  the next allocation will be twice as much.
static PINPUT AllocateBuffer ( void )
{
    g_uiBuffSize = g_uiNextBuffSize ;
    PINPUT pRet = new INPUT [ g_uiBuffSize ] ;
    memset ( pRet , NULL , sizeof ( INPUT ) * g_uiBuffSize ) ;
    g_uiNextBuffSize = g_uiBuffSize * 2 ;
    return ( pRet ) ;
}

// Adds the information into the global INPUT array.  If needed, it will
//  automatically reallocate the array.  It also bumps up the current
//  position in the array.
static void AddToKeyInputArray ( WORD   wVK       ,
                                 WORD   wScanCode ,
                                 DWORD  dwFlags    )
{
    // Double check that this is not off the end of the array.
    if ( g_uiCount == g_uiBuffSize )
    {
        // Allocate a new buffer.
        PINPUT pTemp = AllocateBuffer ( ) ;
        // Copy the data over.
        memcpy ( pTemp          ,
                 g_pRetKeys     ,
                 sizeof ( INPUT ) * g_uiCount ) ;
        // Get rid of the old memory.
        delete [] g_pRetKeys ;
        // Now use the bigger memory.
        g_pRetKeys = pTemp ;
    }
    // Fill in the particular INPUT.
    g_pRetKeys[ g_uiCount ].type           = INPUT_KEYBOARD ;
    g_pRetKeys[ g_uiCount ].ki.wVk         = wVK ;
    g_pRetKeys[ g_uiCount ].ki.wScan       = wScanCode ;
    g_pRetKeys[ g_uiCount ].ki.dwFlags     = dwFlags ;
    g_pRetKeys[ g_uiCount ].ki.time        = 0 ;
    g_pRetKeys[ g_uiCount ].ki.dwExtraInfo = 0 ;
    // Bump up the current array position.
    g_uiCount++ ;
}

// Adds an OEM character to the input array.
static void AddOEMChar ( TCHAR chChar )
{
    // First try and do the conversion.
    SHORT sTemp = VkKeyScan ( chChar ) ;
    // If the conversion is -1, then there is
    //  a problem.
    if ( -1 == sTemp )
    {
        RaiseException ( STATUS_PARSE_ERROR , 0 , 0 , 0 ) ;
    }
    // Get the hi byte to do the flags
    //  calculations.
    BYTE hiByte = HIBYTE ( sTemp ) ;

    // If the shift key is set, add that to the output stream.
    if ( 0x01 == ( 0x01 & hiByte ) )
    {
        //AddToKeyInputArray ( VK_SHIFT , MVK_TO_SC ( VK_SHIFT ) ) ;                           ,
        AddToKeyInputArray ( VK_SHIFT , MVK_TO_SC ( VK_SHIFT ) ) ;
    }

    // If the ctrl key is set, add that to the output stream.
    if ( 0x02 == ( 0x02 & hiByte ) )
    {
        AddToKeyInputArray ( VK_CONTROL , MVK_TO_SC ( VK_CONTROL ) ) ;
    }

    // If the alt key is set, add that to the output stream.
    if ( 0x04 == ( 0x04 & hiByte ) )
    {
        AddToKeyInputArray ( VK_MENU , MVK_TO_SC ( VK_MENU ) ) ;
    }

    // BUG BUG
    //  What is supposed to happen with those
    //  other flags -- the keyboard driver flags
    //  and the Hankaku flags?

    // Add the key itself.
    AddToKeyInputArray ( LOBYTE ( sTemp ) ,
                         chChar            );

    AddToKeyInputArray ( LOBYTE ( sTemp ) ,
                         chChar           ,
                         KEYEVENTF_KEYUP   ) ;

    // Undo any of the down keys.

    // If the shift key is set, add that to the output stream.
    if ( 0x01 == ( 0x01 & hiByte ) )
    {
        AddToKeyInputArray ( VK_SHIFT               ,
                             MVK_TO_SC ( VK_SHIFT ) ,
                             KEYEVENTF_KEYUP         ) ;
    }

    // If the ctrl key is set, add that to the output stream.
    if ( 0x02 == ( 0x02 & hiByte ) )
    {
        AddToKeyInputArray ( VK_CONTROL               ,
                             MVK_TO_SC ( VK_CONTROL ) ,
                             KEYEVENTF_KEYUP           ) ;
    }

    // If the alt key is set, add that to the output stream.
    if ( 0x04 == ( 0x04 & hiByte ) )
    {
        AddToKeyInputArray ( VK_MENU               ,
                             MVK_TO_SC ( VK_MENU ) ,
                             KEYEVENTF_KEYUP        ) ;
    }

}

// Used by bsearch to find stuff in the BRACECODE array.
static int CodeCompare ( const void * elem1 , const void * elem2 )
{
    return ( _tcscmp ( ((PBRACECODE)elem1)->szString ,
                       ((PBRACECODE)elem2)->szString  ) ) ;
}

// Processes an item in a brace statement.  szString points to the
//  character AFTER the open brace.
static void ProcessBraceStatement ( LPTSTR szString , UINT & uiCurrPos )
{
    // The first thing to do is to check that there is a closing brace.
    UINT uiCloseBrace = 0 ;
    while ( _T( '\0' ) != szString[ uiCloseBrace ] )
    {
        if ( _T ( '}' ) == szString[ uiCloseBrace ] )
        {
            // Since this could be a "{}}" check the next character.
            if ( _T ( '}' ) == szString[ uiCloseBrace + 1 ] )
            {
                uiCloseBrace++ ;
            }
            break ;
        }
        uiCloseBrace++ ;
    }

    // If not pointing at a close brace, kick out.
    if ( _T ( '}' ) != szString[ uiCloseBrace ] )
    {
        RaiseException ( STATUS_PARSE_ERROR , 0 , 0 , 0 ) ;
    }

    // Update the current position index to the brace.
    uiCurrPos += uiCloseBrace ;

    // Zero out the brace.  It is no longer needed.
    szString[ uiCloseBrace ] = _T ( '\0' ) ;

    // Copy the string and uppercase it for the comparison.
    TCHAR szBuff[ MAX_PATH ] ;
    _tcsncpy ( szBuff   ,
               szString ,
               min ( MAX_PATH , uiCloseBrace ) ) ;
    szBuff[ min ( MAX_PATH , uiCloseBrace ) ] = _T ( '\0' ) ;
    _tcsupr ( szBuff ) ;

    // Now do the lookup in the table.
    BRACECODE stTemp ;
    stTemp.szString = szBuff ;

    PBRACECODE pFound = (PBRACECODE)bsearch ( (void*)&stTemp        ,
                                              (void*)&g_stParenCode ,
                                              BRACECODE_COUNT       ,
                                              sizeof ( BRACECODE )  ,
                                              CodeCompare            ) ;

    if ( NULL == pFound )
    {
        RaiseException ( STATUS_PARSE_ERROR , 0 , 0 , 0 ) ;
    }

    if ( 0 == pFound->wScan )
    {
        AddToKeyInputArray ( pFound->wVK , MVK_TO_SC ( pFound->wVK ) ) ;
        AddToKeyInputArray ( pFound->wVK               ,
                             MVK_TO_SC ( pFound->wVK ) ,
                             KEYEVENTF_KEYUP            ) ;
    }
    else
    {
        AddOEMChar ( (TCHAR)pFound->wScan ) ;
    }
}

// Does the real work of processing the input string.  Be careful, this
//  functions uses recursion to handle the () processing.
static DWORD ProcessString ( LPTSTR  szString   ,
                             UINT &  uiCurrPos  ,
                             BOOL    bRecursive  )
{
    // Indicates that a ALT, CTRL, or SHIFT key is down.
    DWORD dwState = 0 ;

    WORD wScanCode ;

    while ( _T ( '\0' ) != szString [ uiCurrPos ] )
    {
        TCHAR chChar = szString[ uiCurrPos ] ;

        switch ( chChar )
        {
            // Shift key
            case _T ( '+' ) :
                // Press the shift key down.
                AddToKeyInputArray ( VK_SHIFT , MVK_TO_SC ( VK_SHIFT ));
                SETSHIFTDOWNSTATE ( dwState ) ;
                break ;
            // Control key.
            case _T ( '^' ) :
                // Press the control key down.
                AddToKeyInputArray ( VK_CONTROL              ,
                                     MVK_TO_SC ( VK_CONTROL ) ) ;
                SETCTRLDOWNSTATE ( dwState ) ;
                break ;
            // Alt key.
            case _T ( '%' ) :
                AddToKeyInputArray ( VK_MENU , MVK_TO_SC ( VK_MENU ) ) ;
                SETALTDOWNSTATE ( dwState ) ;
                break ;
            // The Enter key.
            case _T ( '~' ) :
                wScanCode = MVK_TO_SC ( VK_RETURN ) ;
                AddToKeyInputArray ( VK_RETURN , wScanCode ) ;
                AddToKeyInputArray ( VK_RETURN       ,
                                     wScanCode       ,
                                     KEYEVENTF_KEYUP  ) ;
                break ;
            // A Brace.
            case _T ( '{' ) :
                // Move past the brace.
                uiCurrPos++ ;
                ProcessBraceStatement ( szString + uiCurrPos ,
                                        uiCurrPos              ) ;
                break ;

            // The "long term Shift/Ctrl/Alt hold" code.
            case _T ( '(' ) :
                {
                    // If the Shift, Ctrl, or Alt key is not down, it
                    //  is an error.
                    if ( 0 == dwState )
                    {
                        RaiseException ( STATUS_PARSE_ERROR ,
                                         0                  ,
                                         0                  ,
                                         0                   ) ;
                    }
                    // Where the matching close paren for this open
                    //  paren is located.
                    UINT uiCloseParen = 0 ;
                    //  The numer of open parens seen.
                    UINT uiOpenCount = 0 ;
                    LPTSTR szCurr = szString + uiCurrPos ;
                    // Find the closing paren taking into account
                    //  nested paren pairs.
                    while ( _T( '\0' ) != szCurr [ uiCloseParen ] )
                    {
                        if ( _T ( '(' ) == szCurr [ uiCloseParen ] )
                        {
                            // Bump the nesting level.
                            uiOpenCount++ ;
                        }
                        if ( _T ( ')' ) == szCurr [ uiCloseParen ] )
                        {
                            // Decrement the open paren count.
                            uiOpenCount--;
                            // Is this the one?
                            if ( 0 == uiOpenCount )
                            {
                                break ;
                            }
                        }
                        uiCloseParen++ ;
                    }

                    // No closing paren, error out.
                    if ( _T ( '\0' ) == szCurr[ uiCloseParen ] )
                    {
                        RaiseException ( STATUS_PARSE_ERROR ,
                                         0                  ,
                                         0                  ,
                                         0                   ) ;
                    }
                    // Move the temp string pointer past the open paren.
                    szCurr++ ;
                    // The position in szCurr to start working on.
                    UINT uiProcessed = 0 ;
                    // Recursively handle the parethesised statement.
                    ProcessString ( szCurr ,  uiProcessed , TRUE ) ;
                    // Move the current master position past the closed
                    //  paren.
                    uiCurrPos += uiProcessed ;
                    // Check the states and undo any active.
                    if ( TRUE == ISSTATESHIFTDOWN ( dwState ) )
                    {
                        AddToKeyInputArray ( VK_SHIFT               ,
                                             MVK_TO_SC ( VK_SHIFT ) ,
                                             KEYEVENTF_KEYUP         ) ;
                    }
                    if ( TRUE == ISSTATECTRLDOWN ( dwState ) )
                    {
                        AddToKeyInputArray ( VK_CONTROL               ,
                                             MVK_TO_SC ( VK_CONTROL ) ,
                                             KEYEVENTF_KEYUP          );
                    }
                    if ( TRUE == ISSTATEALTDOWN ( dwState ) )
                    {
                        AddToKeyInputArray ( VK_MENU               ,
                                             MVK_TO_SC ( VK_MENU ) ,
                                             KEYEVENTF_KEYUP        ) ;
                    }
                }
                break ;

            case _T ( ')' ) :
                // If the function is not recursing, and the close paren
                //  is the character, it is an error.
                if ( FALSE == bRecursive )
                {
                   RaiseException ( STATUS_PARSE_ERROR , 0 , 0 , 0 ) ;
                }
                // Just move past the close paren and return.
                uiCurrPos++ ;
                return ( TRUE ) ;
                break ;

            // The following keys must be in braces or are part of the
            //  control stuff.  If they are seen here, it is an error.
            case _T ( '[' ) :
            case _T ( ']' ) :
            case _T ( '}' ) :
                RaiseException ( STATUS_PARSE_ERROR , 0 , 0 , 0 ) ;
                break ;

            default :
                // Figure out the key range.  If it is one of the normal
                //  VK_* keys, then just add it, otherwise, treat it as
                //  an OEM key.
                if ( ( chChar >= _T ( '0' ) ) &&
                     ( chChar <= _T ( '9' ) )    )
                {
                    // Press the key down.
                    AddToKeyInputArray ( chChar , MVK_TO_SC ( chChar ));
                    // Let the key up.
                    AddToKeyInputArray ( chChar               ,
                                         MVK_TO_SC ( chChar ) ,
                                         KEYEVENTF_KEYUP       ) ;
                }
                // Since MapVirtualKey returns the lowercase scancode,
                //  I force the Shift down if needed.
                else if ( ( chChar >= _T ( 'A' ) ) &&
                          ( chChar <= _T ( 'Z' ) )    )
                {
                    if ( FALSE == ISSTATESHIFTDOWN ( dwState ) )
                    {
                        AddToKeyInputArray ( VK_SHIFT               ,
                                             MVK_TO_SC ( VK_SHIFT )  ) ;
                    }
                    // Press the key down.
                    AddToKeyInputArray ( chChar , MVK_TO_SC ( chChar ));
                    // Let the key up.
                    AddToKeyInputArray ( chChar               ,
                                         MVK_TO_SC ( chChar ) ,
                                         KEYEVENTF_KEYUP       ) ;
                    if ( FALSE == ISSTATESHIFTDOWN ( dwState ) )
                    {
                        AddToKeyInputArray ( VK_SHIFT               ,
                                             MVK_TO_SC ( VK_SHIFT ) ,
                                             KEYEVENTF_KEYUP         ) ;
                    }
                }
                else
                {
                    // Treat it as an OEM key.
                    AddOEMChar ( chChar ) ;
                }
                // Check the states.
                if ( TRUE == ISSTATESHIFTDOWN ( dwState ) )
                {
                    AddToKeyInputArray ( VK_SHIFT               ,
                                         MVK_TO_SC ( VK_SHIFT ) ,
                                         KEYEVENTF_KEYUP         ) ;
                }
                if ( TRUE == ISSTATECTRLDOWN ( dwState ) )
                {
                    AddToKeyInputArray ( VK_CONTROL               ,
                                         MVK_TO_SC ( VK_CONTROL ) ,
                                         KEYEVENTF_KEYUP           ) ;
                }
                if ( TRUE == ISSTATEALTDOWN ( dwState ) )
                {
                    AddToKeyInputArray ( VK_MENU               ,
                                         MVK_TO_SC ( VK_MENU ) ,
                                         KEYEVENTF_KEYUP        ) ;
                }

                // Set the state back to nothing.
                dwState = 0 ;
                break ;
        }
        // Bump the current position.
        uiCurrPos++ ;
    }
    return ( dwState ) ;
}
