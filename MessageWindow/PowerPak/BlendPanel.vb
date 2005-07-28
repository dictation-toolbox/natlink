'-------------------------------------------------------------------------------
'<copyright file="BlendPanel.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.Windows.Forms
Imports System.Drawing.Drawing2D
Imports System.Drawing
Imports System.ComponentModel




'=--------------------------------------------------------------------------=
' BlendPanel
'=--------------------------------------------------------------------------=
' This is a simple extension of the Panel control to support cool blended
' backgrounds.  The new and relevant properties are the BlendStartColor,
' BlendFinishColor and BlendStyle properties.
'
'
<DefaultProperty("Blend"), DefaultEvent("Click")> _
Public Class BlendPanel
    Inherits Panel

    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    ' Private member variables 
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=

    '
    ' Our blending information
    '
    Private m_blend As BlendFill






    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    ' Public Methods, Members, etc
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=


    '=----------------------------------------------------------------------=
    ' Constructor
    '=----------------------------------------------------------------------=
    ' Initializes a new instance of this control.  
    '
    Public Sub New()

        MyBase.New()

        Me.m_blend = New BlendFill(BlendStyle.Vertical, SystemColors.InactiveCaption, SystemColors.Window)

        '
        ' This is a lot of style setting to just ensure that we draw 
        ' ourselves in a relatively flicker free manner when we resize 
        ' (and even when we don't).
        '
        setStyle(ControlStyles.UserPaint, True)
        setStyle(ControlStyles.ResizeRedraw, True)
        setstyle(ControlStyles.AllPaintingInWmPaint, True)
        setstyle(ControlStyles.DoubleBuffer, True)

    End Sub ' New


    '=----------------------------------------------------------------------=
    ' Blend
    '=----------------------------------------------------------------------=
    ' This controls how the background is drawn. 
    '
    ' Type:
    '       VbPowerPack.BlendFill
    '
    <LocalisableDescription("Generic.BlendFill"), _
     Category("Appearance"), _
     Localizable(True)> _
    Public Property Blend() As BlendFill

        Get
            Return Me.m_blend
        End Get

        '
        ' set the new value, refresh, and fire a change event.
        '
        Set(ByVal in_newBlend As BlendFill)
            Me.m_blend = in_newBlend
            Me.Refresh()
            OnBlendChanged(EventArgs.Empty)
        End Set

    End Property ' Blend


    '=----------------------------------------------------------------------=
    ' BackgroundImage
    '=----------------------------------------------------------------------=
    ' Since we own background painting for this control, the BackgroundImage
    ' property doesn't make any sense.
    '
    <Browsable(False), EditorBrowsable(EditorBrowsableState.Never)> _
    Public Shadows Property BackgroundImage() As Image

        Get
            Return MyBase.BackgroundImage
        End Get

        Set(ByVal newBackgroundImage As Image)
            MyBase.BackgroundImage = newBackgroundImage
        End Set

    End Property ' BackgroundImage


    '=----------------------------------------------------------------------=
    ' BackColor
    '=----------------------------------------------------------------------=
    ' Since we own background painting for this control, the BackColor
    ' property doesn't make any sense.
    '
    <Browsable(False), EditorBrowsable(EditorBrowsableState.Never)> _
    Public Overrides Property BackColor() As Color

        Get
            Return MyBase.BackColor
        End Get

        Set(ByVal newBackColor As Color)
            MyBase.BackColor = newBackColor
        End Set

    End Property ' BackColor







    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    ' Private Members/Methods, etc
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=


    '=----------------------------------------------------------------------=
    ' OnBlendChanged
    '=----------------------------------------------------------------------=
    ' Tell people that the blend for this control has changed.
    '
    Protected Overridable Sub OnBlendChanged(ByVal e As System.EventArgs)

        RaiseEvent BlendChanged(Me, e)

    End Sub ' OnBlendChanged


    '=----------------------------------------------------------------------=
    ' OnPaint
    '=----------------------------------------------------------------------=
    ' Handles the WM_PAINT message, and is the place where we will
    ' use the gradient brush to paint the background of the control.  We
    ' will not support WM_ERASEBKGND on this control as the flicker is simply
    ' too annoying.
    '
    Protected Overrides Sub OnPaint(ByVal pevent As System.Windows.Forms.PaintEventArgs)

        Dim lgb As LinearGradientBrush

        '
        ' no point in doing this if we've got nothing to show.
        '
        If Me.Width = 0 Or Me.Height = 0 Then Return

        '
        ' Get the brush based on the settings we have for the blend.
        '
        lgb = Me.m_blend.GetLinearGradientBrush(New Rectangle(0, 0, Me.Width, Me.Height), _
                                                MiscFunctions.GetRightToLeftValue(Me))

        '
        ' now just fill our Background up with a blended background brush.
        ' This is a very powerful feature available in GDI+ exposed 
        ' via our WinForms Graphics object.
        '
        pevent.Graphics.FillRectangle(lgb, New Rectangle(0, 0, Me.Width, Me.Height))

        '
        ' we'll call this so the Paint event is fired for users to paint some
        ' additional goo in their own code ...
        '
        MyBase.OnPaint(pevent)

    End Sub ' OnPaint


    '=----------------------------------------------------------------------=
    ' OnPaintBackground
    '=----------------------------------------------------------------------=
    ' we don't want people to see this in their IDEs since it's not at all
    ' used (we have our control set to do ALL painting in WM_PAINT (OnPaint)
    ' so as to reduce flicker.
    '
    <Browsable(False), EditorBrowsable(EditorBrowsableState.Never)> _
    Protected Overrides Sub OnPaintBackground(ByVal pevent As PaintEventArgs)

        MyBase.OnPaintBackground(pevent)

    End Sub





    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '                               Events
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=



    '=----------------------------------------------------------------------=
    ' BackgroundImageChanged
    '=----------------------------------------------------------------------=
    ' This event no longer makes sense for this control, since we ignore the
    ' BackgroundImage property.
    '
    <Browsable(False), EditorBrowsable(EditorBrowsableState.Never)> _
    Public Shadows Event BackgroundImageChanged(ByVal sender As Object, ByVal e As EventArgs)


    '=----------------------------------------------------------------------=
    ' BackColorChanged
    '=----------------------------------------------------------------------=
    ' This event no longer makes sense for this control, since we ignore the
    ' BackColor property.
    '
    <Browsable(False), EditorBrowsable(EditorBrowsableState.Never)> _
    Public Shadows Event BackColorChanged(ByVal sender As Object, ByVal e As EventArgs)


    '=----------------------------------------------------------------------=
    ' BlendChanged
    '=----------------------------------------------------------------------=
    ' prop change notificatoin: sent whenever the Blend property is
    ' changed.
    '
    <LocalisableDescription("BlendPanel.BlendChanged"), _
     Category("Property Changed")> _
    Public Event BlendChanged(ByVal sender As Object, ByVal e As EventArgs)



End Class ' BlendPanel




