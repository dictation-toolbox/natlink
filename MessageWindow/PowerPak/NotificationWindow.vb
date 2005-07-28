Option Strict Off

'-------------------------------------------------------------------------------
'<copyright file="NotificationWindow.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.Windows.Forms
Imports System.Drawing
Imports System.ComponentModel
Imports System.Runtime.InteropServices


' 
' CONSIDER: IM Toast Window WndClass is:
'         MSBLPopupMsgWClass.  If it's important that we go and position 
'         ourselves relative to them, then we need to add a routine to 
'         seek out windows of this class.
'



'=--------------------------------------------------------------------------=
' NotificationWindow
'=--------------------------------------------------------------------------=
' This is a popup window inspired/motivated by the "Toast" style windows
' seen in Windows applications today, such as Instant Messenger and Office
' 2003.
'
<DefaultProperty("Text"), DefaultEvent("Click")> _
Public Class NotificationWindow
    Inherits Component

    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    ' Private member variables and the likes
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=

    Private Const DEFAULT_TIMEOUT As Integer = 10000        ' 10s

    Private Const CORNERIMAGE_MAX_WIDTH As Integer = 32
    Private Const CORNERIMAGE_MAX_HEIGHT As Integer = 32

    '
    ' This is the text content of the Notification Window
    '
    Private m_defaultText As String

    '
    ' Timeout in milliseconds before the window disappears
    '
    Private m_defaultTimeout As Integer

    '
    ' Icon displayed in the top left (right on bidi) corner
    '
    Private m_cornerImage As Image

    '
    ' Image displayed across the bottom of the window.
    '
    Private m_bottomImage As Image

    '
    ' How the background is blended.
    '
    Private m_blend As BlendFill

    '
    ' Font with which to display the text
    '
    Private m_font As Font

    '
    ' The colour in which to display the text
    '
    Private m_foreColour As Color

    '
    ' The method in which the notification window is shown and/or hidden
    '
    Private m_showStyle As NotificationShowStyle

    '
    ' Indicates whether the content text will be displayed as a hyperlink
    ' label.
    '
    Private m_textIsHyperLink As Boolean

    '
    ' Indicates what the transparent "mask" colour should be for the two
    ' images (Icon and BottomImage) on this window should be.
    '
    Private m_transparentColour As Color


    '
    ' indicates whether or not we should show a Close or "X" button in the
    ' top corner.
    '
    Private m_closeButton As Boolean

    '
    ' Should we draw RTL?
    '
    Private m_rightToLeft As RightToLeft







    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '                     Public Methods, Members, etc
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


        Me.m_defaultTimeout = DEFAULT_TIMEOUT
        Me.m_cornerImage = Nothing
        Me.m_bottomImage = Nothing
        Me.m_blend = New BlendFill(BlendStyle.Vertical, SystemColors.InactiveCaption, SystemColors.Window)
        Me.m_font = Control.DefaultFont
        Me.m_foreColour = Control.DefaultForeColor
        Me.m_showStyle = NotificationShowStyle.Slide
        Me.m_textIsHyperLink = False
        Me.m_transparentColour = Color.Transparent
        Me.m_rightToLeft = RightToLeft.No

    End Sub

    '=----------------------------------------------------------------------=
    ' Constructor
    '=----------------------------------------------------------------------=
    ' Initializes a new instance of this control and sites us in the given
    ' container, if appropriate.
    '
    ' Parameters:
    '       IContainer      - [in]  container to which to add ourselves.
    '
    Public Sub New(ByVal container As IContainer)

        Me.New()
        container.Add(Me)

    End Sub


    '=----------------------------------------------------------------------=
    ' Notify
    '=----------------------------------------------------------------------=
    ' Shows a new instance of a NotificationWindow, based on the current
    ' properties that have been set by the programmer.  The window is shown
    ' and the method then immediately returns.
    '
    ' Returns:
    '       Form              - A handle to the newly shown form.
    '
    <LocalisableDescription("NotificationWindow.Notify1")> _
    Public Function Notify() As Form

        Return Notify(Me.m_defaultText, _
                                   Me.m_defaultTimeout, _
                                   Nothing, _
                                   Me.m_cornerImage, _
                                   Me.m_bottomImage, _
                                   Me.m_textIsHyperLink, _
                                   Me.m_font, _
                                   Me.m_foreColour, _
                                   Me.m_transparentColour, _
                                   Me.m_closeButton, _
                                   Me.m_showStyle, _
                                   Me.m_blend, _
                                   Me.m_rightToLeft)

    End Function ' Notify

    '=----------------------------------------------------------------------=
    ' Notify
    '=----------------------------------------------------------------------=
    ' Shows a new instance of a NotificationWindow, based on the current
    ' properties that have been set by the programmer.  The window is shown
    ' and the method then immediately returns.
    '
    ' Parameters:
    '       String              - [in]  Text to display
    '
    ' Returns:
    '       Form                - A handle to the newly shown form.
    '
    <LocalisableDescription("NotificationWindow.Notify1")> _
    Public Function Notify(ByVal in_text As String) As Form

        Return Notify(in_text, _
                                   Me.m_defaultTimeout, _
                                   Nothing, _
                                   Me.m_cornerImage, _
                                   Me.m_bottomImage, _
                                   Me.m_textIsHyperLink, _
                                   Me.m_font, _
                                   Me.m_foreColour, _
                                   Me.m_transparentColour, _
                                   Me.m_closeButton, _
                                   Me.m_showStyle, _
                                   Me.m_blend, _
                                   Me.m_rightToLeft)

    End Function ' Notify


    '=----------------------------------------------------------------------=
    ' Notify
    '=----------------------------------------------------------------------=
    ' Shows a new instance of a NotificationWindow, based on the current
    ' properties that have been set by the programmer.  The window is shown
    ' and the method then immediately returns.
    '
    ' Parameters:
    '       String              - [in]  Text to display
    '       Integer             - [in]  timeout in ms
    '
    ' Returns:
    '       Form                - A handle to the newly shown form.
    '
    <LocalisableDescription("NotificationWindow.Notify1")> _
    Public Function Notify(ByVal in_text As String, _
                                        ByVal in_timeout As Integer) _
                                        As Form

        Return Notify(in_text, _
                                   in_timeout, _
                                   Nothing, _
                                   Me.m_cornerImage, _
                                   Me.m_bottomImage, _
                                   Me.m_textIsHyperLink, _
                                   Me.m_font, _
                                   Me.m_foreColour, _
                                   Me.m_transparentColour, _
                                   Me.m_closeButton, _
                                   Me.m_showStyle, _
                                   Me.m_blend, _
                                   Me.m_rightToLeft)

    End Function ' Notify


    '=----------------------------------------------------------------------=
    ' Notify
    '=----------------------------------------------------------------------=
    ' Shows a new instance of a NotificationWindow, based on the current
    ' properties that have been set by the programmer.  The window is shown
    ' and the method then immediately returns.
    '
    ' Parameters:
    '       String              - [in]  Text to display
    '       Integer             - [in]  timeout in ms
    '       Object              - [in]  "Tag" to identify this window.
    '
    ' Returns:
    '       Form                - A handle to the newly shown form.
    '
    <LocalisableDescription("NotificationWindow.Notify1")> _
    Public Function Notify(ByVal in_text As String, _
                                        ByVal in_timeout As Integer, _
                                        ByVal in_tag As Object) _
                                        As Form

        Return Notify(in_text, _
                                   in_timeout, _
                                   in_tag, _
                                   Me.m_cornerImage, _
                                   Me.m_bottomImage, _
                                   Me.m_textIsHyperLink, _
                                   Me.m_font, _
                                   Me.m_foreColour, _
                                   Me.m_transparentColour, _
                                   Me.m_closeButton, _
                                   Me.m_showStyle, _
                                   Me.m_blend, _
                                   Me.m_rightToLeft)

    End Function ' Notify


    '=----------------------------------------------------------------------=
    ' Notify
    '=----------------------------------------------------------------------=
    ' Shows a new instance of a NotificationWindow, based on the given 
    ' parameterized values.  The window is shown and the method then
    ' immediately returns.
    '
    ' Parameters:
    '       String              - [in]  Text to display
    '       Integer             - [in]  Timeout in ms
    '       Object              - [in]  "Tag" to identify the window
    '       Image               - [in]  corner image
    '       Image               - [in]  bottom image
    '       Boolean             - [in]  is the text hyperlinked?
    '       Font                - [in]  font to use
    '       Color               - [in]  text colour
    '       Color               - [in]  masking colour for images
    '       Boolean             - [in]  should the "X" button be shown?
    '       NotificationShowStyle - [in]    how to show the window
    '       BlendFill           - [in]  how the background is to be drawn.
    '       Boolean             - [in]  Are we RTL or not?
    '
    ' Returns:
    '       Form                - A handle to the newly shown form.
    '
    <LocalisableDescription("NotificationWindow.Notify1")> _
    Public Function Notify(ByVal in_text As String, _
                                        ByVal in_timeout As Integer, _
                                        ByVal in_tag As Object, _
                                        ByVal in_cornerImage As Image, _
                                        ByVal in_bottomImage As Image, _
                                        ByVal in_textIsHyperLink As Boolean, _
                                        ByVal in_font As Font, _
                                        ByVal in_foreColour As Color, _
                                        ByVal in_transparentColour As Color, _
                                        ByVal in_closeButton As Boolean, _
                                        ByVal in_showStyle As NotificationShowStyle, _
                                        ByVal in_blend As BlendFill, _
                                        ByVal in_rightToLeft As RightToLeft) _
                                        As Form

        Dim f As NotificationForm

        f = New NotificationForm(Me, in_tag, _
                                 in_text, _
                                 in_timeout, _
                                 in_cornerImage, _
                                 in_bottomImage, _
                                 in_textIsHyperLink, _
                                 in_font, _
                                 in_foreColour, _
                                 in_transparentColour, _
                                 in_closeButton, _
                                 in_showStyle, _
                                 in_blend, _
                                 determineRTL())

        '
        ' Please see NotificationForm::ShowNoActivate.  Unfortunately,
        ' Winforms doesn't let me specify a flag to ShowWindow, so I have
        ' to do some wonky stuff to show the window in a non-activated
        ' fashion.  This will be addressed in future versions of it.
        '
        f.ShowNoActivate()
        Return f

    End Function ' Notify



    '=----------------------------------------------------------------------=
    ' DefaultText
    '=----------------------------------------------------------------------=
    ' Gets and/or sets the content that is displayed in the NotificationWindow
    ' if the user doesn't specify a value for the "text" parameter to the 
    ' Notify Method.
    '
    <LocalisableDescription("NotificationWindow.DefaultText"), _
     Category("Appearance"), _
     DefaultValue(""), _
     Localizable(True)> _
    Public Property DefaultText() As String

        Get
            Return Me.m_defaultText
        End Get

        Set(ByVal in_newDefaultText As String)
            Me.m_defaultText = in_newDefaultText
        End Set

    End Property ' DefaultText


    '=----------------------------------------------------------------------=
    ' DefaultTimeout
    '=----------------------------------------------------------------------=
    ' Default Timeout in milliseconds before the window disappears for the
    ' cases when the user doesn't specify the "timeout" parameter of the
    ' Notify method.
    '
    <LocalisableDescription("NotificationWindow.DefaultTimeout"), _
     Category("Behavior"), _
     DefaultValue(DEFAULT_TIMEOUT), _
     Localizable(True)> _
    Public Property DefaultTimeout() As Integer

        Get
            Return Me.m_defaultTimeout
        End Get

        Set(ByVal in_newDefaultTimeout As Integer)

            If in_newDefaultTimeout < 0 Then
				Throw New ArgumentException("excNotificationWindowNegTime")
            End If

            Me.m_defaultTimeout = in_newDefaultTimeout
        End Set

    End Property ' DefaultTimeout


    '=----------------------------------------------------------------------=
    ' CornerImage
    '=----------------------------------------------------------------------=
    ' Icon displayed in the top left corner.  The background is masked for 
    ' transparency based on the current value of the ImageTransparentColor
    ' property.
    '
    <LocalisableDescription("NotificationWindow.CornerImage"), _
     Category("Appearance"), _
     DefaultValue(GetType(Image), Nothing), _
     Localizable(True)> _
    Public Property CornerImage() As Image

        Get
            Return Me.m_cornerImage
        End Get

        Set(ByVal in_newCornerImage As Image)
            If Not in_newCornerImage Is Nothing _
               AndAlso (in_newCornerImage.Width > CORNERIMAGE_MAX_WIDTH _
                        OrElse in_newCornerImage.Height > CORNERIMAGE_MAX_HEIGHT) Then
				Throw New ArgumentException("excNotificationWindowCorner3232")
            End If

            Me.m_cornerImage = in_newCornerImage
        End Set

    End Property ' CornerImage


    '=----------------------------------------------------------------------=
    ' BottomImage
    '=----------------------------------------------------------------------=
    ' This is the image displayed across the bottom of the NotificationWindow.
    ' The background is masked for transparency based on the current value
    ' of the ImageTransparentColor property.
    '
    <LocalisableDescription("NotificationWindow.BottomImage"), _
     Category("Appearance"), _
     DefaultValue(GetType(Image), Nothing), _
     Localizable(True)> _
    Public Property BottomImage() As Image

        Get
            Return Me.m_bottomImage
        End Get

        Set(ByVal in_newBottomImage As Image)
            Me.m_bottomImage = in_newBottomImage
        End Set

    End Property ' BottomImage


    '=----------------------------------------------------------------------=
    ' CloseButton
    '=----------------------------------------------------------------------=
    ' Inidicates whether or not we should show a Close or "X" button in the
    ' top corner of the window.
    '
    ' Type:
    '       Boolean
    '
    <LocalisableDescription("NotificationWindow.CloseButton"), _
     Category("Behavior"), _
     DefaultValue(False), _
     Localizable(True)> _
    Public Property CloseButton() As Boolean
        Get
            Return Me.m_closeButton
        End Get
        Set(ByVal in_newCloseButton As Boolean)
            Me.m_closeButton = in_newCloseButton
        End Set
    End Property ' CloseButton


    '=----------------------------------------------------------------------=
    ' Blend
    '=----------------------------------------------------------------------=
    ' This controls how the background is drawn.
    '
    ' Type:
	'       BlendFill
	'
	<LocalisableDescription("NotificationWindow.Blend"), _
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
		End Set

	End Property	' Blend



	'=----------------------------------------------------------------------=
	' Font
	'=----------------------------------------------------------------------=
	' Font with which to display the text.
	<LocalisableDescription("NotificationWindow.Font"), _
	 Category("Appearance"), _
	 Localizable(True)> _
	Public Property Font() As Font

		Get
			Return Me.m_font
		End Get

		Set(ByVal newFont As Font)
			Me.m_font = newFont
		End Set

	End Property	' Font


	'=----------------------------------------------------------------------=
	' ForeColor
	'=----------------------------------------------------------------------=
	' The colour in which to display the text.
	<LocalisableDescription("NotificationWindow.ForeColour"), _
	 Category("Appearance"), _
	 DefaultValue(GetType(SystemColors), "Control"), _
	 Localizable(True)> _
	Public Property ForeColor() As Color

		Get
			Return Me.m_foreColour
		End Get

		Set(ByVal newForeColor As Color)
			Me.m_foreColour = newForeColor
		End Set

	End Property	' ForeColor


	'=----------------------------------------------------------------------=
	' ShowStyle
	'=----------------------------------------------------------------------=
	' The method in which the notification window is shown and/or hidden.
	<LocalisableDescription("NotificationWindow.ShowStyle"), _
	 Category("Behavior"), _
	 DefaultValue(NotificationShowStyle.Slide), _
	 Localizable(True)> _
	Public Property ShowStyle() As NotificationShowStyle

		Get
			Return Me.m_showStyle
		End Get

		Set(ByVal in_newShowStyle As NotificationShowStyle)
			If in_newShowStyle < 0 Or in_newShowStyle > 2 Then
				Throw New ArgumentOutOfRangeException("Value")
			End If
			Me.m_showStyle = in_newShowStyle
		End Set

	End Property	' ShowStyle


	'=----------------------------------------------------------------------=
	' TextIsHyperLink
	'=----------------------------------------------------------------------=
	' Indicates whether the content text will be displayed as a LinkLabel
	'
	<LocalisableDescription("NotificationWindow.TextIsHyperLink"), _
	 Category("Behavior"), _
	 DefaultValue(False), _
	 Localizable(True)> _
	Public Property TextIsHyperLink() As Boolean

		Get
			Return Me.m_textIsHyperLink
		End Get

		Set(ByVal newTextIsHyperLink As Boolean)
			Me.m_textIsHyperLink = newTextIsHyperLink
		End Set

	End Property	' TextIsHyperLink


	'=----------------------------------------------------------------------=
	' ImageTransparentColor
	'=----------------------------------------------------------------------=
	' Indicates what the transparent "mask" colour should be for the two
	' images (Icon and BottomImage) on this window.
	'
	<LocalisableDescription("NotificationWindow.TransparentColour"), _
	 Category("Appearance"), _
	 DefaultValue(GetType(Color), "Transparent"), _
	 Localizable(True)> _
	Public Property ImageTransparentColor() As Color

		Get
			Return Me.m_transparentColour
		End Get

		Set(ByVal newTransparentColor As Color)
			Me.m_transparentColour = newTransparentColor
		End Set

	End Property	' ImageTransparentColor


	'=----------------------------------------------------------------------=
	' RightToLeft
	'=----------------------------------------------------------------------=
	' Should the control be drawn using RightToLeft support for Arabic/Hebrew
	' systems?
	'
	' Type:
	'       Boolean
	'
	<LocalisableDescription("NotificationWindow.RightToLeft"), _
	 Category("Appearance"), _
	 DefaultValue(System.Windows.Forms.RightToLeft.No), _
	 Localizable(True)> _
	Public Property RightToLeft() As RightToLeft

		Get
			Return Me.m_rightToLeft
		End Get

		Set(ByVal in_newRightToLeft As RightToLeft)
			If in_newRightToLeft < 0 OrElse in_newRightToLeft > 2 Then
				Throw New ArgumentOutOfRangeException("Value", "excNotificationWindowBadRTL")
			End If

			'
			' Unfortunately, there's no way to actually find out who
			' our parent form is at runtime, so we can't really use
			' the Inherit Value.  We just map it to Nope.
			'
			If in_newRightToLeft = RightToLeft.Inherit Then
				in_newRightToLeft = RightToLeft.No
			End If

			Me.m_rightToLeft = in_newRightToLeft
		End Set

	End Property	' RightToLeft









	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	' Private/Protected Members/Methods, etc
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=



	'=----------------------------------------------------------------------=
	' OnClick
	'=----------------------------------------------------------------------=
	' The user has clicked on the form.  We will raise an event letting them
	' know this.  After the Click event is raised, the NotificationWindow
	' component will fire the "Closing" event for the window, which is
	' cancellable.
	'
	' Parameters:
	'       Object                  - [in]  User "Tag" for this window.
	'       Form                    - [in]  NotificationForm handle
	'
	Protected Friend Overridable Sub OnClick(ByVal in_tag As Object, _
											 ByVal in_nf As Form)

		RaiseEvent Click(Me, System.EventArgs.Empty)

	End Sub	' OnClick


	'=----------------------------------------------------------------------=
	' OnClosing
	'=----------------------------------------------------------------------=
	' The Notification Window is about to close (because the user clicked on
	' it, the user clicked on the "X" close button, or the timeout expired.).
	' This event lets the application know about it, and gives them the 
	' opportunity to cancel the close event.
	'
	' Parameters:
	'       NotificationClosedReason    - [in]  why is it closing?
	'       Object                      - [in]  "Tag" identifying window 
	'       Form                        - [in]  actual window handle closing
	'
	' Returns:
	'       Boolean                     - True means Cancel, False means close.
	'
	<LocalisableDescription("NotificationWindow.OnClosing")> _
	Protected Friend Overridable Function OnClosing(ByVal in_reason As NotificationClosedReason, _
													ByVal in_tag As Object, _
													ByVal in_window As Form) _
													As Boolean

		Dim ncea As NotificationCancelEventArgs
		ncea = New NotificationCancelEventArgs(in_reason, in_tag, in_window)

		RaiseEvent Closing(Me, ncea)
		Return ncea.Cancel

	End Function	' OnClosing


	'=----------------------------------------------------------------------=
	' OnClose
	'=----------------------------------------------------------------------=
	' The given NotificationWindow has been closed.  Go and tell anybody who
	' cares why.
	'
	' Parameters:
	'       NotificationClosedReason    - [in]  why?
	'       Object                      - [in]  "Tag" identifying window closed
	'       Form                        - [in]  Handle for closed window.
	'
	Protected Friend Sub OnClosed(ByVal in_reason As NotificationClosedReason, _
								  ByVal in_tag As Object, _
								  ByVal in_handle As Form)

		RaiseEvent Closed(Me, New NotificationClosedEventArgs(in_reason, in_tag, in_handle))

	End Sub	' OnClosed


	'=----------------------------------------------------------------------=
	' determineRTL
	'=----------------------------------------------------------------------=
	' Figures out if we should be RTL
	'
	' Returns:
	'       Boolean             - True means yes, false nope.
	'
	Private Function determineRTL() As Boolean

		Dim rtl As RightToLeft
		Dim c As Control

		If Me.m_rightToLeft = RightToLeft.Yes Then Return True
		If Me.m_rightToLeft = RightToLeft.No Then Return False

		If Me.m_rightToLeft = RightToLeft.Inherit Then
			System.Diagnostics.Debug.Fail("I should never have an Inherit Value!")
			Return False
		End If

	End Function	' determineRTL






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
	' Click
	'=----------------------------------------------------------------------=
	' The user has clicked on the notification Window.  The Closing event
	' will be fired next, and the programmer can either cancel it or let the
	' window close.
	'
	'
	<LocalisableDescription("NotificationWindow.Click"), _
	 Category("Behavior")> _
	Public Event Click(ByVal sender As Object, ByVal e As System.EventArgs)


	'=----------------------------------------------------------------------=
	' Closing
	'=----------------------------------------------------------------------=
	' Fired just before the Window is about to close, and gives a reason for
	' why this happens.
	'
	<LocalisableDescription("NotificationWindow.Closing"), _
	 Category("Behavior")> _
	Public Event Closing(ByVal sender As Object, ByVal ce As NotificationCancelEventArgs)


	'=----------------------------------------------------------------------=
	' Closed
	'=----------------------------------------------------------------------=
	' The NotificationWindow has been closed.  This event provides the reason,
	' and is not cancellable at all.
	'
	<LocalisableDescription("NotificationWindow.Closed"), _
	 Category("Behavior")> _
	Public Event Closed(ByVal sender As Object, ByVal e As NotificationClosedEventArgs)



End Class ' NotificationWindow









'=--------------------------------------------------------------------------=
' NotificationForm
'=--------------------------------------------------------------------------=
' This is the actual Form window that is the Notification Window.
'
'
'
Friend Class NotificationForm
    Inherits System.Windows.Forms.Form

    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    ' System Imports and Constants
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '
    Declare Auto Function ShowWindow Lib "User32.dll" (ByVal handle As System.IntPtr, ByVal nCmdShow As Integer) As Boolean


    Private Const DEFAULT_WIDTH As Integer = 155
    Private Const DEFAULT_HEIGHT As Integer = 135
    Private Const BORDER_WIDTH As Integer = 5
    Private Const ICON_MAXHEIGHT As Integer = 32
    Private Const ICON_MAXWIDTH As Integer = 32
    Private Const BOTTOMIMAGE_MAXHEIGHT As Integer = 16
    Private Const TIMER_INTERVAL As Integer = 50            ' ms

    '=----------------------------------------------------------------------=
    ' TaskBarLocation
    '=----------------------------------------------------------------------=
    ' Where is the Windows TaskBar?
    '
    Private Enum TaskBarLocation

        Top
        Left
        Bottom
        Right

    End Enum ' TaskBarLocation

    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    ' Private member variables and the likes
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=

    '
    ' This is static/Shared collection of forms, that lets us know what
    ' other NotificationForms are active so that we can position ourselves
    ' relative to them
    '
    Private Shared s_FormsCollection As System.Collections.ArrayList

    '
    ' This is our parent component. We need this to be able to send events
    ' to the programmer.
    '
    Private m_parent As NotificationWindow

    '
    ' This is the panel in which we will do our drawing of text and images.
    '
    Private WithEvents m_panel As BlendPanel

    ' 
    ' The image to display at the top
    '
    Private m_cornerImage As Image

    ' 
    ' The image to display across the bottom.
    '
    Private m_bottomImage As Image

    '
    ' We will only use this for one tick:  It controls our Timeout period.
    '
    Private WithEvents m_timer As Timer

    '
    ' We use this timer for showing and hiding the window.
    '
    Private WithEvents m_showTimer As Timer

    '
    ' The text to display in the control.
    '
    Private m_text As String

    '
    ' Whether to display the text as hyperlinked or not.
    '
    Private m_textIsHyperLink As Boolean

    '
    ' The font in which to display the text.
    '
    Private m_font As Font

    ' The colour in which to display the text.
    '
    Private m_foreColour As Color

    '
    ' The method with which to both show and hide the window.
    '
    Private m_showStyle As NotificationShowStyle

    '
    ' is the mouse within the BlendPanel??
    '
    Private m_mouseInPanel As Boolean

    '
    ' are we being shown or hidden?
    '
    Private m_showing As Boolean

    '
    ' User-provided Tag to identify this window.
    '
    Private m_tag As Object

    '
    ' do we draw a close button or not?
    '
    Private m_closeButton As Boolean

    '
    ' Are we Right-to-left on RTL systems?
    '
    Private m_rightToLeft As Boolean

    '
    ' Is the mouse over the close button?
    '
    Private m_mouseOverClose As Boolean

    '
    ' why are we disappearing?
    '
    Private m_disappearReason As NotificationClosedReason



    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '                     Public Methods, Members, etc
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=


    '=----------------------------------------------------------------------=
    ' Constructor
    '=----------------------------------------------------------------------=
    ' Instantiate a new instance of th NotificationForm class, and set up
    ' all our views and structures based on what our parent gave us.
    '
    ' Parameters:
    '       NotificationWindow      - [in] parent component.
    '       String                  - [in]  Text to display
    '       Integer                 - [in]  Timeout in ms
    '       NotificationShowStyle   - [in]  how the form is to be shown.
    '
    Public Sub New(ByVal parent As NotificationWindow, _
                   ByVal in_tag As Object, _
                   ByVal in_text As String, _
                   ByVal in_timeout As Integer, _
                   ByVal in_cornerImage As Image, _
                   ByVal in_bottomImage As Image, _
                   ByVal in_textIsHyperLink As Boolean, _
                   ByVal in_font As Font, _
                   ByVal in_foreColour As Color, _
                   ByVal in_transparentColour As Color, _
                   ByVal in_closeButton As Boolean, _
                   ByVal in_showStyle As NotificationShowStyle, _
                   ByVal in_blend As BlendFill, _
                   ByVal in_rightToleft As Boolean)

        '
        ' set up the parent
        '
        System.Diagnostics.Debug.Assert(Not parent Is Nothing)
        Me.m_parent = parent

        '
        ' now set up the window  we will snapshot our values from what they 
        ' are set on the parent at this point in time.
        '
        initializeComponents(in_text, in_timeout, in_tag, in_cornerImage, _
                             in_bottomImage, in_textIsHyperLink, _
                             in_font, in_foreColour, in_transparentColour, _
                             in_closeButton, in_showStyle, _
                             in_blend, in_rightToleft)

    End Sub ' New


    '=----------------------------------------------------------------------=
    ' ShowNoActivate
    '=----------------------------------------------------------------------=
    ' Issue with WinForms implementation in .NET 1.1 -- 
    ' there is no way to show a top level window without it being activated.
    ' Work around by calling ShowWindow ourselves, then have to make the 
    ' WINFORMS engine think that our window is shown, so that subsequent calls 
    ' to Hide() will actually hide the window.
    '
    Public Sub ShowNoActivate()

        Dim p As Point

        '
        ' first, get the location of where we want to show the window.
        '
        p = getPreferredLocation()
        Me.Location = p
        If Me.m_showStyle = NotificationShowStyle.Fade Then
            Me.Opacity = 0.0
        ElseIf Me.m_showStyle = NotificationShowStyle.Slide Then
            Me.Size = New Size(DEFAULT_WIDTH, DEFAULT_HEIGHT / (1000 / Me.m_showTimer.Interval))
        End If
        Me.m_showing = True
        Me.m_showTimer.Start()

        '
        ' please see text comment for this method for an explanation of why
        ' we do this.
        '
        ShowWindow(Me.Handle, 8)
        Visible = True

        '
        ' finally, go and add this to the collection of visible windows.
        '
        addToFormsCollection()

    End Sub





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
    ' addToFormsCollection
    '=----------------------------------------------------------------------=
    ' adds the given form (us) to the global forms collection we're keeping
    ' for NotificationForms (this helps us figure out where to put new
    ' ones
    '
    Private Sub addToFormsCollection()

        If s_FormsCollection Is Nothing Then
            s_FormsCollection = New System.Collections.ArrayList
        End If

        s_FormsCollection.Add(Me)

    End Sub

    '=----------------------------------------------------------------------=
    ' removeFromFormsCollection
    '=----------------------------------------------------------------------=
    ' removes the given form (us) from the global forms collection we're 
    ' keeping for NotificationForms.
    '
    Private Sub removeFromFormsCollection()

        System.Diagnostics.Debug.Assert(Not s_FormsCollection Is Nothing)
        s_FormsCollection.Remove(Me)

    End Sub

    '=----------------------------------------------------------------------=
    ' getPreferredLocation
    '=----------------------------------------------------------------------=
    ' Figures out where:
    '
    ' 1. Where the other NotifiationForms are, so we can position ourselves
    '    correctly based on where they're at.
    ' 2. the TaskBar is.  This lets us figure out the general area where we
    '    show the NotificationForm
    '
    ' Returns:
    '       Point       - top,left of where this window should be positioned
    '
    Private Function getPreferredLocation() As Point

        Dim tbl As TaskBarLocation
        Dim reverse As Boolean
        Dim workingArea As Rectangle
        Dim pt As Point

        pt = New Point
        pt.X = 0 : pt.Y = 0

        reverse = getTaskBarStatusReverse()
        workingArea = SystemInformation.WorkingArea

        '
        ' 1. find out where the existing windows are and figure out
        '    how to place ourselves based on that.
        '
        tbl = getTaskBarLocation()

        '
        ' 2. depending on where the TaskBar is, look at what existing windows
        '    there are there, and place ourselves appropriately.
        '
        Select Case tbl

            Case TaskBarLocation.Top
                If reverse Then
                    pt.X = 0
                Else
                    pt.X = workingArea.Right - DEFAULT_WIDTH
                End If
                pt.Y = workingArea.Top
                If Not s_FormsCollection Is Nothing Then
                    For Each f As NotificationForm In s_FormsCollection
                        If f.Top + DEFAULT_HEIGHT > pt.Y Then
                            pt.Y = f.Top + DEFAULT_HEIGHT
                        End If
                    Next
                End If

            Case TaskBarLocation.Bottom
                If reverse Then
                    pt.X = 0
                Else
                    pt.X = workingArea.Right - DEFAULT_WIDTH
                End If
                pt.Y = workingArea.Bottom - DEFAULT_HEIGHT
                If Not s_FormsCollection Is Nothing Then
                    For Each f As NotificationForm In s_FormsCollection
                        If f.Top - DEFAULT_HEIGHT < pt.Y Then
                            pt.Y = f.top - DEFAULT_HEIGHT
                        End If
                    Next
                End If

            Case TaskBarLocation.Left
                If reverse Then
                    pt.Y = workingArea.Top
                    If Not s_FormsCollection Is Nothing Then
                        For Each f As NotificationForm In s_FormsCollection
                            If f.Top + DEFAULT_HEIGHT > pt.Y Then
                                pt.Y = f.Top + DEFAULT_HEIGHT
                            End If
                        Next
                    End If

                Else
                    pt.Y = workingArea.Bottom - DEFAULT_HEIGHT
                    If Not s_FormsCollection Is Nothing Then
                        For Each f As NotificationForm In s_FormsCollection
                            If f.Top - DEFAULT_HEIGHT < pt.Y Then
                                pt.Y = f.top - DEFAULT_HEIGHT
                            End If
                        Next
                    End If
                End If
                pt.X = workingArea.Left

            Case TaskBarLocation.Right
                If reverse Then
                    pt.Y = workingArea.Top
                    If Not s_FormsCollection Is Nothing Then
                        For Each f As NotificationForm In s_FormsCollection
                            If f.Top + DEFAULT_HEIGHT > pt.Y Then
                                pt.Y = f.Top + DEFAULT_HEIGHT
                            End If
                        Next
                    End If

                Else
                    pt.Y = workingArea.Bottom - DEFAULT_HEIGHT
                    If Not s_FormsCollection Is Nothing Then
                        For Each f As NotificationForm In s_FormsCollection
                            If f.Top - DEFAULT_HEIGHT < pt.Y Then
                                pt.Y = f.top - DEFAULT_HEIGHT
                            End If
                        Next
                    End If
                End If

                pt.X = workingArea.Right - DEFAULT_WIDTH

        End Select ' tbl

        '
        ' great, return this point
        '
        Return pt

    End Function ' getPreferredLocation


    '=----------------------------------------------------------------------=
    ' getTaskBarLocation
    '=----------------------------------------------------------------------=
    ' determines where the Windows Task Bar is
    '
    ' Returns:
    '       TaskBarLocation     - where is it?
    '
    Private Function getTaskBarLocation() As TaskBarLocation

        Dim r As Rectangle


        r = SystemInformation.WorkingArea

        If r.Top = 0 And r.Left = 0 And r.Width = SystemInformation.VirtualScreen.Width Then
            Return TaskBarLocation.Bottom
        ElseIf r.Left = 0 And Not r.Top = 0 Then
            Return TaskBarLocation.Top
        ElseIf Not r.Left = 0 And r.Top = 0 Then
            Return TaskBarLocation.Left
        Else
            Return TaskBarLocation.Right
        End If
    End Function ' getTaskBarLocation


    '=----------------------------------------------------------------------=
    ' getTaskBarStatusReverse
    '=----------------------------------------------------------------------=
    ' Indicates whether the TaskBar's Status Area (where all the little notify
    ' icon thingies are) is reversed from it's normal right/bottom position.
    ' This will be true on RTL sysetms such as Arabic/Hebrew.
    '
    ' Returns:
    '       Boolean     - False means default, True means RTL
    '
    Private Function getTaskBarStatusReverse() As Boolean

        Dim langid, primary As Integer

        '
        ' Using the system, see if we're on an Arabic or Hebrew system, in
        ' which case we'll show up left ...
        '
        langid = Win32Helper.GetUserDefaultUILanguage()
        primary = langid And &H3FF
        If primary = &H1 OrElse primary = &HD Then
            Return True
        Else
            Return False
        End If

    End Function ' getTaskBarStatusReverse


    '=----------------------------------------------------------------------=
    ' initializeComponents
    '=----------------------------------------------------------------------=
    ' Sets up and configures all the components on this window.
    '
    ' Parameters:
    Private Sub initializeComponents(ByVal in_text As String, _
                                     ByVal in_timeout As Integer, _
                                     ByVal in_tag As Object, _
                                     ByVal in_cornerImage As Image, _
                                     ByVal in_bottomImage As Image, _
                                     ByVal in_textIsHyperLink As Boolean, _
                                     ByVal in_font As Font, _
                                     ByVal in_foreColour As Color, _
                                     ByVal in_transparentColour As Color, _
                                     ByVal in_closeButton As Boolean, _
                                     ByVal in_showStyle As NotificationShowStyle, _
                                     ByVal in_blend As BlendFill, _
                                     ByVal in_rightToLeft As Boolean)

        Dim b As Bitmap

        Me.m_tag = in_tag
        Me.m_closeButton = in_closeButton
        Me.m_rightToLeft = in_rightToLeft

        Me.Size = New Size(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        Me.Location = New Point(100, 100)
        Me.StartPosition = FormStartPosition.Manual
        Me.ControlBox = False
        Me.MinimizeBox = False
        Me.MaximizeBox = False
        Me.FormBorderStyle = FormBorderStyle.None
        Me.ShowInTaskbar = False
        Me.AllowTransparency = True

        '
        ' these style bits are all to reduce the amount of flickering that
        ' goes on in this control ...
        '
        Me.SetStyle(ControlStyles.ResizeRedraw, False)
        Me.SetStyle(ControlStyles.DoubleBuffer, True)
        Me.SetStyle(ControlStyles.AllPaintingInWmPaint, True)

        '
        ' we'll put everything in a BlendPanel so we can have room to draw a
        ' big fattie border and save ourselves the hassle of doing a
        ' non(-client) area.
        '
        Me.m_panel = New BlendPanel
        Me.Controls.Add(Me.m_panel)
        Me.m_panel.Blend = in_blend
        If in_rightToLeft Then
            Me.m_panel.RightToLeft = RightToLeft.Yes
        Else
            Me.m_panel.RightToLeft = RightToLeft.No
        End If

        '
        ' Next, we need to get the image icon, compute its height, and make
        ' sure it's set to be properly transparent place, provided we have one.
        '
        If Not in_cornerImage Is Nothing Then
            Me.m_cornerImage = in_cornerImage.Clone()
            b = CType(Me.m_cornerImage, Bitmap)
            If Not b Is Nothing Then
                b.MakeTransparent(in_transparentColour)
            End If
        End If

        '
        ' Do the same with the bottom image.  These two iamges will actually
        ' be painted in the OnPaint for the BlendLabel ...
        '
        If Not in_bottomImage Is Nothing Then
            Me.m_bottomImage = in_bottomImage.Clone()
            b = CType(Me.m_bottomImage, Bitmap)
            If Not b Is Nothing Then
                b.MakeTransparent(in_transparentColour)
            End If
        End If

        '
        ' note: the text will be drawn by hand in the m_panel_Paint
        ' event handler.
        '
        Me.m_text = in_text
        Me.m_textIsHyperLink = in_textIsHyperLink
        Me.m_font = in_font
        Me.m_foreColour = in_foreColour

        '
        ' finally, set up the timers and their timeout periods
        '
        ' 1. Timeout timer (if time > 0)
        ' 2. Fade time (if necessary)
        '
        If Not in_timeout = 0 Then
            Me.m_timer = New Timer
            Me.m_timer.Interval = in_timeout
        End If
        Me.m_showStyle = in_showStyle
        Me.m_showTimer = New Timer
        Me.m_showTimer.Interval = TIMER_INTERVAL

        Me.m_mouseInPanel = False

    End Sub ' initializeComponents


    '=----------------------------------------------------------------------=
    ' m_panel_Paint
    '=----------------------------------------------------------------------=
    ' we'll paint the two images (Icon and BottomImage) directly on the 
    ' BlendPanel.  We might also have to draw the Close button there too.
    '
    Private Sub m_panel_Paint(ByVal sender As Object, ByVal e As System.Windows.Forms.PaintEventArgs) Handles m_panel.Paint

        Dim iconHeight, bottomImageHeight As Integer

        iconHeight = 0 : bottomImageHeight = 0

        '
        ' 1. Draw the Top Corner image
        '
        iconHeight = drawTopCornerImage(e.Graphics)

        '
        ' 2. Draw the bottom spanning image
        '
        bottomImageHeight = drawBottomImage(e.Graphics)

        '
        ' 3. close button? correct height if there is no top corner image.
        '
        drawCloseButton(e.Graphics)
        If Me.m_closeButton = True AndAlso iconHeight < 20 Then iconHeight = 20

        '
        ' 4. Draw the text
        '
        drawText(e.Graphics, iconHeight, Me.Height - iconHeight - bottomImageHeight)

    End Sub ' m_panel_Paint


    '=----------------------------------------------------------------------=
    ' drawTopCornerImage
    '=----------------------------------------------------------------------=
    ' draws the image in the top corner, if there is one.
    '
    ' Parameters:
    '       Graphics            - [in]  where to draw!
    '
    ' Returns:
    '       Integer             - height of the image/icon
    '
    Private Function drawTopCornerImage(ByVal in_graphics As Graphics) As Integer

        Dim iconHeight, iconWidth As Integer
        Dim toppy, lefty As Integer

        iconHeight = 0 : iconWidth = 0

        '
        ' draw the top left image.  figure out if it's to go on the
        ' right or left, and then draw it indented a couple of pixels.
        '
        If Not Me.m_cornerImage Is Nothing Then
            iconHeight = Me.m_cornerImage.Height
            If iconHeight > ICON_MAXHEIGHT Then iconHeight = ICON_MAXHEIGHT
            iconWidth = Me.m_cornerImage.Width
            If iconWidth > ICON_MAXWIDTH Then iconWidth = ICON_MAXWIDTH

            If Me.m_rightToLeft Then
                toppy = 2
                lefty = Me.m_panel.Width - iconWidth - 2
            Else
                toppy = 2
                lefty = 2
            End If

            in_graphics.DrawImage(Me.m_cornerImage, lefty, toppy, iconWidth, iconHeight)
            iconHeight += 2

        End If

        '
        ' Make sure we return this to the caller
        '
        Return iconHeight

    End Function ' drawTopCornerImage


    '=----------------------------------------------------------------------=
    ' drawBottomImage
    '=----------------------------------------------------------------------=
    ' If applicable, draw the bottom image across the bottom of the window,
    ' and then return the height of this image
    '
    ' Parameters:
    '       Graphics                - [in]  where to draw.
    '
    ' Returns:
    '       Integer                 - height in pixels of image drawn
    '
    Private Function drawBottomImage(ByVal in_graphics As Graphics) As Integer

        Dim bottomImageHeight, bottomImageWidth As Integer
        Dim lefty As Integer

        bottomImageHeight = 0 : bottomImageWidth = 0

        '
        ' draw the bottom spanning image.  we'll crop it if it's too big. We
        ' won't bother to reverse this for RTL systems unless it's too short.
        '
        If Not Me.m_bottomImage Is Nothing Then

            bottomImageHeight = Me.m_bottomImage.Height
            If bottomImageHeight > BOTTOMIMAGE_MAXHEIGHT Then
                bottomImageHeight = BOTTOMIMAGE_MAXHEIGHT
            End If
            bottomImageWidth = Me.m_bottomImage.Width
            If bottomImageWidth > Me.m_panel.Width Then
                bottomImageWidth = Me.m_panel.Width
            End If


            lefty = (Me.m_panel.Width - bottomImageWidth) / 2
            in_graphics.DrawImage(Me.m_bottomImage, 0, Me.m_panel.Height - bottomImageHeight, _
                                  New RectangleF(0, 0, bottomImageWidth, bottomImageHeight), _
                                  GraphicsUnit.Pixel)
        End If

        '
        ' Return the computed height (or zero)
        '
        Return bottomImageHeight

    End Function ' drawBottomImage


    '=----------------------------------------------------------------------=
    ' drawCloseButton
    '=----------------------------------------------------------------------=
    ' draws the close button, assuming that we have one to draw!
    '
    ' Parameters:
    '       Graphics            - [in]  where to draw!
    '
    Private Sub drawCloseButton(ByVal in_graphics As Graphics)

        Dim flags As Integer
        Dim hdc As IntPtr
        Dim rc As Win32Helper.RECT

        If Not Me.m_closeButton Then Return

        '
        ' Reverse this on RTL systems
        '
        If Me.m_rightToLeft Then
            rc.left = 3 : rc.top = 3
            rc.right = 18 : rc.bottom = 18
        Else
            rc.left = Me.m_panel.Width - 18 : rc.top = 3
            rc.right = Me.m_panel.Width - 3 : rc.bottom = 18
        End If

        If Me.m_mouseOverClose Then
            If Me.MouseButtons And MouseButtons.Left Then
                flags = &H1200
            Else
                flags = &H1000
            End If
        Else
            flags = 0
        End If

        '
        ' CONSIDER: It would be nice if
        '         there were a better function to use ... these buttons aren't
        '         as nice as the Windows XP-Themed buttons ...
        '
        hdc = in_graphics.GetHdc()
        Win32Helper.DrawFrameControl(hdc, rc, 1, flags)
        in_graphics.ReleaseHdc(hdc)

    End Sub ' drawCloseButton


    '=----------------------------------------------------------------------=
    ' drawText
    '=----------------------------------------------------------------------=
    ' draws the text for this notification window.  Not terribly complicated
    '
    ' Parameters:
    '       Graphics                - [in]  where we should draw.
    '       Integer                 - [in]  top of where to draw
    '       Integer                 - [in]  max height in which we can draw.
    '
    '
    Private Sub drawText(ByVal in_graphics As Graphics, _
                         ByVal in_top As Integer, _
                         ByVal in_height As Integer)

        ' 
        ' finally, draw the text
        '
        Dim sf As StringFormat
        Dim rf As RectangleF
        Dim fc As Color
        Dim ff As Font

        '
        ' add some special processing for the case where we're a hyperlink
        ' and need to display it as active:
        '
        If Me.m_textIsHyperLink = True And Me.m_mouseInPanel Then
            ff = New Font(Me.m_font, FontStyle.Underline)
            fc = SystemColors.HotTrack
        Else
            ff = Me.m_font
            fc = Me.m_foreColour
        End If

        rf = New RectangleF(0, in_top, Me.m_panel.Width, _
                            in_height)
        sf = New StringFormat
        sf.Alignment = StringAlignment.Center
        If Me.m_rightToLeft Then
            sf.FormatFlags = StringFormatFlags.DirectionRightToLeft
        End If
        in_graphics.DrawString(Me.m_text, ff, New SolidBrush(fc), _
                              rf, sf)

    End Sub ' drawText


    '=----------------------------------------------------------------------=
    ' OnLoad
    '=----------------------------------------------------------------------=
    ' this is called RIGHT before we are about to be shown.  We'll go ahead
    ' and start up the timer here, to be sure we timeout after an appropriate
    ' period of time.
    '
    Protected Overrides Sub OnLoad(ByVal e As System.EventArgs)
        MyBase.OnLoad(e)

        '
        ' start up the timer now, provided our timeout value isn't 0 (which
        ' implies don't ever time out)
        '
        If Not Me.m_timer Is Nothing Then
            Me.m_timer.Start()
        End If

    End Sub ' OnLoad


    '=----------------------------------------------------------------------=
    ' getCloseButtonRECT
    '=----------------------------------------------------------------------=
    ' Returns the CloseButton's bounding rect in RECT format.
    '
    ' Returns:
    '       RECT
    '
    Private Function getCloseButtonRECT() As Win32Helper.RECT

        Dim rc As Win32Helper.RECT
        Dim reverse As Boolean

        If Me.m_closeButton = False Then Return rc

        rc.top = 3
        rc.bottom = 18
        If Not Me.m_rightToLeft Then
            rc.left = Me.m_panel.Width - 18
            rc.right = Me.m_panel.Width - 3
        Else
            rc.left = 3
            rc.right = 18
        End If

        Return rc

    End Function ' getCloseButtonRECT


    '=----------------------------------------------------------------------=
    ' getCloseButtonRectangle
    '=----------------------------------------------------------------------=
    ' Returns the close button's rectangle in rectangle format.
    '
    ' Returns:
    '       Rectangle
    '
    Private Function getCloseButtonRectangle() As Rectangle

        Dim reverse As Boolean
        Dim rc As Rectangle

        If Me.m_closeButton = False Then Return New Rectangle(0, 0, 0, 0)

        If Not Me.m_rightToLeft Then
            rc = New Rectangle(Me.m_panel.Width - 18, 3, 15, 15)
        Else
            rc = New Rectangle(3, 3, 15, 15)
        End If

        Return rc

    End Function ' getCloseButtonAsRectangle


    '=----------------------------------------------------------------------=
    ' m_timer_Tick
    '=----------------------------------------------------------------------=
    ' Timed out.  Go ahead and fire the TimedOut event!
    '
    Private Sub m_timer_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles m_timer.Tick

        Dim f As Boolean

        Me.m_disappearReason = NotificationClosedReason.TimedOut
        f = raiseOnClosing(NotificationClosedReason.TimedOut)
        If Not f Then commenceDisappearing()

    End Sub


    '=----------------------------------------------------------------------=
    ' commenceDisappearing
    '=----------------------------------------------------------------------=
    ' Begin the process of going away.  We'll start the timer and then slowly
    ' fade/slide away.
    '
    Private Sub commenceDisappearing()

        If Not Me.m_timer Is Nothing Then
            Me.m_timer.Stop()
        End If
        Me.m_showing = False
        Me.m_showTimer.Start()

    End Sub


    '=----------------------------------------------------------------------=
    ' completeDisappearing
    '=----------------------------------------------------------------------=
    ' we're done the whole going away thing.  Go and actually disappear now
    ' and tear down any structures that are still there ...
    '
    Private Sub completeDisappearing()

        '
        ' We have to stop this right away, otherwise, they'll continue to
        ' fire during the OnClosed processing.
        '
        Me.m_showTimer.Stop()

        '
        ' fire the closed event, and then we'll go and destroy the window
        '
        raiseOnClosed(Me.m_disappearReason)

        removeFromFormsCollection()
        Me.Hide()
        Me.Dispose()

    End Sub ' completeDisappearing


    '=----------------------------------------------------------------------=
    ' m_panel_MouseEnter
    '=----------------------------------------------------------------------=
    ' For those cases where we have linked text, we'll go ahead and underline
    ' the text now.
    '
    Private Sub m_panel_MouseEnter(ByVal sender As Object, ByVal e As System.EventArgs) Handles m_panel.MouseEnter

        Me.m_mouseInPanel = True
        Me.m_panel.Refresh()
        Me.m_panel.Cursor = Cursors.Hand

    End Sub


    '=----------------------------------------------------------------------=
    ' m_panel_MouseLeave
    '=----------------------------------------------------------------------=
    ' For those cases where we have linked text, we'll revert the text to 
    ' normal now.
    '
    Private Sub m_panel_MouseLeave(ByVal sender As Object, ByVal e As System.EventArgs) Handles m_panel.MouseLeave

        Me.m_mouseInPanel = False
        Me.m_panel.Refresh()
        Me.m_panel.Cursor = Cursors.Default

    End Sub ' m_panel_MouseLeave


    '=----------------------------------------------------------------------=
    ' m_panel_MouseMove
    '=----------------------------------------------------------------------=
    ' Figure out if we need to update our little close button.
    '
    Private Sub m_panel_MouseMove(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles m_panel.MouseMove

        Dim r As Rectangle
        r = getCloseButtonRectangle()

        If e.X > r.Left AndAlso e.X < r.Right _
           AndAlso e.Y > r.Top AndAlso e.Y < r.Bottom Then

            Me.m_mouseOverClose = True
            Me.m_panel.Invalidate(r)

        Else
            Me.m_mouseOverClose = False
            Me.m_panel.Invalidate(r)
        End If

    End Sub ' m_panel_MouseMove


    '=----------------------------------------------------------------------=
    ' m_panel_MouseDown
    '=----------------------------------------------------------------------=
    ' Make sure we update buttons when the user presses over the X button
    '
    Private Sub m_panel_MouseDown(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles m_panel.MouseDown

        Dim r As Rectangle

        r = getCloseButtonRectangle()

        If r.Contains(e.X, e.Y) Then
            Me.Invalidate(r)
        End If

    End Sub ' m_panel_MouseDown


    '=----------------------------------------------------------------------=
    ' m_panel_Click
    '=----------------------------------------------------------------------=
    ' the user clicked on the BlendPanel.  Fire the Click Event
    '
    Private Sub m_panel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles m_panel.Click

        Dim abortCloseWindow As Boolean
        Dim rc As Rectangle

        abortCloseWindow = False

        '
        ' See if they clicked on the close button.  If so, then we're going
        ' away.  Period.
        '
        rc = getCloseButtonRectangle()
        If rc.Contains(Me.m_panel.PointToClient(Me.m_panel.MousePosition())) Then

            '
            ' They Clicked on the "X" close button!!!
            '
            Me.m_disappearReason = NotificationClosedReason.CloseClicked
            abortCloseWindow = raiseOnClosing(NotificationClosedReason.CloseClicked)

        Else

            '
            ' Just a regular click somewhere on the control.
            ' 1. fire the Click Event
            ' 2. initiate shutdown with the Closing event
            '
            ' Before firing the click, pause the timer, because otherwise the
            ' window might very well go away while they're processing the click.
            '
            raiseOnClick()

            Me.m_disappearReason = NotificationClosedReason.WindowClicked
            abortCloseWindow = raiseOnClosing(NotificationClosedReason.WindowClicked)

        End If

        '
        ' start going away then if appropriate.
        '
        If Not abortCloseWindow Then
            commenceDisappearing()
        End If

    End Sub ' m_panel_Click


    '=----------------------------------------------------------------------=
    ' OnPaint
    '=----------------------------------------------------------------------=
    ' we have to draw our 'border' here
    '
    ' We also have to draw the Close Button if the user wants us to show one.
    '
    Protected Overrides Sub OnPaint(ByVal e As System.Windows.Forms.PaintEventArgs)

        Dim w, h As Integer
        Dim g As Graphics
        g = e.Graphics

        w = DEFAULT_WIDTH : h = Me.Height

        '
        ' left edge
        '
        g.DrawLine(SystemPens.ControlLight, 0, 0, 0, h - 1)
        g.DrawLine(SystemPens.ControlLightLight, 1, 1, 1, h - 2)
        g.DrawLine(SystemPens.Control, 2, 2, 2, h - 3)
        g.DrawLine(SystemPens.ControlDark, 3, 3, 3, h - 4)
        g.DrawLine(SystemPens.ControlDarkDark, 4, 4, 4, h - 5)

        ' 
        ' top edge
        '
        g.DrawLine(SystemPens.ControlDarkDark, 4, 4, w - 5, 4)
        g.DrawLine(SystemPens.ControlDark, 3, 3, w - 4, 3)
        g.DrawLine(SystemPens.Control, 2, 2, w - 3, 2)
        g.DrawLine(SystemPens.ControlLightLight, 1, 1, w - 2, 1)
        g.DrawLine(SystemPens.ControlLight, 0, 0, w - 1, 0)

        '
        ' right edge
        '
        g.DrawLine(SystemPens.ControlDarkDark, w - 1, 0, w - 1, h - 1)
        g.DrawLine(SystemPens.ControlDark, w - 2, 1, w - 2, h - 2)
        g.DrawLine(SystemPens.Control, w - 3, 2, w - 3, h - 3)
        g.DrawLine(SystemPens.ControlLight, w - 4, 3, w - 4, h - 4)
        g.DrawLine(SystemPens.ControlLightLight, w - 5, 4, w - 5, h - 5)

        '
        ' bottom edge
        '
        g.DrawLine(SystemPens.ControlDarkDark, 0, h - 1, w - 1, h - 1)
        g.DrawLine(SystemPens.ControlDark, 1, h - 2, w - 2, h - 2)
        g.DrawLine(SystemPens.Control, 2, h - 3, w - 3, h - 3)
        g.DrawLine(SystemPens.ControlLight, 3, h - 4, w - 4, h - 4)
        g.DrawLine(SystemPens.ControlLightLight, 4, h - 5, w - 5, h - 5)

    End Sub ' OnPaint


    '=----------------------------------------------------------------------=
    ' m_showTimer_Tick
    '=----------------------------------------------------------------------=
    ' This controls how we are being shown or hidden.
    '
    Private Sub m_showTimer_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles m_showTimer.Tick

        '
        ' are we showing or hiding the window?
        '
        If Me.m_showing Then

            '
            ' if the ShowStyle is Fade, then go and fiddle with the opacity.
            '
            Select Case Me.m_showStyle
                Case NotificationShowStyle.Fade
                    Dim d As Double

                    d = (1000 / Me.m_showTimer.Interval) / 100
                    If Me.Opacity + d >= 1.0 Then
                        Me.Opacity = 1.0
                        Me.m_showTimer.Stop()
                    Else
                        Me.Opacity += d
                    End If

                Case NotificationShowStyle.Slide
                    '
                    ' Othewise, we're a Slide ShowStyle, and we need to increase
                    ' our size a little bit more.
                    '
                    Dim i As Integer
                    i = DEFAULT_HEIGHT / (1000 / Me.m_showTimer.Interval)
                    If Me.Height + i >= DEFAULT_HEIGHT Then
                        Me.Height = DEFAULT_HEIGHT
                        Me.m_showTimer.Stop()
                    Else
                        Me.Height += i
                    End If

                Case Else

                    Me.Show()
                    Me.m_showTimer.Stop()

            End Select

        Else

            '
            ' we're being asked to go away.  Are we a Fade or Slide window?
            '
            Select Case Me.m_showStyle

                Case NotificationShowStyle.Fade
                    Dim d As Double
                    d = (1000.0 / Me.m_showTimer.Interval) / 100.0

                    If Me.Opacity - d <= 0.0 Then
                        Me.Opacity = 0.0
                        completeDisappearing()
                    Else
                        Me.Opacity -= d
                    End If


                Case NotificationShowStyle.Slide
                    '
                    ' we're ShowStyle.Slide.  Decrease our size a little bit
                    ' at a time.
                    '
                    Dim i As Integer
                    i = DEFAULT_HEIGHT / (1000 / Me.m_showTimer.Interval)
                    If Me.Height - i <= 0 Then
                        Me.Height = 0
                        completeDisappearing()
                    Else
                        Me.Height -= i
                    End If


                Case Else

                    Me.Hide()
                    completeDisappearing()

            End Select

        End If ' me.m_showing = true

    End Sub ' m_showTimer_Tick


    '=----------------------------------------------------------------------=
    ' CreateParams
    '=----------------------------------------------------------------------=
    ' Issue: Setting the TopMost property in WinForms causes the
    ' window to be activated. Work around by just specify-ing the topmost _EX_ style 
    ' bit at window creation time.  
    '
    Protected Overrides ReadOnly Property CreateParams() As System.Windows.Forms.CreateParams

        Get
            Dim cp As CreateParams

            cp = MyBase.CreateParams

            '
            ' add WS_EX_TOPMOST and WS_EX_NOACTIVATE
            '
            cp.ExStyle = cp.ExStyle Or &H8 Or &H8000000
            Return cp
        End Get

    End Property


    '=----------------------------------------------------------------------=
    ' OnClosing
    '=----------------------------------------------------------------------=
    ' For those cases where the user aborts the Closing and/or just wants to
    ' close the Notification Window at their leisure, we still want the window
    ' to disappear in a cool manner and fire the "Closed" event.  This 
    ' override from our base class is how this is done!
    '
    Protected Overrides Sub OnClosing(ByVal e As System.ComponentModel.CancelEventArgs)

        e.Cancel = True

        Me.m_disappearReason = NotificationClosedReason.CloseMethod
        Me.commenceDisappearing()

    End Sub ' OnClosing



    '=----------------------------------------------------------------------=
    ' OnResize
    '=----------------------------------------------------------------------=
    ' This lets us peel the bottom border up and down property when the
    ' ShowStyle is Slide.
    '
    Protected Overrides Sub OnResize(ByVal e As System.EventArgs)

        If Not Me.m_panel Is Nothing Then
            Me.m_panel.SetBounds(BORDER_WIDTH, BORDER_WIDTH, _
                                 DEFAULT_WIDTH - 2 * BORDER_WIDTH, _
                                 Me.Height - 2 * BORDER_WIDTH)
        End If

    End Sub ' OnResize


    '=----------------------------------------------------------------------=
    ' raiseOnClosing
    '=----------------------------------------------------------------------=
    ' Raises the Closing event with our parent, first making sure to pause the
    ' timer.
    '
    ' Parameters:
    '       NotificationClosedReason        - [in]  why we're going away.
    '       
    ' Returns:
    '       Boolean                         - True means cancel close.
    '
    Private Function raiseOnClosing(ByVal in_reason As NotificationClosedReason) _
                                    As Boolean
        Dim cancel As Boolean

        If Not Me.m_timer Is Nothing Then Me.m_timer.Stop()
        cancel = Me.m_parent.OnClosing(in_reason, Me.m_tag, Me)
        If Not Me.m_timer Is Nothing AndAlso Not cancel Then Me.m_timer.Start()

        Return cancel

    End Function ' raiseOnClosing


    '=----------------------------------------------------------------------=
    ' raiseOnClosed
    '=----------------------------------------------------------------------=
    ' Raises the Closed event with our parent, first making sure to pause the
    ' timer.
    '
    ' Parameters:
    '       NotificationClosedReason        - [in]  why, oh why are we gone?
    '
    Private Sub raiseOnClosed(ByVal in_reason As NotificationClosedReason)

        If Not Me.m_timer Is Nothing Then Me.m_timer.Stop()
        Me.m_parent.OnClosed(in_reason, Me.m_tag, Me)

    End Sub ' raiseOnClosed


    '=----------------------------------------------------------------------=
    ' raiseOnClick
    '=----------------------------------------------------------------------=
    ' Causes us to raise the Click event with our parents.  we will first
    ' pause the timer.
    '
    Private Sub raiseOnClick()

        If Not Me.m_timer Is Nothing Then Me.m_timer.Stop()
        Me.m_parent.OnClick(Me.m_tag, Me)
        If Not Me.m_timer Is Nothing Then Me.m_timer.Start()

    End Sub ' raiseOnClick

End Class ' NotificationForm




'=--------------------------------------------------------------------------=
' NotificationEventArgs
'=--------------------------------------------------------------------------=
' Contains information about an NotificationWindow event.
'
'       
Public Class NotificationEventArgs
    Inherits System.EventArgs

    '
    ' Tag used to identify the window.
    '
    Private m_tag As Object

    '
    ' Handle to the window closed.
    '
    Private m_Handle As Form



    '=----------------------------------------------------------------------=
    ' Constructor
    '=----------------------------------------------------------------------=
    ' Initialises a new instance of this arg class.  
    '
    ' Parameters:
    '       Object                      - [in]  User provided Tag (optional)
    '       Form                        - [in]  Handle to closed window.
    '
    Public Sub New(ByVal in_tag As Object, _
                   ByVal in_handle As Form)

        Me.m_tag = in_tag
        Me.m_Handle = in_handle

    End Sub ' New


    '=----------------------------------------------------------------------=
    ' Tag
    '=----------------------------------------------------------------------=
    ' The user provided Tag
    '
    ' Type:
    '       Object
    '
    <LocalisableDescription("NotificationEventArgs.Tag")> _
    Public ReadOnly Property Tag() As Object
        Get
            Return Me.m_tag
        End Get
    End Property  ' Tag


    '=----------------------------------------------------------------------=
    ' Handle
    '=----------------------------------------------------------------------=
    ' A handle to the window about which the event is talking
    '
    ' Type:
    '       Form
    '
    <LocalisableDescription("NotificationEventArgs.Handle")> _
    Public ReadOnly Property Handle() As Form
        Get
            Return Me.m_Handle
        End Get
    End Property ' Handle



End Class ' NotificationClosedEventArgs    


'=--------------------------------------------------------------------------=
' NotificationClosedEventArgs
'=--------------------------------------------------------------------------=
' A NotifcationWindow has closed.  This arg class tells you which one and what
' the reason was.
'
'
Public Class NotificationClosedEventArgs
    Inherits NotificationEventArgs

    '
    ' Why was this notification winder closed?
    '
    Private m_reason As NotificationClosedReason



    '=----------------------------------------------------------------------=
    ' Constructor
    '=----------------------------------------------------------------------=
    ' Initialises a new instance of this arg class.  
    '
    ' Parameters:
    '       NotificationClosedReason    - [in]  why'd the window go away?
    '       Object                      - [in]  User provided Tag (optional)
    '       Form                        - [in]  Handle to closed window.
    '
    Public Sub New(ByVal in_reason As NotificationClosedReason, _
                   ByVal in_tag As Object, _
                   ByVal in_handle As Form)

        MyBase.New(in_tag, in_handle)
        Me.m_reason = in_reason

    End Sub ' New


    '=----------------------------------------------------------------------=
    ' Reason
    '=----------------------------------------------------------------------=
    ' Why did the window go away?
    '
    ' Type:
    '       NotificationClosedReason
    '
    <LocalisableDescription("NotificationClosedEventArgs.Reason")> _
    Public ReadOnly Property Reason() As NotificationClosedReason
        Get
            Return Me.m_reason
        End Get
    End Property ' Reason



End Class ' NotificationClosedEventArgs


'=--------------------------------------------------------------------------=
' NotificationCancelEventArgs
'=--------------------------------------------------------------------------=
' When the Click event is fired, gives the user a chance to cancel the 
' resulting Close
'
'
Public Class NotificationCancelEventArgs
    Inherits NotificationEventArgs

    '
    ' Is the user going to cancel this?
    '
    Private m_cancel As Boolean

    '
    ' Why was this notification winder closed?
    '
    Private m_reason As NotificationClosedReason




    '=----------------------------------------------------------------------=
    ' Constructor
    '=----------------------------------------------------------------------=
    ' Initialises a new instance of this arg class.  
    '
    ' Parameters:
    '       Object                      - [in]  User provided Tag (optional)
    '       Form                        - [in]  Handle to closed window.
    '
    Public Sub New(ByVal in_reason As NotificationClosedReason, _
                   ByVal in_tag As Object, _
                   ByVal in_handle As Form)

        MyBase.New(in_tag, in_handle)
        Me.m_cancel = False
        Me.m_reason = in_reason

    End Sub ' New


    '=----------------------------------------------------------------------=
    ' Reason
    '=----------------------------------------------------------------------=
    ' Why did the window go away?
    '
    ' Type:
    '       NotificationClosedReason
    '
    <LocalisableDescription("NotificationClosedEventArgs.Reason")> _
    Public ReadOnly Property Reason() As NotificationClosedReason
        Get
            Return Me.m_reason
        End Get
    End Property ' Reason




    '=----------------------------------------------------------------------=
    ' Cancel
    '=----------------------------------------------------------------------=
    ' Gives the user a chance to cancel the impending close.
    '
    ' Type:
    '       Boolean
    '
    <LocalisableDescription("NotificationCancelEventArgs.Cancel")> _
    Public Property Cancel() As Boolean
        Get
            Return Me.m_cancel
        End Get

        Set(ByVal in_newCancel As Boolean)
            Me.m_cancel = in_newCancel
        End Set

    End Property ' Cancel

End Class ' NotificationCancelEventArgs



