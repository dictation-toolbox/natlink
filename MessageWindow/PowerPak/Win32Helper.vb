'-------------------------------------------------------------------------------
'<copyright file="Win32Helper.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.Runtime.InteropServices



'=--------------------------------------------------------------------------=
' Win32Helper
'=--------------------------------------------------------------------------=
' A class containing constants, enums, structures and Declare
' statements for helping us get to win32 ...
'
'
Friend Class Win32Helper

    '=----------------------------------------------------------------------=
    ' Misc Constants
    '=----------------------------------------------------------------------=
    '
    Public Const MAX_PATH As Integer = 260

    '=----------------------------------------------------------------------=
    ' Window Messages
    '=----------------------------------------------------------------------=
    '
    Public Const WM_DESTROY As Integer = &H2
    Public Const WM_DEVICECHANGE As Integer = &H219


    '=----------------------------------------------------------------------=
    ' DeviceBroadcastTypes
    '=----------------------------------------------------------------------=
    ' These are in the wParam of WM_DEVICECHANGE messages
    '
    Public Enum DeviceBroadcastTypes

        DBT_APPYBEGIN = &H0
        DBT_APPYEND = &H1
        DBT_DEVNODES_CHANGED = &H7
        DBT_QUERYCHANGECONFIG = &H17
        DBT_CONFIGCHANGED = &H18
        DBT_CONFIGCHANGECANCELED = &H19
        DBT_MONITORCHANGE = &H1B
        DBT_SHELLLOGGEDON = &H20
        DBT_CONFIGMGAPI32 = &H22
        DBT_VXDINITCOMPLETE = &H23
        DBT_VOLLOCKQUERYLOCK = &H8041
        DBT_VOLLOCKLOCKTAKEN = &H8042
        DBT_VOLLOCKLOCKFAILED = &H8043
        DBT_VOLLOCKQUERYUNLOCK = &H8044
        DBT_VOLLOCKLOCKRELEASED = &H8045
        DBT_VOLLOCKUNLOCKFAILED = &H8046
        DBT_NO_DISK_SPACE = &H47
        DBT_LOW_DISK_SPACE = &H48
        DBT_CONFIGMGPRIVATE = &H7FFF
        DBT_DEVICEARRIVAL = &H8000
        DBT_DEVICEQUERYREMOVE = &H8001
        DBT_DEVICEQUERYREMOVEFAILED = &H8002
        DBT_DEVICEREMOVEPENDING = &H8003
        DBT_DEVICEREMOVECOMPLETE = &H8004
        DBT_DEVICETYPESPECIFIC = &H8005
        DBT_CUSTOMEVENT = &H8006
        DBT_DEVTYP_OEM = &H0
        DBT_DEVTYP_DEVNODE = &H1
        DBT_DEVTYP_VOLUME = &H2
        DBT_DEVTYP_PORT = &H3
        DBT_DEVTYP_NET = &H4
        DBT_DEVTYP_DEVICEINTERFACE = &H5
        DBT_DEVTYP_HANDLE = &H6
        DBT_VPOWERDAPI = &H8100
        DBT_USERDEFINED = &HFFFF

    End Enum ' DeviceBroadcastTypes


    '=----------------------------------------------------------------------=
    ' DriveType
    '=----------------------------------------------------------------------=
    ' Return values for GetDriveType
    '
    Public Enum DriveType

        DRIVE_UNKNOWN = 0
        DRIVE_NO_ROOT_DIR = 1
        DRIVE_REMOVABLE = 2
        DRIVE_FIXED = 3
        DRIVE_REMOTE = 4
        DRIVE_CDROM = 5
        DRIVE_RAMDISK = 6

    End Enum ' DriveType


    '=----------------------------------------------------------------------=
    ' DeviceVolumeFlags
    '=----------------------------------------------------------------------=
    ' These are possible values of the dbcv_flags field in the 
    ' DEV_BROADCAST_VOLUME structure
    '
    Public Enum DeviceVolumeFlags

        CommonButUnknownValue = 0
        DBTF_MEDIA = &H1
        DBTF_NET = &H2

    End Enum ' DeviceVolumeFlags



    '
    ' DEV_BROADCAST_HDR, used for various WM_DEVICECHANGE messages
    '
    <StructLayout(LayoutKind.Sequential)> _
    Public Structure DEV_BROADCAST_HDR

        <MarshalAs(UnmanagedType.U4)> _
        Public dbch_size As Integer

        <MarshalAs(UnmanagedType.U4)> _
        Public dbch_servicetype As Integer

        <MarshalAs(UnmanagedType.U4)> _
        Public dbch_reserved As Integer

    End Structure ' DEV_BROADCAST_HDR


    '
    ' For WM_DEVICECHANGE messages where the dbch_servicetype is
    ' set to DBT_DEVTYP_VOLUME.
    '
    <StructLayout(LayoutKind.Sequential)> _
    Public Structure DEV_BROADCAST_VOLUME

        <MarshalAs(UnmanagedType.U4)> _
        Public dbcv_size As Integer

        <MarshalAs(UnmanagedType.U4)> _
        Public dbcv_servicetype As Integer

        <MarshalAs(UnmanagedType.U4)> _
        Public dbcv_reserved As Integer

        <MarshalAs(UnmanagedType.U4)> _
        Public dbcv_unitmask As Integer

        <MarshalAs(UnmanagedType.U2)> _
        Public dbcv_flags As Short

    End Structure ' DEV_BROADCAST_VOLUME

    '
    ' Possible Flag values for RegisterDeviceNotification
    '
    Public Const DEVICE_NOTIFY_ALL_INTERFACE_CLASSES As Integer = 4
    Public Const DEVICE_NOTIFY_WINDOW_HANDLE As Integer = 0
    Public Const DEVICE_NOTIFY_SERVICE_HANDLE As Integer = 1


    '=----------------------------------------------------------------------=
    ' SERVER_INFO_100
    '=----------------------------------------------------------------------=
    ' For NetServerEnum
    '
    <StructLayout(LayoutKind.Sequential)> _
    Public Structure SERVER_INFO_100

        Public sv100_platform_id As Integer
        <MarshalAs(UnmanagedType.LPWStr)> Public sv100_name As String

    End Structure ' SERVER_INFO_100

    '=----------------------------------------------------------------------=
    ' SERVER_INFO_101
    '=----------------------------------------------------------------------=
    ' For NetServerEnum
    '
    ' typedef struct _SERVER_INFO_101 {
    '      DWORD  sv101_platform_id;
    '      LPWSTR sv101_name;
    '      DWORD  sv101_version_major;
    '      DWORD  sv101_version_minor;
    '      DWORD  sv101_type;
    '      LPWSTR sv101_comment;
    ' } SERVER_INFO_101, *PSERVER_INFO_101, *LPSERVER_INFO_101;
    '
    <StructLayout(LayoutKind.Sequential)> _
    Public Structure SERVER_INFO_101

        Public sv101_platform_id As Integer
        <MarshalAs(UnmanagedType.LPWStr)> Public sv101_name As String
        Public sv101_version_major As Integer
        Public sv101_version_minor As Integer
        Public sv101_type As Integer
        <MarshalAs(UnmanagedType.LPWStr)> Public sv101_comment As String

    End Structure ' SERVER_INFO_101


    '=----------------------------------------------------------------------=
    ' SHARE_INFO_1
    '=----------------------------------------------------------------------=
    ' for NetShareEnum
    '
    <StructLayout(LayoutKind.Sequential)> _
    Public Structure SHARE_INFO_1

        <MarshalAs(UnmanagedType.LPWStr)> Public shi1_netname As String
        Public shi1_type As Integer
        <MarshalAs(UnmanagedType.LPWStr)> Public shi1_remark As String

    End Structure ' SHARE_INFO_1


    '
    ' For SHARE_INFO_1
    '
    Public Enum ShareType

        STYPE_DISKTREE = 0
        STYPE_PRINTQ = 1
        STYPE_DEVICE = 2
        STYPE_IPC = 3
        STYPE_TEMPORARY = &H40000000
        STYPE_SPECIAL = &H80000000

    End Enum ' ShareType


    <StructLayout(LayoutKind.Sequential)> _
    Public Structure RECT

        Public left As Integer
        Public top As Integer
        Public right As Integer
        Public bottom As Integer

    End Structure ' RECT


    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '                               Functions
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=


    '=----------------------------------------------------------------------=
    ' RegisterDeviceNotification
    '=----------------------------------------------------------------------=
    ' HDEVNOTIFY RegisterDeviceNotification(
    '   HANDLE hRecipient,
    '   LPVOID NotificationFilter,
    '   DWORD Flags
    ' );
    '
    ' NotificationFilter is a pointer to a DEV_BROADCAST_HDR structure.
    ' Flags are the DEVICE_NOTIFY_* constants above.
    '
    Public Declare Auto Function RegisterDeviceNotification Lib "user32.dll" ( _
                                    ByVal hwnd As IntPtr, _
                                    ByVal pstructure As IntPtr, _
                                    ByVal dwFlags As Integer) _
                                    As IntPtr

    '=----------------------------------------------------------------------=
    ' UnregisterDeviceNotification
    '=----------------------------------------------------------------------=
    ' BOOL UnregisterDeviceNotification(
    '   HDEVNOTIFY Handle
    ' );
    '
    ' Handle is the handle returned from RegisterDeviceNotification.  Return
    ' value is success or not.
    '
    Public Declare Auto Function UnregisterDeviceNotification Lib "user32.dll" ( _
                                    ByVal handle As IntPtr) _
                                    As Boolean



    Public Declare Auto Function GetLastError Lib "kernel32.dll" () As Integer



    '=----------------------------------------------------------------------=
    ' PostMessage
    '=----------------------------------------------------------------------=
    '  BOOL PostMessage(
    '       HWND hWnd,
    '       UINT Msg,
    '       WPARAM wParam,
    '       LPARAM lParam
    '  );
    '
    Public Declare Auto Function PostMessage Lib "user32.dll" ( _
                                    ByVal hwnd As IntPtr, _
                                    ByVal msg As Integer, _
                                    ByVal wparam As IntPtr, _
                                    ByVal lparam As IntPtr) _
                                    As Boolean


    '=----------------------------------------------------------------------=
    ' GetDriveType
    '=----------------------------------------------------------------------=
    '  UINT GetDriveType(
    '     LPCTSTR lpRootPathName
    '  );
    '
    Public Declare Auto Function GetDriveType Lib "kernel32.dll" ( _
                                    ByVal driveRoot As String) _
                                    As Integer



    '=----------------------------------------------------------------------=
    ' GetVolumeInformation
    '=----------------------------------------------------------------------=
    ' Returns aaaaallll sorts of nifty information about the given Win32
    ' volume ...
    '
    '  BOOL GetVolumeInformation(
    '         LPCTSTR lpRootPathName,
    '         LPTSTR lpVolumeNameBuffer,
    '         DWORD nVolumeNameSize,
    '         LPDWORD lpVolumeSerialNumber,
    '         LPDWORD lpMaximumComponentLength,
    '         LPDWORD lpFileSystemFlags,
    '         LPTSTR lpFileSystemNameBuffer,
    '         DWORD nFileSystemNameSize
    '  );
    '
    Public Declare Auto Function GetVolumeInformation Lib "kernel32.dll" ( _
                                    ByVal lpRootPathName As String, _
                                    ByVal lpVolumeNameBuffer As System.Text.StringBuilder, _
                                    ByVal nVolumeNameSize As Integer, _
                                    ByRef lpvolumeSerialNumber As Integer, _
                                    ByRef lpMaximumComponentLength As Integer, _
                                    ByRef lpFileSystemFlags As Integer, _
                                    ByVal lpFileSystemNameBuffer As System.Text.StringBuilder, _
                                    ByVal nFileSystemNameSize As Integer) _
                                    As Boolean


    '=----------------------------------------------------------------------=
    ' GetVolumeNameForVolumeMountPoint
    '=----------------------------------------------------------------------=
    '  BOOL GetVolumeNameForVolumeMountPoint(
    '       LPCTSTR lpszVolumeMountPoint,
    '       LPTSTR lpszVolumeName,
    '       DWORD cchBufferLength
    '  );
    '
    Public Declare Auto Function GetVolumeNameForVolumeMountPoint Lib "kernel32.dll" ( _
                                    ByVal lpszVolumeMountPoint As String, _
                                    ByVal lpszVolumeName As System.Text.StringBuilder, _
                                    ByVal cchBufferLength As Integer) _
                                    As Boolean



    '=----------------------------------------------------------------------=
    ' GetLogicalDrives
    '=----------------------------------------------------------------------=
    ' DWORD GetLogicalDrives(void);
    '
    Public Declare Auto Function GetLogicalDrives Lib "kernel32.dll" () _
                                    As Integer


    '=----------------------------------------------------------------------=
    ' NetServerEnum
    '=----------------------------------------------------------------------=
    ' NET_API_STATUS NetServerEnum(
    '     LPCWSTR servername,
    '     DWORD level,
    '     LPBYTE* bufptr,
    '     DWORD prefmaxlen,
    '     LPDWORD entriesread,
    '     LPDWORD totalentries,
    '     DWORD servertype,
    '     LPCWSTR domain,
    '     LPDWORD resume_handle
    ' );
    '
    Public Declare Auto Function NetServerEnum Lib "netapi32.dll" ( _
                                    ByVal in_zero As IntPtr, _
                                    ByVal in_level As Integer, _
                                    ByRef out_bufptr As IntPtr, _
                                    ByVal in_prefmaxlen As Integer, _
                                    ByRef out_entriesread As Integer, _
                                    ByRef out_totalentries As Integer, _
                                    ByVal in_servertype As Integer, _
                                    ByVal in_domain As String, _
                                    ByRef out_resumeHandle As IntPtr) _
                                    As Integer


    '=----------------------------------------------------------------------=
    ' NetApiBufferFree
    '=----------------------------------------------------------------------=
    ' NET_API_STATUS NetApiBufferFree(
    '      LPVOID Buffer
    ' );
    '
    Public Declare Auto Function NetApiBufferFree Lib "netapi32.dll" ( _
                                    ByVal in_buffer As IntPtr) _
                                    As Integer


    '=----------------------------------------------------------------------=
    ' NetShareEnum
    '=----------------------------------------------------------------------=
    ' NET_API_STATUS NetShareEnum(
    '    LPWSTR servername,
    '    DWORD level,
    '    LPBYTE* bufptr,
    '    DWORD prefmaxlen,
    '    LPDWORD entriesread,
    '    LPDWORD totalentries,
    '    LPDWORD resume_handle
    ' );
    '
    Public Declare Auto Function NetShareEnum Lib "netapi32.dll" ( _
                                    ByVal in_serverName As String, _
                                    ByVal in_level As Integer, _
                                    ByRef out_bufptr As IntPtr, _
                                    ByVal in_prefmaxlen As Integer, _
                                    ByRef out_entriesread As Integer, _
                                    ByRef out_totalentries As Integer, _
                                    ByRef out_resume_handle As IntPtr) _
                                    As Integer


    '=----------------------------------------------------------------------=
    ' ExtractIconEx
    '=----------------------------------------------------------------------=
    ' UINT ExtractIconEx(
    '   LPCTSTR lpszFile,
    '   int nIconIndex,
    '   HICON* phiconLarge,
    '   HICON* phiconSmall,
    '   UINT nIcons
    ' );
    '
    '
    ' NOTE: I don't want to deal with the hassle of ICON arrays, so I 
    '       declared phiconLarge/Small to only be arrays of size one.
    '       As a result in_nIcons MUST ALWAYS BE "1"
    '
    Public Declare Auto Function ExtractIconEx Lib "shell32.dll" ( _
                                    ByVal in_lpszFile As String, _
                                    ByVal in_nIconIndex As Integer, _
                                    ByRef out_phiconLarge As IntPtr, _
                                    ByRef out_phiconSmall As IntPtr, _
                                    ByVal in_nIcons As Integer) _
                                    As Integer

    '=----------------------------------------------------------------------=
    ' DestroyIcon
    '=----------------------------------------------------------------------=
    ' BOOL WINAPI DestroyIcon(
    '       HICON hIcon
    ' );
    '
    Public Declare Auto Function DestroyIcon Lib "user32.dll" ( _
                                    ByVal in_hIcon As IntPtr) _
                                    As Boolean

    '=----------------------------------------------------------------------=
    ' SHGetFileInfo
    '=----------------------------------------------------------------------=
    ' DWORD_PTR SHGetFileInfo(
    '       LPCTSTR pszPath,
    '       DWORD dwFileAttributes,
    '       SHFILEINFO *psfi,
    '       UINT cbFileInfo,
    '       UINT uFlags
    ' );
    '
    ' NOTE:  in_pshfi is a pointer to a struct called SHFILEINFO.  We will
    '        CoTaskMemAlloc this using the Marshall class (the struct is 692
    '        bytes in size), and then pick apart the data on our own.  I've
    '        simply had too many problems trying to marshall it any other 
    '        way ....
    '
    Public Declare Unicode Function SHGetFileInfoW Lib "Shell32.dll" ( _
                                    ByVal in_pszPath As String, _
                                    ByVal in_dwFileAttributes As Integer, _
                                    ByVal in_pshfi As IntPtr, _
                                    ByVal in_cbFileInfo As Integer, _
                                    ByVal in_uFlags As Integer) _
                                    As Integer

    '=----------------------------------------------------------------------=
    ' SHGetFolderPath
    '=----------------------------------------------------------------------=
    ' HRESULT SHGetFolderPath(
    '       HWND hwndOwner,
    '       int nFolder,
    '       HANDLE hToken,
    '       DWORD dwFlags,
    '       LPTSTR pszPath
    ' );
    '
    Public Declare Auto Function SHGetFolderPath Lib "shell32.dll" ( _
                                    ByVal in_hwndOwner As IntPtr, _
                                    ByVal in_nFolder As Integer, _
                                    ByVal in_hToken As IntPtr, _
                                    ByVal in_dwFlags As Integer, _
                                    ByVal in_pszPath As System.Text.StringBuilder) _
                                    As Integer


    '=----------------------------------------------------------------------=
    ' GetDiskFreeSpaceFreeEx
    '=----------------------------------------------------------------------=
    ' BOOL GetDiskFreeSpaceEx(
    '       LPCTSTR lpDirectoryName,
    '       PULARGE_INTEGER lpFreeBytesAvailable,
    '       PULARGE_INTEGER lpTotalNumberOfBytes,
    '       PULARGE_INTEGER lpTotalNumberOfFreeBytes
    ' );
    '
    Public Declare Auto Function GetDiskFreeSpaceEx Lib "kernel32.dll" ( _
                                    ByVal in_lpDirectoryName As String, _
                                    ByRef out_lpFreeBytesAvailableLow As Long, _
                                    ByRef out_lpTotalNumberOfBytesLow As Long, _
                                    ByRef out_lpTotalNumberOfFreeBytesLow As Long _
                                    ) As Boolean



    '=----------------------------------------------------------------------=
    ' LoadLibrary
    '=----------------------------------------------------------------------=
    ' HMODULE LoadLibrary(
    '       LPCTSTR lpFileName
    ' );
    '
    Public Declare Auto Function LoadLibrary Lib "kernel32.dll" ( _
                                    ByVal in_lpFileName As String) _
                                    As IntPtr

    '=----------------------------------------------------------------------=
    ' GetProcAddress
    '=----------------------------------------------------------------------=
    ' FARPROC GetProcAddress(
    '       HMODULE hModule,
    '       LPCSTR lpProcName
    ' );
    '
    Public Declare Ansi Function GetProcAddress Lib "kernel32.dll" Alias "GetProcAddress" ( _
                                      ByVal in_hModule As IntPtr, _
                                      <MarshalAs(UnmanagedType.LPStr)> ByVal in_lpProcName As String) _
                                      As IntPtr


    '=----------------------------------------------------------------------=
    ' FreeLibrary
    '=----------------------------------------------------------------------=
    ' BOOL FreeLibrary(
    '       HMODULE hModule
    ' );
    '
    Public Declare Auto Function FreeLibrary Lib "kernel32.dll" ( _
                                    ByVal in_hModule As IntPtr) _
                                    As Boolean


    '=----------------------------------------------------------------------=
    ' CallWindowProc
    '=----------------------------------------------------------------------=
    Declare Auto Function CallWindowProc Lib "user32.dll" ( _
                                ByVal in_wndProc As IntPtr, _
                                ByVal hwnd As IntPtr, _
                                ByVal msg As Integer, _
                                ByVal wparam As IntPtr, _
                                ByVal lparam As IntPtr) As Integer



    '=----------------------------------------------------------------------=
    ' LoadString
    '=----------------------------------------------------------------------=
    ' int LoadString(
    '       HINSTANCE hInstance,
    '       UINT uID,
    '       LPTSTR lpBuffer,
    '       int nBufferMax
    ' );
    '
    Declare Auto Function LoadString Lib "user32.dll" ( _
                                ByVal in_hInstance As IntPtr, _
                                ByVal in_uID As Integer, _
                                ByVal in_lpBuffer As System.Text.StringBuilder, _
                                ByVal in_nBufferMax As Integer) _
                                As Integer


    '=----------------------------------------------------------------------=
    ' LoadIcon
    '=----------------------------------------------------------------------=
    ' HICON LoadIcon(
    '       HINSTANCE hInstance,
    '       LPCTSTR lpIconName
    ' );
    '
    Declare Auto Function LoadIcon Lib "user32.dll" ( _
                                ByVal in_hInstance As IntPtr, _
                                ByVal in_lpIconName As String) _
                                As IntPtr


    '=----------------------------------------------------------------------=
    ' SendMessage
    '=----------------------------------------------------------------------=
    ' LRESULT SendMessage(
    '          HWND hWnd,
    '          UINT Msg,
    '          WPARAM wParam,
    '          LPARAM lParam
    ' );
    '
    Public Declare Auto Function SendMessage Lib "user32.dll" ( _
                                ByVal in_hwnd As IntPtr, _
                                ByVal in_msg As Integer, _
                                ByVal in_wparam As IntPtr, _
                                ByVal in_lparam As IntPtr) _
                                As Integer


    '=----------------------------------------------------------------------=
    ' DrawFrameControl
    '=----------------------------------------------------------------------=
    ' BOOL DrawFrameControl(
    '       HDC hdc,     // handle to device context
    '       LPRECT lprc, // bounding rectangle
    '       UINT uType,  // frame-control type
    '       UINT uState  // frame-control state
    ' );
    '
    Public Declare Auto Function DrawFrameControl Lib "user32.dll" ( _
                                ByVal in_hdc As IntPtr, _
                                ByRef in_lprc As RECT, _
                                ByVal in_uType As Integer, _
                                ByVal in_uSTate As Integer) As Boolean


    '=----------------------------------------------------------------------=
    ' GetUserDefaultUILanguage
    '=----------------------------------------------------------------------=
    ' LANGID GetUserDefaultUILanguage(void);
    '
    Public Declare Auto Function GetUserDefaultUILanguage Lib "kernel32.dll" () _
                                As Integer



End Class ' Win32Helper
