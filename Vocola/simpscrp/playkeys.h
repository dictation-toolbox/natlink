/*----------------------------------------------------------------------
   John Robbins - Feb '99 Microsoft Systems Journal Bugslayer Column
------------------------------------------------------------------------
The PlayKeys function.

I tried to make this ready for internationalization, but I have not
tested this with different keyboard layouts.  If you find that it is not
ready, I would appreciate if you would let me know!
----------------------------------------------------------------------*/

#ifndef _PLAYKEYS_H
#define _PLAYKEYS_H

#ifdef __cplusplus
extern "C" {
#endif

/*//////////////////////////////////////////////////////////////////////
The return defines for PlayKeys
//////////////////////////////////////////////////////////////////////*/
#define PK_SUCCESS        0
#define PK_INVALIDPARAMS  1
#define PK_PARSEERROR     2
#define PK_ERROR          3
#define PK_NOSENDINPUT    4
#define PK_CRASH          5

/*----------------------------------------------------------------------
FUNCTION        :   PlayKeys
DISCUSSION      :
    This function takes a string that corresponds to the keys to play.
The string format follows the Visual Basic SendKey statement rules.
For the first version of this function does not support the repeat keys
construct, "{key number}".
    If the string parses properly, the keys get sent through the
SendInput function.  SendInput is supported by NT4 SP3, Win2000, and
Win98.  PlayKeys checks if USER32.DLL exports SendInput before any other
processing.  If this code must run on an operating system that does not
have SendKeys, you might be able to use the keybd_event.  SendInput is
preferrable because it blocks all other input so that the keystrokes
placed in the keyboard queue as a contiguous unit.
    The caller is responsible for ensuring that the system is set up to
properly handle the upcoming keystrokes.  Needless to say, this function
could prove quite dangerous.
PARAMETERS      :
    szString  - The string to parse.
    puiErrPos - The pointer that will recieve the position of the error
                character in the string.  If the functions succeeds,
                this is undefined.
RETURNS         :
    PK_SUCCESS       - The piRetBuff holds the parsed string.
    PK_INVALIDPARAMS - One or more of the parameters were invalid.
    PK_PARSEERROR    - szString has an invalid character in it.
    PK_NOSENDINPUT   - The SendInput API is not supported on the current
                       operating system.
    PK_ERROR         - There was a completely unexpected problem.
    PK_CRASH         - There was a crash inside the function.
----------------------------------------------------------------------*/
UINT PlayKeys ( LPCTSTR szString  ,
                                                 LPUINT  puiErrPos  ) ;


#ifdef __cplusplus
}
#endif

#endif  // _PLAYKEYS_H


