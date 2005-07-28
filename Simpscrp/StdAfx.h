// stdafx.h : include file for standard system include files,
//  or project specific include files that are used frequently, but
//      are changed infrequently
//

#if !defined(AFX_STDAFX_H__8C2DDFC3_0D14_11D3_98DB_006008463ADC__INCLUDED_)
#define AFX_STDAFX_H__8C2DDFC3_0D14_11D3_98DB_006008463ADC__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000


// Insert your headers here
#define WIN32_LEAN_AND_MEAN		// Exclude rarely-used stuff from Windows headers

#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#pragma warning ( disable : 4127 )
#define ASSERT(f) \
    do                                                              \
    {                                                               \
        if ( !(f))                                                  \
        {                                                           \
                DebugBreak ( ) ;                                    \
        }                                                           \
    } while (0)

#define SUPERASSERT(x)     ASSERT(x)
#define VERIFY(f)          ASSERT(f)


// TODO: reference additional headers your program requires here

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_STDAFX_H__8C2DDFC3_0D14_11D3_98DB_006008463ADC__INCLUDED_)
