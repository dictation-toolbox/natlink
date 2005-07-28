'-------------------------------------------------------------------------------
'<copyright file="NotificationClosedReason.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.ComponentModel



'=--------------------------------------------------------------------------=
' NotificationCloseReason
'=--------------------------------------------------------------------------=
' This enumeration lists the possible reasons for which a NotificationWindow
' can be closed.
'
'
<LocalisableDescription("NotificationClosedReason")> _
Public Enum NotificationClosedReason

    <LocalisableDescription("NotificationClosedReason.WindowClicked")> _
    WindowClicked

    <LocalisableDescription("NotificationClosedReason.CloseClicked")> _
    CloseClicked

    <LocalisableDescription("NotificationClosedReason.TimedOut")> _
    TimedOut

    <LocalisableDescription("NotificationClosedReason.CloseMethod")> _
    CloseMethod

End Enum ' NotificationClosedReason

