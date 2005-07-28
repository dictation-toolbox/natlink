'-------------------------------------------------------------------------------
'<copyright file="BlendFillEditor.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.Windows.Forms
Imports System.Drawing.design
Imports System.ComponentModel
Imports System.ComponentModel.Design
Imports System.Windows.Forms.ComponentModel
Imports System.Windows.Forms.Design


Namespace Design

    '=----------------------------------------------------------------------=
    ' BlendFillEditor
    '=----------------------------------------------------------------------=
    ' This is a drop down editor for the BlendFill type to show the various 
    ' ways to blend as well as the colours to blend.
    '
    ' 
    Public Class BlendFillEditor
        Inherits UITypeEditor


        '=------------------------------------------------------------------=
        ' GetEditStyle
        '=------------------------------------------------------------------=
        ' We use this method to indicate that we're going to be using a drop
        ' down editor for our value.
        '
        Public Overloads Overrides Function GetEditStyle(ByVal context As System.ComponentModel.ITypeDescriptorContext) As UITypeEditorEditStyle

            If Not (context Is Nothing) AndAlso Not (context.Instance Is Nothing) Then
                Return UITypeEditorEditStyle.DropDown
            End If

            Return MyBase.GetEditStyle(context)

        End Function ' GetEditStyle



        '=------------------------------------------------------------------=
        ' EditValue
        '=------------------------------------------------------------------=
        ' Instructs us to pop up our dropdown editor and let the user
        ' edit the value for this class.
        '
        Public Overloads Overrides Function EditValue(ByVal context As System.ComponentModel.ITypeDescriptorContext, ByVal provider As System.IServiceProvider, ByVal value As Object) As Object

            Dim editorService As IWindowsFormsEditorService
            Dim editor As BlendFillEditorUI
            Dim reverse As Boolean
            Dim blend As BlendFill

            If (Not (context Is Nothing) AndAlso Not (context.Instance Is Nothing) AndAlso Not (provider Is Nothing)) Then

                editorService = CType(provider.GetService(GetType(IWindowsFormsEditorService)), IWindowsFormsEditorService)

                If Not (editorService Is Nothing) Then

                    '
                    ' get the current values and create an editor
                    '
                    blend = CType(value, BlendFill)
                    reverse = getReverseValue(context)
                    editor = New BlendFillEditorUI(editorService, blend, reverse)

                    '
                    ' Now use the host service to show the editor.
                    '
                    editorService.DropDownControl(editor)

                    '
                    ' Finally, get the new value and return it.
                    '
                    value = editor.GetValue()

                End If
            End If

            Return value

        End Function ' EditValue



        '=------------------------------------------------------------------=
        ' GetPaintValueSupported
        '=------------------------------------------------------------------=
        ' We want to support cool painting in the property browser.
        '
        '
        Public Overloads Overrides Function GetPaintValueSupported(ByVal context As System.ComponentModel.ITypeDescriptorContext) As Boolean
            Return True
        End Function ' GetPaintValueSupported



        '=------------------------------------------------------------------=
        ' PaintValue
        '=------------------------------------------------------------------=
        ' Paints our cool value in the property browser.
        '
        '
        Public Overloads Overrides Sub PaintValue(ByVal e As System.Drawing.Design.PaintValueEventArgs)

            Dim lgb As System.Drawing.Drawing2D.LinearGradientBrush
            Dim bf As BlendFill

            bf = CType(e.Value, BlendFill)
            If Not bf Is Nothing Then

                Try
                    lgb = bf.GetLinearGradientBrush(e.Bounds)

                    e.Graphics.FillRectangle(lgb, e.Bounds)
                Finally
                    If Not lgb Is Nothing Then lgb.Dispose()
                End Try
            End If

        End Sub ' PaintValue








        '=------------------------------------------------------------------=
        '=------------------------------------------------------------------=
        '=------------------------------------------------------------------=
        '=------------------------------------------------------------------=
        '                   Private Methods/Functions/etc.
        '=------------------------------------------------------------------=
        '=------------------------------------------------------------------=
        '=------------------------------------------------------------------=
        '=------------------------------------------------------------------=


        '=------------------------------------------------------------------=
        ' getReverseValue
        '=------------------------------------------------------------------=
        ' Indicates whether or not the given instance behind this editor has
        ' RightToLeft reading set to true.
        '
        Private Function getReverseValue(ByVal context As System.ComponentModel.ITypeDescriptorContext) _
                                         As Boolean

            Dim pdc As PropertyDescriptorCollection
            Dim pd As PropertyDescriptor
            Dim rtl As RightToLeft
            Dim ctl As Control

            '
            ' We have to look at context.Instance, and see if it has a 
            ' property named "RightToLeft".  If so, then use that value,
            ' otherwise, just assume no RTL.
            '
            If Not context Is Nothing Then
                If Not context.Instance Is Nothing Then
                    pdc = TypeDescriptor.GetProperties(context.Instance)
                    If Not pdc Is Nothing Then
                        pd = pdc("RightToLeft")
                        rtl = CType(pd.GetValue(context.Instance), RightToLeft)
                        Try
                            ctl = CType(context.Instance, Control)
                        Catch ex As Exception
                        End Try
                        If Not ctl Is Nothing Then
                            Return MiscFunctions.GetRightToLeftValue(ctl)
                        Else
                            Return Not rtl = RightToLeft.No
                        End If
                    End If
                End If
            End If

            Return False

        End Function ' getReverseValue



    End Class ' BlendFillEditor



End Namespace ' Design
