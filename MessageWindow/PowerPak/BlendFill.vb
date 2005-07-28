Option Strict Off
'-------------------------------------------------------------------------------
'<copyright file="BlendFill.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.Drawing
Imports System.Reflection
Imports System.Globalization
Imports System.ComponentModel
Imports System.Drawing.Drawing2D
Imports System.ComponentModel.Design.Serialization



'=--------------------------------------------------------------------------=
' BlendFill
'=--------------------------------------------------------------------------=
' A class that wraps a LinearGradientBrush into a VB-user friendly
' class that can be code gen'd and easily added to your controls.
'
'
<Editor(GetType(Design.BlendFillEditor), GetType(System.Drawing.Design.UITypeEditor)), _
 TypeConverter(GetType(BlendFill.BlendFillTypeConverter)), _
 Serializable()> _
Public Class BlendFill


	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'                      Private types/data
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=

	'
	' Blend style
	'
	Private m_style As BlendStyle

	'
	' Start Colour
	'
	Private m_startColour As Color

	'
	' End Colour
	'
	Private m_finishColour As Color





	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'                     Public Methods/Properties/etc
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=


	'=----------------------------------------------------------------------=
	' Constructor
	'=----------------------------------------------------------------------=
	' Initializes a new instance of this class.  Requires the blend style,
	' as well as the start and finish colour.
	'
	' 
	Public Sub New(ByVal in_blendStyle As BlendStyle, _
	   ByVal in_startColour As Color, _
	   ByVal in_finishColour As Color)

		If Not System.Enum.IsDefined(GetType(BlendStyle), in_blendStyle) Then
			Throw New ArgumentOutOfRangeException("in_blendStyle", "Invalid value of BlendStyle.")
		End If
		Me.m_style = in_blendStyle

		Me.m_startColour = in_startColour
		Me.m_finishColour = in_finishColour

	End Sub	' New


	'=----------------------------------------------------------------------=
	' Style
	'=----------------------------------------------------------------------=
	' The style of blend we represent
	'
	' Type:
	'       BlendStyle
	'
	<LocalisableDescription("BlendFill.Style"), _
	 Category("Appearance"), DefaultValue(BlendStyle.Vertical)> _
	Public ReadOnly Property Style() As BlendStyle
		Get
			Return Me.m_style
		End Get


	End Property	' BlendStyle

	'=----------------------------------------------------------------------=
	' StartColor
	'=----------------------------------------------------------------------=
	' Indicates the "starting" colour of the linear blend.
	'
	' Type:
	'       Color
	'
	<LocalisableDescription("BlendFill.StartColour"), _
	 Category("Appearance")> _
	Public ReadOnly Property StartColor() As Color

		Get
			Return Me.m_startColour
		End Get

	End Property	' StartColor


	'=----------------------------------------------------------------------=
	' FinishColor
	'=----------------------------------------------------------------------=
	' Indicates the "finising" colour of the linear blend operation.
	'
	' Type:
	'       Color
	'
	<LocalisableDescription("BlendFill.FinishColour"), _
	 Category("Appearance")> _
	Public ReadOnly Property FinishColor() As Color

		Get
			Return Me.m_finishColour
		End Get

	End Property	' FinishColor


	'=----------------------------------------------------------------------=
	' GetLinearGradientBrush
	'=----------------------------------------------------------------------=
	' Returns a LinearGradient brush for the currently set values.
	'
	' Parameters:
	'       Rectangle               - [in]  the bounding rectfor the drawing
	'
	' Returns:
	'       System.Drawing.Drawing2D.LinearGradientBrush
	'
	<LocalisableDescription("BlendFill.GetLinearGradientBrush"), _
	 Category("Appearance")> _
	Public Function GetLinearGradientBrush(ByVal in_rect As Rectangle) _
	   As System.Drawing.Drawing2D.LinearGradientBrush

		'
		' Use the overloaded version
		'
		Return Me.GetLinearGradientBrush(in_rect, False)

	End Function	' GetLinearGradientBrush

	'=----------------------------------------------------------------------=
	' GetLinearGradientBrush
	'=----------------------------------------------------------------------=
	' Returns a LinearGradientBrush for the currently set values, letting the
	' caller specify whether we should reverse the values for RTL painting.
	'
	' Parameters:
	'       Rectangle               - [in]  the bounding rectfor the drawing
	'       Boolean                 - [in]  True = Reverse values for RTL 
	'
	' Returns:
	'       LinearGradientBrush
	'
	<LocalisableDescription("BlendFill.GetLinearGradientBrush2"), _
	 Category("Appearance")> _
	Public Function GetLinearGradientBrush(ByVal in_rect As Rectangle, _
	   ByVal in_reverseForRTL As Boolean) _
	   As LinearGradientBrush

		'
		' Issue with WinForms LinearGradientBrush:
		' If an angle of 180 degrees is specified, it doesn't
		' draw the left most pixel in the rectangle.  Thus, instead of 
		' trying to work around with pixels and rect boundaries, we're just going
		' to swap the colours on RTL systems with a Horizontal Gradient.
		' Otherwise, we'll go with the normal code paths to do this.
		'
		If in_reverseForRTL And Me.m_style = BlendStyle.Horizontal Then
			Return New LinearGradientBrush(in_rect, Me.m_finishColour, Me.m_startColour, 0)
		Else
			Return New LinearGradientBrush(in_rect, _
				Me.m_startColour, _
				Me.m_finishColour, _
				getAngle(Me.m_style, in_reverseForRTL))
		End If

	End Function	' GetLinearGradientBrush









	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'                   Private Methods/Properties/Subs
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=


	'=----------------------------------------------------------------------=
	' getAngle
	'=----------------------------------------------------------------------=
	' Returns an angle for a LinearGradientBrush given a direction/style
	'
	' Parameters:
	'       Integer         - [in]  style/direction
	'       Boolean         - [in]  should we reverse for RTL reading on Bidi?
	'
	' Returns:
	'       Single          - angle to draw.
	'
	Private Shared Function getAngle(ByVal in_direction As Integer, _
	   ByVal in_reverseForRTL As Boolean) _
	   As Single

		Select Case in_direction

			Case BlendStyle.Horizontal
				If in_reverseForRTL Then
					Return 180S
				Else
					Return 0S
				End If

			Case BlendStyle.Vertical
				Return 90S

			Case BlendStyle.ForwardDiagonal
				If in_reverseForRTL Then
					Return 135S
				Else
					Return 45S
				End If

			Case BlendStyle.BackwardDiagonal
				If in_reverseForRTL Then
					Return 45S
				Else
					Return 135S
				End If

			Case Else
				System.Diagnostics.Debug.Fail("Invalid direction.")
				Return 0S
		End Select

	End Function	' getAngle








	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'                            Nested Classes
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=
	'=----------------------------------------------------------------------=


	'=----------------------------------------------------------------------=
	' BlendFillTypeConverter
	'=----------------------------------------------------------------------=
	' This class provides design time functionalities for our
	' BlendFill class, as well as the ability to Code-Gen it.
	'
	' To do this, it inherits and implements methods on the TypeConverter class ...
	'
	'
	Public Class BlendFillTypeConverter
		Inherits TypeConverter


		'=------------------------------------------------------------------=
		' CanConvertTo
		'=------------------------------------------------------------------=
		' We support conversion to String as well as InstanceDescriptor
		' format, which makes it a bit easier on us in code generation.
		'
		'
		Public Overloads Overrides Function CanConvertTo(ByVal context As System.ComponentModel.ITypeDescriptorContext, ByVal destinationType As System.Type) As Boolean

			If destinationType Is GetType(String) _
			   OrElse destinationType Is GetType(InstanceDescriptor) Then

				Return True
			End If

			Return MyBase.CanConvertTo(context, destinationType)

		End Function		  ' CanConvertTo


		'=------------------------------------------------------------------=
		' ConvertTo
		'=------------------------------------------------------------------=
		' This is how we convert ourselves to a string or an Instance-
		' Descriptor, which is used in Code Generation.
		'
		'
		Public Overloads Overrides Function ConvertTo(ByVal context As System.ComponentModel.ITypeDescriptorContext, ByVal culture As System.Globalization.CultureInfo, ByVal value As Object, ByVal destinationType As System.Type) As Object

			Dim ci As ConstructorInfo
			Dim bf As BlendFill

			'
			' We'll only do something if they're asking us to convert a 
			' BlendFill object, of course ...
			'
			bf = CType(value, BlendFill)
			If Not bf Is Nothing Then
				'
				' What type do they want?
				'
				If destinationType Is GetType(InstanceDescriptor) Then

					'
					' Get the constructor that takes the style, and two
					' colours
					'
					ci = GetType(BlendFill).GetConstructor(New Type() { _
					   GetType(BlendStyle), _
					   GetType(Color), _
					   GetType(Color)})

					If Not ci Is Nothing Then

						'
						' Return the values for this constructor.
						'
						Return New InstanceDescriptor(ci, New Object() { _
						 bf.Style, _
						 bf.StartColor, _
						 bf.FinishColor})

					End If

				ElseIf destinationType Is GetType(String) Then

					Return blendFillToString(bf, culture)

				End If
			End If

			Return MyBase.ConvertTo(context, culture, value, destinationType)

		End Function		  ' ConvertTo

		'=------------------------------------------------------------------=
		' ConvertFrom
		'=------------------------------------------------------------------=
		' You can convert from Strings (of a certain type) to this object.
		'
		Public Overloads Overrides Function ConvertFrom(ByVal context As System.ComponentModel.ITypeDescriptorContext, ByVal culture As System.Globalization.CultureInfo, ByVal value As Object) As Object

			Dim bf As String

			'
			' If they gave us a string, then we'll try our best to parse it 
			' out.
			'
			bf = CType(value, String)
			If Not bf Is Nothing Then

				Return blendFillFromString(bf.Trim(), culture)
			End If

			MyBase.ConvertFrom(context, culture, value)

		End Function		  ' ConvertFrom


		'=------------------------------------------------------------------=
		' CanConvertFrom
		'=------------------------------------------------------------------=
		' You can convert from Strings (of a certain type) to this object.
		'
		'
		Public Overloads Overrides Function CanConvertFrom(ByVal context As System.ComponentModel.ITypeDescriptorContext, ByVal sourceType As System.Type) As Boolean

			If sourceType Is GetType(String) Then Return True
			Return MyBase.CanConvertFrom(context, sourceType)

		End Function		  ' CanConvertFrom


		'=------------------------------------------------------------------=
		' parseBlendStyle
		'=------------------------------------------------------------------=
		' Given the string value of a blend style, parse it back to an int
		'
		' Parameters:
		'       String          - [in]  BlendStyle value.
		'
		' Returns:
		'       BlendStyle      - enumerated integer
		'
		Private Shared Function parseBlendStyle(ByVal in_val As String) As BlendStyle

			Dim names() As String
			Dim x As Integer

			System.Diagnostics.Debug.Assert(Not in_val Is Nothing)
			in_val = in_val.Trim()

			'
			' Okay, get the list of names in the Enumeration.
			'
			names = System.Enum.GetNames(GetType(BlendStyle))
			For x = 0 To names.Length - 1
				If names(x).Equals(in_val) Then Return x
			Next

			Return -1

		End Function		  ' parseBlendStyle


		'=------------------------------------------------------------------=
		' blendFillToString
		'=------------------------------------------------------------------=
		' Converts a blend fill object to a string, using Culture Sensitive
		' separators and using text values where possible.
		'
		' Parameters:
		'       BlendFill               - [in]  convert me
		'       CultureInfo             - [in]  where to get culture data
		'
		' Returns:
		'       String
		'
		Private Shared Function blendFillToString(ByVal in_bf As BlendFill, _
		   ByVal in_culture As CultureInfo) _
		   As String

			Dim sb As System.Text.StringBuilder
			Dim tci, tcc As TypeConverter
			Dim sep, c1, c2 As String
			Dim args(2) As String

			'
			' Get appropriate conveters and culture data
			'
			tci = TypeDescriptor.GetConverter(GetType(Integer))
			tcc = TypeDescriptor.GetConverter(GetType(Color))
			If in_culture Is Nothing Then in_culture = CultureInfo.CurrentCulture
			sep = in_culture.TextInfo.ListSeparator & " "

			'
			' Get the style as a string
			'
			args(0) = System.Enum.GetName(GetType(BlendStyle), in_bf.Style)

			'
			' start colour
			'
			args(1) = tcc.ConvertToString(in_bf.StartColor)

			'
			' Finish colour
			'
			args(2) = tcc.ConvertToString(in_bf.FinishColor)

			'
			' Generate the string.  We have to wrap the colours in () so that
			' ARGB specified ones can be determined later ...
			'
			sb = New System.Text.StringBuilder

			sb.Append(args(0))
			sb.Append(sep)
			sb.Append("(")
			sb.Append(args(1))
			sb.Append(")")
			sb.Append(sep)
			sb.Append("(")
			sb.Append(args(2))
			sb.Append(")")

			Return sb.ToString()

		End Function		  ' blendFillToString


		'=------------------------------------------------------------------=
		' blendFillFromString
		'=------------------------------------------------------------------=
		' Given a string that we serialised out using blendFillToString, this
		' function attempts to parse in the given input and regenerate a 
		' BlendFill object.
		'
		' Parameters:
		'       String              - [in]  what to parse
		'       CultureInfo         - [in]  what locale to use for parsing
		'
		' Returns:
		'       BlendFill
		'
		Private Shared Function blendFillFromString(ByVal in_bf As String, _
			 ByVal in_culture As CultureInfo) _
			 As BlendFill
			Dim tcc As TypeConverter
			Dim style As BlendStyle
			Dim pieces() As String
			Dim c1, c2 As Color
			Dim sep As String

			'
			' Get the various type converters and culture info we need
			'
			If in_culture Is Nothing Then in_culture = CultureInfo.CurrentCulture
			sep = in_culture.TextInfo.ListSeparator
			tcc = TypeDescriptor.GetConverter(GetType(Color))

			'
			' Explode the string.  Unfortunately, we can using String.Split()
			' since we need to preserve ()s around the colours.
			'
			pieces = MiscFunctions.ExplodePreservingSubObjects(in_bf, sep, "(", ")")

			If Not pieces.Length = 3 Then
				Throw New ArgumentException("excBlendFillParse", "value")
			End If

			style = parseBlendStyle(pieces(0))
			c1 = tcc.ConvertFromString(pieces(1))
			c2 = tcc.ConvertFromString(pieces(2))

			If style = -1 OrElse c1.Equals(Color.Empty) OrElse c2.Equals(Color.Empty) Then
				Throw New ArgumentException("excBlendFillParse", "value")
			End If

			Return New BlendFill(style, c1, c2)

		End Function		  ' blendFillFromString

	End Class	' BlendFillTypeConverter




End Class ' BlendFill





