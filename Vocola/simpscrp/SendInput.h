/*----------------------------------------------------------------------
   John Robbins - Feb '99 Microsoft Systems Journal Bugslayer Column
------------------------------------------------------------------------
Defines the new SendInput information if not defined.  This is just a
stopgape measure until everyone starts defining _WIN32_WINNT > 0x0400.
----------------------------------------------------------------------*/

#ifndef _SENDINPUT_H
#define _SENDINPUT_H

// Only include the following if needed.
#ifndef INPUT_MOUSE

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tagMOUSEINPUT {
    LONG    dx;
    LONG    dy;
    DWORD   mouseData;
    DWORD   dwFlags;
    DWORD   time;
    DWORD   dwExtraInfo;
} MOUSEINPUT, *PMOUSEINPUT, FAR* LPMOUSEINPUT;

typedef struct tagKEYBDINPUT {
    WORD    wVk;
    WORD    wScan;
    DWORD   dwFlags;
    DWORD   time;
    DWORD   dwExtraInfo;
} KEYBDINPUT, *PKEYBDINPUT, FAR* LPKEYBDINPUT;

typedef struct tagHARDWAREINPUT {
    DWORD   uMsg;
    WORD    wParamL;
    WORD    wParamH;
} HARDWAREINPUT, *PHARDWAREINPUT, FAR* LPHARDWAREINPUT;

#define INPUT_MOUSE     0
#define INPUT_KEYBOARD  1
#define INPUT_HARDWARE  2

typedef struct tagINPUT {
    DWORD   type;

    union
    {
        MOUSEINPUT      mi;
        KEYBDINPUT      ki;
        HARDWAREINPUT   hi;
    };
} INPUT, *PINPUT, FAR* LPINPUT;

WINUSERAPI
UINT
WINAPI
SendInput(
    UINT    cInputs,     // number of input in the array
    LPINPUT pInputs,     // array of inputs
    int     cbSize);     // sizeof(INPUT)

#ifdef __cplusplus
}
#endif

#endif  // INPUT_MOUSE

#endif // _SENDINPUT_H


