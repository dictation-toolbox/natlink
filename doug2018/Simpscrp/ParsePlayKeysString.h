/*----------------------------------------------------------------------
   John Robbins - Feb '99 Microsoft Systems Journal Bugslayer Column
------------------------------------------------------------------------
The core code that processes a string passed to SendKeys
----------------------------------------------------------------------*/

#ifndef _PARSEPLAYKEYSSTRING_H
#define _PARSEPLAYKEYSSTRING_H

/*//////////////////////////////////////////////////////////////////////
Includes
//////////////////////////////////////////////////////////////////////*/
// Defines the SP3 or higher SendInput information.
// Include error returns from PlayKeys.
#include "PlayKeys.h"
#include "SendInput.h"

/*----------------------------------------------------------------------
FUNCTION        :   ParsePlayKeysString
DISCUSSION      :
    Given a string, parses it and returns the VK_* keycodes for each
item in the string.  For the most part, this follows the same
conventions as the Visual Basic SendKeys rules.  The difference is that
this version does not support the repeat keys specifier, "{h 10}".
PARAMETERS      :
    szString  - The string to parse.
    uiErrChar - The character that caused the error.  Undefined if no
                error.
    pRetKeys  - The return buffer.  This memory is allocated with new
                and is up to the caller to delete [] or it will be
                leaked.
    uiCount   - The number of items in piRetBuff.
RETURNS         :
    PK_SUCCESS       - The piRetBuff holds the parsed string.
    PK_INVALIDPARAMS - One or more of the parameters were invalid.
    PK_PARSEERROR    - The input string was not properly formatted.
                         piErrChar points to the character.
    PK_ERROR         - There was a completely unexpected problem.
----------------------------------------------------------------------*/
UINT ParsePlayKeysString ( IN  LPCTSTR  szString  ,
                           OUT UINT &   uiErrChar ,
                           OUT PINPUT & pRetKeys  ,
                           OUT UINT &   uiCount    ) ;

#endif  // _PARSEPLAYKEYSSTRING_H


