'-------------------------------------------------------------------------------
'<copyright file="BlendStyle.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.ComponentModel
Imports System.Globalization


'=--------------------------------------------------------------------------=
' BlendStyle
'=--------------------------------------------------------------------------=
' This is a simple enumeration controlling the way in which a background is
' blended on the BlendPanel or other similar controls.
'
' NOTE: These values mirror 
'
'               System.Drawing.Drawing2D.LinearGradientMode
'
'
<LocalisableDescription("BlendStyle")> _
Public Enum BlendStyle

    <LocalisableDescription("BlendStyle.Horizontal")> _
    Horizontal = 0

    <LocalisableDescription("BlendStyle.Vertical")> _
    Vertical

    <LocalisableDescription("BlendStyle.ForwardDiagonal")> _
    ForwardDiagonal

    <LocalisableDescription("BlendStyle.BackwardDiagonal")> _
    BackwardDiagonal

End Enum ' BlendStyle


