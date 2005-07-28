Option Strict Off
'-------------------------------------------------------------------------------
'<copyright file="MiscFunctions.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.Drawing


'=--------------------------------------------------------------------------=
' MiscFunctions
'=--------------------------------------------------------------------------=
' Module (not class) for utility methods.
'
'
Friend Module MiscFunctions



    '=---------------------------------------------------------------------=
    ' ExplodePreservingSubObjects
    '=---------------------------------------------------------------------=
    ' Given a string that contains a bunch of values separated by a given 
    ' list separator, split them out, with the added twist of keeping objects
    ' wrapped in the specified start and end wrappers intact.
    '
    ' I.e.
    '       If the separator were ",", start and end were ( and ) resp, then:
    '
    '       Woooba, (eeeek, wonk, aack!), (234, 324, 394.404)
    '
    '       would return:
    '
    '       Wooba
    '       eeeek, wonk, aack!
    '       234, 324, 394.404
    '
    ' Parameters:
    '       String                  - [in]  string to explode.
    '       String                  - [in]  separator
    '       String                  - [in]  sub-object start marker.
    '       String                  - [in]  sub-object finish marker.
    '
    ' Returns:
    '       String()
    '
    Public Function ExplodePreservingSubObjects(ByVal in_str As String, _
                                                ByVal in_sep As String, _
                                                ByVal in_start As String, _
                                                ByVal in_finish As String) _
                                                As String()

        Dim al As System.Collections.ArrayList
        Dim inSubObject As Integer
        Dim start As Integer
        Dim idx As Integer
        Dim s As String

        al = New System.Collections.ArrayList

        '
        ' loop through one character at a time looking for separator, etc.
        '
        While idx < in_str.Length

            If in_str.Chars(idx) = in_start Then
                inSubObject += 1
            ElseIf in_str.Chars(idx) = in_finish Then
                inSubObject -= 1
            End If

            '
            ' If we are at a separator, and aren't in a sub-object, then
            ' split out the string, stripping off the sub-object markers.
            '
            If in_str.Chars(idx) = in_sep AndAlso inSubObject = 0 Then
                s = in_str.Substring(start, idx - start).Trim()
                If s.Chars(0) = in_start Then
                    s = s.Substring(1, s.Length - 2)
                End If
                al.Add(s)
                start = idx + 1
            End If

            idx += 1

        End While

        '
        ' Finally add what's left!
        '
        s = in_str.Substring(start, idx - start).Trim()
        If s.Chars(0) = in_start Then
            s = s.Substring(1, s.Length - 2)
        End If
        al.Add(s)

        Return al.ToArray(GetType(String))

    End Function ' ExplodePreservingSubObjects


    '=---------------------------------------------------------------------=
    ' GetRightToLeftValue
    '=---------------------------------------------------------------------=
    ' given a control, figure out if it should be drawn Right To Left, which
    ' might involve going up the parent chain.
    '
    ' Returns:
    '       Boolean                 - True, draw RTL
    '
    Public Function GetRightToLeftValue(ByVal in_ctl As System.Windows.Forms.Control) _
                                        As Boolean

        If in_ctl.RightToLeft = Windows.Forms.RightToLeft.Yes Then Return True
        If in_ctl.RightToLeft = Windows.Forms.RightToLeft.No Then Return False
        If in_ctl.Parent Is Nothing Then Return False

        If in_ctl.RightToLeft = Windows.Forms.RightToLeft.Inherit Then
            Return GetRightToLeftValue(in_ctl.Parent)
        End If

    End Function ' GetRightToLeftValue


    '=---------------------------------------------------------------------=
    ' FlipColour
    '=---------------------------------------------------------------------=
    ' Takes a colour and returns a new one with all the values inverted 
    ' inside of 255
    '
    ' Parameters:
    '       Color
    '
    ' Returns:
    '       Color
    '
    Public Function FlipColour(ByVal in_colour As Color) As Color

        Return Color.FromArgb(in_colour.A, 255 - in_colour.R, 255 - in_colour.G, _
                              255 - in_colour.B)

    End Function ' FlipColour

    '=---------------------------------------------------------------------=
    ' IconToBitmap
    '=---------------------------------------------------------------------=
    ' converts a System.Drawing.Icon to a System.Drawing.Bitmap
    '
    ' Parameters:
    '       Icon                - [in]  icon to draw.
    '
    ' Returns:
    '       Bitmap
    '
    Public Function IconToBitmap(ByVal in_colour As Color, ByVal in_icon As Icon) As Bitmap

        Dim g As Graphics
        Dim b As Bitmap
        Dim c As Color

        b = New Bitmap(in_icon.Width, in_icon.Height, System.Drawing.Imaging.PixelFormat.Format32bppPArgb)
        g = Graphics.FromImage(b)
        g.FillRectangle(New SolidBrush(Color.Black), New Rectangle(0, 0, b.Width, b.Height))
        g.DrawIcon(in_icon, 0, 0)
        g.Dispose()

        b.MakeTransparent(Color.Black)


        '        b = in_icon.ToBitmap()
        '        b.MakeTransparent(Color.Black)
        Return b

    End Function ' IconToBitmap


    '=---------------------------------------------------------------------=
    ' ScaleColour
    '=---------------------------------------------------------------------=
    ' A pretty terrible function for scaling a colour down a certain 
    ' percentage
    '
    ' Parameters:
    '       Color               - [in]  colour to be scaled
    '       Integer             - [in]  Percent to scale it
    '
    ' Returns:
    '       Color               - scaled colour object.
    '
    Public Function ScaleColour(ByVal in_colour As Color, ByVal in_pct As Integer) As Color

        Dim d As Double
        Dim r, g, b As Integer

        d = in_pct / 100.0

        r = in_colour.R * d
        If r > 255 Then r = 255
        If g < 0 Then g = 0
        g = in_colour.G * d
        If g > 255 Then g = 255
        If g < 0 Then g = 0
        b = in_colour.B * d
        If b > 255 Then b = 255
        If b < 0 Then b = 0

        Return Color.FromArgb(in_colour.A, r, g, b)

    End Function

End Module
