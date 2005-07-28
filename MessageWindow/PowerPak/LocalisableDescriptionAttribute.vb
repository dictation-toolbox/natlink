'-------------------------------------------------------------------------------
'<copyright file="LocalisableDescriptionAttribute.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.ComponentModel
Imports System.Resources


'=--------------------------------------------------------------------------=
' LocalisableDescriptionAttribute
'=--------------------------------------------------------------------------=
' This is a subclass of the Description Attribute that will let use localise
' these values.
'
'
Public Class LocalisableDescriptionAttribute
    Inherits DescriptionAttribute


    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '               Public Members/Methods/Functions/etc...
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=


    '=----------------------------------------------------------------------=
    ' Constructor
    '=----------------------------------------------------------------------=
    ' Goes and initializes a new instance of this class given the XML key
    ' to find for the actual localised description text.
    '
    ' Parameters:
    '       String                  - [in]  Key for which to search.
    '
    Public Sub New(ByVal in_key As String)

		MyBase.New(in_key)

    End Sub ' New


End Class ' LocalisableDescriptionAttribute


