'-------------------------------------------------------------------------------
'<copyright file="NotificationShowStyle.vb" company="Microsoft">
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
' NotificationShowStyle
'=--------------------------------------------------------------------------=
' This enumeration controls how a NotificationWindow is shown and/or hidden.
'
<LocalisableDescription("NotificationShowStyle")> _
Public Enum NotificationShowStyle

    <LocalisableDescription("NotificationShowStyle.Slide")> _
    Slide

    <LocalisableDescription("NotificationShowStyle.Fade")> _
    Fade

    <LocalisableDescription("NotificationShowStyle.Immediately")> _
    Immediately

End Enum ' NotificationShowStyle




