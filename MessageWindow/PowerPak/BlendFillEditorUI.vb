Option Strict Off
'-------------------------------------------------------------------------------
'<copyright file="BlendFillEditorUI.vb" company="Microsoft">
'   Copyright (c) Microsoft Corporation. All rights reserved.
'</copyright>
'
' THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
' KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
' PARTICULAR PURPOSE.
'-------------------------------------------------------------------------------

Imports System.Drawing
Imports System.Windows.Forms
Imports System.ComponentModel
Imports System.Drawing.Drawing2D
Imports System.Windows.Forms.Design


'=--------------------------------------------------------------------------=
' BlendFillEditorUI
'=--------------------------------------------------------------------------=
' This is the design time UITypeEditor for the BlendFill class.
'
'
<ToolboxItem(False)> _
Public Class BlendFillEditorUI
    Inherits System.Windows.Forms.UserControl

    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '                      Private types/data
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=

    '
    ' current blend direction.
    '
    Private m_direction As BlendStyle

    '
    ' Start Colour
    '
    Private m_startColour As Color

    '
    ' Finish Colour
    '
    Private m_finishColour As Color

    '
    ' Are we reversed for RTL?
    '
    Private m_reverse As Boolean


    Private m_svc As IWindowsFormsEditorService


#Region " Windows Form Designer generated code "

    Public Sub New(ByVal in_svc As IWindowsFormsEditorService, _
                   ByVal in_blendFill As BlendFill, _
                   ByVal in_reverse As Boolean)
        MyBase.New()

        'This call is required by the Windows Form Designer.
        InitializeComponent()

        'Add any initialization after the InitializeComponent() call

        Me.m_svc = in_svc

        '
        ' Save out the values we were given.
        '
        Me.m_direction = in_blendFill.Style
        Me.m_startColour = in_blendFill.StartColor
        Me.m_finishColour = in_blendFill.FinishColor
        Me.m_reverse = in_reverse

        '
        ' Populate and select values in the appropriate list boxes.
        '
        Dim rm As System.Resources.ResourceManager
        rm = New System.Resources.ResourceManager(GetType(BlendFillEditorUI))
        populateDirectionListBox(rm)
        populateAndSelectColourList(Me.startColourList, Me.m_startColour, rm)
        populateAndSelectColourList(Me.finishColourList, Me.m_finishColour, rm)

    End Sub ' New


    'Form overrides dispose to clean up the component list.
    Protected Overloads Overrides Sub Dispose(ByVal disposing As Boolean)
        If disposing Then
            If Not (components Is Nothing) Then
                components.Dispose()
            End If
        End If
        MyBase.Dispose(disposing)
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    Friend WithEvents mainTab As System.Windows.Forms.TabControl
    Friend WithEvents directionPage As System.Windows.Forms.TabPage
    Friend WithEvents startColourPage As System.Windows.Forms.TabPage
    Friend WithEvents finishColourPage As System.Windows.Forms.TabPage
    Friend WithEvents directionComboBox As System.Windows.Forms.ComboBox
    Friend WithEvents startColourList As System.Windows.Forms.ListBox
    Friend WithEvents finishColourList As System.Windows.Forms.ListBox
    Friend WithEvents blendSamplePanel As System.Windows.Forms.Panel
    <System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
        Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(BlendFillEditorUI))
        Me.mainTab = New System.Windows.Forms.TabControl
        Me.directionPage = New System.Windows.Forms.TabPage
        Me.blendSamplePanel = New System.Windows.Forms.Panel
        Me.directionComboBox = New System.Windows.Forms.ComboBox
        Me.startColourPage = New System.Windows.Forms.TabPage
        Me.startColourList = New System.Windows.Forms.ListBox
        Me.finishColourPage = New System.Windows.Forms.TabPage
        Me.finishColourList = New System.Windows.Forms.ListBox
        Me.mainTab.SuspendLayout()
        Me.directionPage.SuspendLayout()
        Me.startColourPage.SuspendLayout()
        Me.finishColourPage.SuspendLayout()
        Me.SuspendLayout()
        '
        'mainTab
        '
        Me.mainTab.AccessibleDescription = resources.GetString("mainTab.AccessibleDescription")
        Me.mainTab.AccessibleName = resources.GetString("mainTab.AccessibleName")
        Me.mainTab.Alignment = CType(resources.GetObject("mainTab.Alignment"), System.Windows.Forms.TabAlignment)
        Me.mainTab.Anchor = CType(resources.GetObject("mainTab.Anchor"), System.Windows.Forms.AnchorStyles)
        Me.mainTab.Appearance = CType(resources.GetObject("mainTab.Appearance"), System.Windows.Forms.TabAppearance)
        Me.mainTab.BackgroundImage = CType(resources.GetObject("mainTab.BackgroundImage"), System.Drawing.Image)
        Me.mainTab.Controls.Add(Me.directionPage)
        Me.mainTab.Controls.Add(Me.startColourPage)
        Me.mainTab.Controls.Add(Me.finishColourPage)
        Me.mainTab.Dock = CType(resources.GetObject("mainTab.Dock"), System.Windows.Forms.DockStyle)
        Me.mainTab.Enabled = CType(resources.GetObject("mainTab.Enabled"), Boolean)
        Me.mainTab.Font = CType(resources.GetObject("mainTab.Font"), System.Drawing.Font)
        Me.mainTab.ImeMode = CType(resources.GetObject("mainTab.ImeMode"), System.Windows.Forms.ImeMode)
        Me.mainTab.ItemSize = CType(resources.GetObject("mainTab.ItemSize"), System.Drawing.Size)
        Me.mainTab.Location = CType(resources.GetObject("mainTab.Location"), System.Drawing.Point)
        Me.mainTab.Name = "mainTab"
        Me.mainTab.Padding = CType(resources.GetObject("mainTab.Padding"), System.Drawing.Point)
        Me.mainTab.RightToLeft = CType(resources.GetObject("mainTab.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.mainTab.SelectedIndex = 0
        Me.mainTab.ShowToolTips = CType(resources.GetObject("mainTab.ShowToolTips"), Boolean)
        Me.mainTab.Size = CType(resources.GetObject("mainTab.Size"), System.Drawing.Size)
        Me.mainTab.TabIndex = CType(resources.GetObject("mainTab.TabIndex"), Integer)
        Me.mainTab.Text = resources.GetString("mainTab.Text")
        Me.mainTab.Visible = CType(resources.GetObject("mainTab.Visible"), Boolean)
        '
        'directionPage
        '
        Me.directionPage.AccessibleDescription = resources.GetString("directionPage.AccessibleDescription")
        Me.directionPage.AccessibleName = resources.GetString("directionPage.AccessibleName")
        Me.directionPage.Anchor = CType(resources.GetObject("directionPage.Anchor"), System.Windows.Forms.AnchorStyles)
        Me.directionPage.AutoScroll = CType(resources.GetObject("directionPage.AutoScroll"), Boolean)
        Me.directionPage.AutoScrollMargin = CType(resources.GetObject("directionPage.AutoScrollMargin"), System.Drawing.Size)
        Me.directionPage.AutoScrollMinSize = CType(resources.GetObject("directionPage.AutoScrollMinSize"), System.Drawing.Size)
        Me.directionPage.BackgroundImage = CType(resources.GetObject("directionPage.BackgroundImage"), System.Drawing.Image)
        Me.directionPage.Controls.Add(Me.blendSamplePanel)
        Me.directionPage.Controls.Add(Me.directionComboBox)
        Me.directionPage.Dock = CType(resources.GetObject("directionPage.Dock"), System.Windows.Forms.DockStyle)
        Me.directionPage.Enabled = CType(resources.GetObject("directionPage.Enabled"), Boolean)
        Me.directionPage.Font = CType(resources.GetObject("directionPage.Font"), System.Drawing.Font)
        Me.directionPage.ImageIndex = CType(resources.GetObject("directionPage.ImageIndex"), Integer)
        Me.directionPage.ImeMode = CType(resources.GetObject("directionPage.ImeMode"), System.Windows.Forms.ImeMode)
        Me.directionPage.Location = CType(resources.GetObject("directionPage.Location"), System.Drawing.Point)
        Me.directionPage.Name = "directionPage"
        Me.directionPage.RightToLeft = CType(resources.GetObject("directionPage.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.directionPage.Size = CType(resources.GetObject("directionPage.Size"), System.Drawing.Size)
        Me.directionPage.TabIndex = CType(resources.GetObject("directionPage.TabIndex"), Integer)
        Me.directionPage.Text = resources.GetString("directionPage.Text")
        Me.directionPage.ToolTipText = resources.GetString("directionPage.ToolTipText")
        Me.directionPage.Visible = CType(resources.GetObject("directionPage.Visible"), Boolean)
        '
        'blendSamplePanel
        '
        Me.blendSamplePanel.AccessibleDescription = resources.GetString("blendSamplePanel.AccessibleDescription")
        Me.blendSamplePanel.AccessibleName = resources.GetString("blendSamplePanel.AccessibleName")
        Me.blendSamplePanel.Anchor = CType(resources.GetObject("blendSamplePanel.Anchor"), System.Windows.Forms.AnchorStyles)
        Me.blendSamplePanel.AutoScroll = CType(resources.GetObject("blendSamplePanel.AutoScroll"), Boolean)
        Me.blendSamplePanel.AutoScrollMargin = CType(resources.GetObject("blendSamplePanel.AutoScrollMargin"), System.Drawing.Size)
        Me.blendSamplePanel.AutoScrollMinSize = CType(resources.GetObject("blendSamplePanel.AutoScrollMinSize"), System.Drawing.Size)
        Me.blendSamplePanel.BackgroundImage = CType(resources.GetObject("blendSamplePanel.BackgroundImage"), System.Drawing.Image)
        Me.blendSamplePanel.Dock = CType(resources.GetObject("blendSamplePanel.Dock"), System.Windows.Forms.DockStyle)
        Me.blendSamplePanel.Enabled = CType(resources.GetObject("blendSamplePanel.Enabled"), Boolean)
        Me.blendSamplePanel.Font = CType(resources.GetObject("blendSamplePanel.Font"), System.Drawing.Font)
        Me.blendSamplePanel.ImeMode = CType(resources.GetObject("blendSamplePanel.ImeMode"), System.Windows.Forms.ImeMode)
        Me.blendSamplePanel.Location = CType(resources.GetObject("blendSamplePanel.Location"), System.Drawing.Point)
        Me.blendSamplePanel.Name = "blendSamplePanel"
        Me.blendSamplePanel.RightToLeft = CType(resources.GetObject("blendSamplePanel.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.blendSamplePanel.Size = CType(resources.GetObject("blendSamplePanel.Size"), System.Drawing.Size)
        Me.blendSamplePanel.TabIndex = CType(resources.GetObject("blendSamplePanel.TabIndex"), Integer)
        Me.blendSamplePanel.Text = resources.GetString("blendSamplePanel.Text")
        Me.blendSamplePanel.Visible = CType(resources.GetObject("blendSamplePanel.Visible"), Boolean)
        '
        'directionComboBox
        '
        Me.directionComboBox.AccessibleDescription = resources.GetString("directionComboBox.AccessibleDescription")
        Me.directionComboBox.AccessibleName = resources.GetString("directionComboBox.AccessibleName")
        Me.directionComboBox.Anchor = CType(resources.GetObject("directionComboBox.Anchor"), System.Windows.Forms.AnchorStyles)
        Me.directionComboBox.BackgroundImage = CType(resources.GetObject("directionComboBox.BackgroundImage"), System.Drawing.Image)
        Me.directionComboBox.Cursor = System.Windows.Forms.Cursors.Default
        Me.directionComboBox.Dock = CType(resources.GetObject("directionComboBox.Dock"), System.Windows.Forms.DockStyle)
        Me.directionComboBox.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.directionComboBox.Enabled = CType(resources.GetObject("directionComboBox.Enabled"), Boolean)
        Me.directionComboBox.Font = CType(resources.GetObject("directionComboBox.Font"), System.Drawing.Font)
        Me.directionComboBox.ImeMode = CType(resources.GetObject("directionComboBox.ImeMode"), System.Windows.Forms.ImeMode)
        Me.directionComboBox.IntegralHeight = CType(resources.GetObject("directionComboBox.IntegralHeight"), Boolean)
        Me.directionComboBox.ItemHeight = CType(resources.GetObject("directionComboBox.ItemHeight"), Integer)
        Me.directionComboBox.Location = CType(resources.GetObject("directionComboBox.Location"), System.Drawing.Point)
        Me.directionComboBox.MaxDropDownItems = CType(resources.GetObject("directionComboBox.MaxDropDownItems"), Integer)
        Me.directionComboBox.MaxLength = CType(resources.GetObject("directionComboBox.MaxLength"), Integer)
        Me.directionComboBox.Name = "directionComboBox"
        Me.directionComboBox.RightToLeft = CType(resources.GetObject("directionComboBox.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.directionComboBox.Size = CType(resources.GetObject("directionComboBox.Size"), System.Drawing.Size)
        Me.directionComboBox.TabIndex = CType(resources.GetObject("directionComboBox.TabIndex"), Integer)
        Me.directionComboBox.Text = resources.GetString("directionComboBox.Text")
        Me.directionComboBox.Visible = CType(resources.GetObject("directionComboBox.Visible"), Boolean)
        '
        'startColourPage
        '
        Me.startColourPage.AccessibleDescription = resources.GetString("startColourPage.AccessibleDescription")
        Me.startColourPage.AccessibleName = resources.GetString("startColourPage.AccessibleName")
        Me.startColourPage.Anchor = CType(resources.GetObject("startColourPage.Anchor"), System.Windows.Forms.AnchorStyles)
        Me.startColourPage.AutoScroll = CType(resources.GetObject("startColourPage.AutoScroll"), Boolean)
        Me.startColourPage.AutoScrollMargin = CType(resources.GetObject("startColourPage.AutoScrollMargin"), System.Drawing.Size)
        Me.startColourPage.AutoScrollMinSize = CType(resources.GetObject("startColourPage.AutoScrollMinSize"), System.Drawing.Size)
        Me.startColourPage.BackgroundImage = CType(resources.GetObject("startColourPage.BackgroundImage"), System.Drawing.Image)
        Me.startColourPage.Controls.Add(Me.startColourList)
        Me.startColourPage.Dock = CType(resources.GetObject("startColourPage.Dock"), System.Windows.Forms.DockStyle)
        Me.startColourPage.Enabled = CType(resources.GetObject("startColourPage.Enabled"), Boolean)
        Me.startColourPage.Font = CType(resources.GetObject("startColourPage.Font"), System.Drawing.Font)
        Me.startColourPage.ImageIndex = CType(resources.GetObject("startColourPage.ImageIndex"), Integer)
        Me.startColourPage.ImeMode = CType(resources.GetObject("startColourPage.ImeMode"), System.Windows.Forms.ImeMode)
        Me.startColourPage.Location = CType(resources.GetObject("startColourPage.Location"), System.Drawing.Point)
        Me.startColourPage.Name = "startColourPage"
        Me.startColourPage.RightToLeft = CType(resources.GetObject("startColourPage.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.startColourPage.Size = CType(resources.GetObject("startColourPage.Size"), System.Drawing.Size)
        Me.startColourPage.TabIndex = CType(resources.GetObject("startColourPage.TabIndex"), Integer)
        Me.startColourPage.Text = resources.GetString("startColourPage.Text")
        Me.startColourPage.ToolTipText = resources.GetString("startColourPage.ToolTipText")
        Me.startColourPage.Visible = CType(resources.GetObject("startColourPage.Visible"), Boolean)
        '
        'startColourList
        '
        Me.startColourList.AccessibleDescription = resources.GetString("startColourList.AccessibleDescription")
        Me.startColourList.AccessibleName = resources.GetString("startColourList.AccessibleName")
        Me.startColourList.Anchor = CType(resources.GetObject("startColourList.Anchor"), System.Windows.Forms.AnchorStyles)
        Me.startColourList.BackgroundImage = CType(resources.GetObject("startColourList.BackgroundImage"), System.Drawing.Image)
        Me.startColourList.ColumnWidth = CType(resources.GetObject("startColourList.ColumnWidth"), Integer)
        Me.startColourList.Dock = CType(resources.GetObject("startColourList.Dock"), System.Windows.Forms.DockStyle)
        Me.startColourList.DrawMode = System.Windows.Forms.DrawMode.OwnerDrawFixed
        Me.startColourList.Enabled = CType(resources.GetObject("startColourList.Enabled"), Boolean)
        Me.startColourList.Font = CType(resources.GetObject("startColourList.Font"), System.Drawing.Font)
        Me.startColourList.HorizontalExtent = CType(resources.GetObject("startColourList.HorizontalExtent"), Integer)
        Me.startColourList.HorizontalScrollbar = CType(resources.GetObject("startColourList.HorizontalScrollbar"), Boolean)
        Me.startColourList.ImeMode = CType(resources.GetObject("startColourList.ImeMode"), System.Windows.Forms.ImeMode)
        Me.startColourList.IntegralHeight = CType(resources.GetObject("startColourList.IntegralHeight"), Boolean)
        Me.startColourList.ItemHeight = CType(resources.GetObject("startColourList.ItemHeight"), Integer)
        Me.startColourList.Location = CType(resources.GetObject("startColourList.Location"), System.Drawing.Point)
        Me.startColourList.Name = "startColourList"
        Me.startColourList.RightToLeft = CType(resources.GetObject("startColourList.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.startColourList.ScrollAlwaysVisible = CType(resources.GetObject("startColourList.ScrollAlwaysVisible"), Boolean)
        Me.startColourList.Size = CType(resources.GetObject("startColourList.Size"), System.Drawing.Size)
        Me.startColourList.TabIndex = CType(resources.GetObject("startColourList.TabIndex"), Integer)
        Me.startColourList.Visible = CType(resources.GetObject("startColourList.Visible"), Boolean)
        '
        'finishColourPage
        '
        Me.finishColourPage.AccessibleDescription = resources.GetString("finishColourPage.AccessibleDescription")
        Me.finishColourPage.AccessibleName = resources.GetString("finishColourPage.AccessibleName")
        Me.finishColourPage.Anchor = CType(resources.GetObject("finishColourPage.Anchor"), System.Windows.Forms.AnchorStyles)
        Me.finishColourPage.AutoScroll = CType(resources.GetObject("finishColourPage.AutoScroll"), Boolean)
        Me.finishColourPage.AutoScrollMargin = CType(resources.GetObject("finishColourPage.AutoScrollMargin"), System.Drawing.Size)
        Me.finishColourPage.AutoScrollMinSize = CType(resources.GetObject("finishColourPage.AutoScrollMinSize"), System.Drawing.Size)
        Me.finishColourPage.BackgroundImage = CType(resources.GetObject("finishColourPage.BackgroundImage"), System.Drawing.Image)
        Me.finishColourPage.Controls.Add(Me.finishColourList)
        Me.finishColourPage.Dock = CType(resources.GetObject("finishColourPage.Dock"), System.Windows.Forms.DockStyle)
        Me.finishColourPage.Enabled = CType(resources.GetObject("finishColourPage.Enabled"), Boolean)
        Me.finishColourPage.Font = CType(resources.GetObject("finishColourPage.Font"), System.Drawing.Font)
        Me.finishColourPage.ImageIndex = CType(resources.GetObject("finishColourPage.ImageIndex"), Integer)
        Me.finishColourPage.ImeMode = CType(resources.GetObject("finishColourPage.ImeMode"), System.Windows.Forms.ImeMode)
        Me.finishColourPage.Location = CType(resources.GetObject("finishColourPage.Location"), System.Drawing.Point)
        Me.finishColourPage.Name = "finishColourPage"
        Me.finishColourPage.RightToLeft = CType(resources.GetObject("finishColourPage.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.finishColourPage.Size = CType(resources.GetObject("finishColourPage.Size"), System.Drawing.Size)
        Me.finishColourPage.TabIndex = CType(resources.GetObject("finishColourPage.TabIndex"), Integer)
        Me.finishColourPage.Text = resources.GetString("finishColourPage.Text")
        Me.finishColourPage.ToolTipText = resources.GetString("finishColourPage.ToolTipText")
        Me.finishColourPage.Visible = CType(resources.GetObject("finishColourPage.Visible"), Boolean)
        '
        'finishColourList
        '
        Me.finishColourList.AccessibleDescription = resources.GetString("finishColourList.AccessibleDescription")
        Me.finishColourList.AccessibleName = resources.GetString("finishColourList.AccessibleName")
        Me.finishColourList.Anchor = CType(resources.GetObject("finishColourList.Anchor"), System.Windows.Forms.AnchorStyles)
        Me.finishColourList.BackgroundImage = CType(resources.GetObject("finishColourList.BackgroundImage"), System.Drawing.Image)
        Me.finishColourList.ColumnWidth = CType(resources.GetObject("finishColourList.ColumnWidth"), Integer)
        Me.finishColourList.Dock = CType(resources.GetObject("finishColourList.Dock"), System.Windows.Forms.DockStyle)
        Me.finishColourList.DrawMode = System.Windows.Forms.DrawMode.OwnerDrawFixed
        Me.finishColourList.Enabled = CType(resources.GetObject("finishColourList.Enabled"), Boolean)
        Me.finishColourList.Font = CType(resources.GetObject("finishColourList.Font"), System.Drawing.Font)
        Me.finishColourList.HorizontalExtent = CType(resources.GetObject("finishColourList.HorizontalExtent"), Integer)
        Me.finishColourList.HorizontalScrollbar = CType(resources.GetObject("finishColourList.HorizontalScrollbar"), Boolean)
        Me.finishColourList.ImeMode = CType(resources.GetObject("finishColourList.ImeMode"), System.Windows.Forms.ImeMode)
        Me.finishColourList.IntegralHeight = CType(resources.GetObject("finishColourList.IntegralHeight"), Boolean)
        Me.finishColourList.ItemHeight = CType(resources.GetObject("finishColourList.ItemHeight"), Integer)
        Me.finishColourList.Location = CType(resources.GetObject("finishColourList.Location"), System.Drawing.Point)
        Me.finishColourList.Name = "finishColourList"
        Me.finishColourList.RightToLeft = CType(resources.GetObject("finishColourList.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.finishColourList.ScrollAlwaysVisible = CType(resources.GetObject("finishColourList.ScrollAlwaysVisible"), Boolean)
        Me.finishColourList.Size = CType(resources.GetObject("finishColourList.Size"), System.Drawing.Size)
        Me.finishColourList.TabIndex = CType(resources.GetObject("finishColourList.TabIndex"), Integer)
        Me.finishColourList.Visible = CType(resources.GetObject("finishColourList.Visible"), Boolean)
        '
        'BlendFillEditorUI
        '
        Me.AccessibleDescription = resources.GetString("$this.AccessibleDescription")
        Me.AccessibleName = resources.GetString("$this.AccessibleName")
        Me.BackgroundImage = CType(resources.GetObject("$this.BackgroundImage"), System.Drawing.Image)
        Me.ClientSize = CType(resources.GetObject("$this.ClientSize"), System.Drawing.Size)
        Me.Controls.Add(Me.mainTab)
        Me.Enabled = CType(resources.GetObject("$this.Enabled"), Boolean)
        Me.Font = CType(resources.GetObject("$this.Font"), System.Drawing.Font)
        Me.ImeMode = CType(resources.GetObject("$this.ImeMode"), System.Windows.Forms.ImeMode)
        Me.Location = CType(resources.GetObject("$this.Location"), System.Drawing.Point)
        Me.Name = "BlendFillEditorUI"
        Me.RightToLeft = CType(resources.GetObject("$this.RightToLeft"), System.Windows.Forms.RightToLeft)
        Me.Text = resources.GetString("$this.Text")
        Me.mainTab.ResumeLayout(False)
        Me.directionPage.ResumeLayout(False)
        Me.startColourPage.ResumeLayout(False)
        Me.finishColourPage.ResumeLayout(False)
        Me.ResumeLayout(False)

    End Sub

#End Region




    '=----------------------------------------------------------------------=
    ' GetValue
    '=----------------------------------------------------------------------=
    ' Returns what this editor currently has represented as a value.
    '
    ' Returns:
    '       BlendFill
    '
    Friend Function GetValue() As BlendFill

        Dim pdc As PropertyDescriptorCollection
        Dim canli As ColourAndNameListItem
        Dim startColour, finishColour As Color
        Dim direction As BlendStyle

        '
        ' Get the start colour
        '
        canli = CType(Me.startColourList.Items(Me.startColourList.SelectedIndex), ColourAndNameListItem)
        If Not canli Is Nothing Then
            startColour = canli.Colour
        End If

        ' 
        ' Finish Colour
        '
        canli = CType(Me.finishColourList.Items(Me.finishColourList.SelectedIndex), ColourAndNameListItem)
        If Not canli Is Nothing Then
            finishColour = canli.Colour
        End If

        '
        ' blend direction
        '
        direction = Me.directionComboBox.SelectedIndex

        Return New BlendFill(direction, startColour, finishColour)

    End Function ' GetValue



    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '                   Private Methods/Properties/etc
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=


    '=----------------------------------------------------------------------=
    ' populateDirectionListBox
    '=----------------------------------------------------------------------=
    ' Populates and initializes the direction list box with the appropriate
    ' values.
    '
    ' Parameters:
    '       ResourceManager         - [in]  where to obtain localised strs
    '
    Private Sub populateDirectionListBox(ByVal in_resources As System.Resources.ResourceManager)

        Dim s As String

        '
        ' Please note that these keys match the values/order of BlendStyle
        ' exactly !!!!
        '
        Dim keys() As String = New String() { _
            "directionHorizontal", _
            "directionVertical", _
            "directionForwardDiagonal", _
            "directionBackwardDiagonal" _
        }

        '
        ' Loop through the list of values, and put them into the list box.
        '
        For x As Integer = 0 To keys.Length - 1

            s = in_resources.GetString(keys(x))
            System.Diagnostics.Debug.Assert(Not s Is Nothing AndAlso Not s = "")
            Me.directionComboBox.Items.Add(s)

        Next

        '
        ' Finally, select the appropriate item
        '
        Me.directionComboBox.SelectedIndex = Me.m_direction

    End Sub ' populateDirectionListBox


    '=----------------------------------------------------------------------=
    ' populateAndSelectColourList
    '=----------------------------------------------------------------------=
    ' Sets up an owner draw listbox to contain most of the interesting colours
    ' currently available on the system.  It will then select the given colour.
    '
    ' Parameters:
    '       ListBox             - [in]  OwnerDraw listbox to populate.
    '       Color               - [in]  color to select.
    '       ResourceManager     - [in]  from where to get strings
    '
    '
    Private Sub populateAndSelectColourList(ByVal in_listBox As ListBox, _
                                            ByVal in_selectMe As Color, _
                                            ByVal in_resources As System.Resources.ResourceManager)

        Dim canli As New ColourAndNameListItem
        Dim s As String

        '
        ' 1. Add SystemColours to list box.  Please note that we're going to
        '    pass in the colour to select so that we can compare against the
        '    colours in their native format, and not have to go back and 
        '    regenerate the colours from the type strings, etc ...
        '
        addColoursToList(in_listBox, GetType(SystemColors), in_selectMe)

        '
        ' 2. Add Regular colours to the list box.
        '
        addColoursToList(in_listBox, GetType(Color), in_selectMe)

        '
        ' 3. If the user gave us a colour that isn't one of the predefined
        '    system-y colours, then go and add a "Custom" entry for their
        '    colour.
        '
        If in_listBox.SelectedIndex = -1 Then
            s = in_resources.GetString("customColour")
            System.Diagnostics.Debug.Assert(Not s Is Nothing AndAlso Not s = "")

            canli = New ColourAndNameListItem
            canli.Colour = in_selectMe
            canli.Name = s

            in_listBox.Items.Insert(0, canli)
            in_listBox.SelectedIndex = 0
        End If

    End Sub ' populateAndSelectColourList


    '=----------------------------------------------------------------------=
    ' addColoursToList
    '=----------------------------------------------------------------------=
    ' Given an object with a tonne of static colour objects, go and get those
    ' and add them to the list of colours.  We will also do an optimisation, 
    ' and select the appropriate colour if it's in our list.
    '
    ' Parameters:
    '       ListBox             - [in]  where to add the colours.
    '       Type                - [in]  where to get colours.
    '       Color               - [in]  select me if you've got it.
    '
    Private Sub addColoursToList(ByVal in_listBox As ListBox, _
                                 ByVal in_colourSource As Type, _
                                 ByVal in_selectMe As Color)

        Dim pic() As System.Reflection.PropertyInfo
        Dim canli As ColourAndNameListItem
        Dim pi As System.Reflection.PropertyInfo
        Dim i As Integer

        pic = in_colourSource.GetProperties(&HFFFFFFFF)

        '
        ' Loop through all the properties looking for Colour properties.
        '
        For Each pi In pic

            If pi.PropertyType() Is GetType(Color) Then
                canli = New ColourAndNameListItem
                canli.Colour = pi.GetValue(Nothing, Nothing)
                canli.Name = pi.Name

                i = in_listBox.Items.Add(canli)
                If in_selectMe.Equals(canli.Colour) Then
                    in_listBox.SelectedIndex = i
                End If
            End If
        Next

    End Sub ' addColoursToList



    '=----------------------------------------------------------------------=
    ' startColourList_DrawItem
    '=----------------------------------------------------------------------=
    ' We are supposed to draw an item in the list box now.
    '
    Private Sub startColourList_DrawItem(ByVal sender As Object, ByVal e As System.Windows.Forms.DrawItemEventArgs) Handles startColourList.DrawItem
        drawItemForListBox(CType(sender, ListBox), e)
    End Sub



    '=----------------------------------------------------------------------=
    ' finishColourList_DrawItem
    '=----------------------------------------------------------------------=
    ' We are supposed to draw an item in the list box now.
    '
    Private Sub finishColourList_DrawItem(ByVal sender As Object, ByVal e As System.Windows.Forms.DrawItemEventArgs) Handles finishColourList.DrawItem
        drawItemForListBox(CType(sender, ListBox), e)
    End Sub


    '=----------------------------------------------------------------------=
    ' drawItemForListBox
    '=----------------------------------------------------------------------=
    ' Draws an item for one of the two colour list boxes.  We're just going 
    ' to try and look as much like the regular Color UITypeEditor as possible.
    '
    ' Parameters:
    '       ListBox             - [in]  box being drawn.
    '       DrawItemEventArgs   - [in]  details about the painting.
    '
    Private Sub drawItemForListBox(ByVal in_listBox As ListBox, _
                                   ByVal in_args As DrawItemEventArgs)

        Dim canli As ColourAndNameListItem
        Dim b As SolidBrush
        Dim r As Rectangle
        Dim g As Graphics
        Dim p As Pen

        If in_listBox Is Nothing Then
            System.Diagnostics.Debug.Fail("DrawItem event for something that isn't a ListBox!")
            Return
        End If

        '
        ' draw the background for all the arguments.
        '
        in_args.DrawBackground()

        g = in_args.Graphics
        r = in_args.Bounds

        '
        ' Get the ColourAndNameListItem for the details of what we're doing.
        '
        canli = CType(in_listBox.Items(in_args.Index), ColourAndNameListItem)
        If canli Is Nothing Then
            System.Diagnostics.Debug.Fail("A bogus item was inserted into the " & in_listBox.Name & " ListBox.")
            Return
        End If

        '
        ' Now, go and draw the colour in a little framed box.
        '
        Try
            b = New SolidBrush(canli.Colour)
            p = New Pen(Color.Black)

            g.FillRectangle(b, r.Left + 2, r.Top + 2, 22, in_listBox.ItemHeight - 4)
            g.DrawRectangle(p, r.Left + 2, r.Top + 2, 22, in_listBox.ItemHeight - 4)

        Finally

            If Not b Is Nothing Then b.Dispose()
            If Not p Is Nothing Then p.Dispose()

        End Try

        '
        ' Finally, go and draw the text next to the colour !
        '
        Try
            If in_args.State And DrawItemState.Selected Then
                b = New SolidBrush(in_listBox.BackColor)
            Else
                b = New SolidBrush(SystemColors.ControlText)
            End If


            g.DrawString(canli.Name, in_listBox.Font, b, _
                         r.Left + 26, in_args.Bounds.Top + 2)

        Finally

            If Not b Is Nothing Then b.Dispose()

        End Try

    End Sub ' drawItemForListBox


    '=----------------------------------------------------------------------=
    ' blendSamplePanel_Paint
    '=----------------------------------------------------------------------=
    ' Paints a little preview of the blend operation for the user.
    '
    '
    Private Sub blendSamplePanel_Paint(ByVal sender As Object, ByVal e As System.Windows.Forms.PaintEventArgs) Handles blendSamplePanel.Paint

        Dim lgb As LinearGradientBrush
        Dim rects() As Rectangle
        Dim g As Graphics
        Dim p As Pen

        g = e.Graphics

        '
        ' Draw the four sample rects.
        '
        rects = getPanelRects()

        For x As Integer = 0 To rects.Length - 1

            Try
                lgb = New LinearGradientBrush(rects(x), Me.m_startColour, _
                          Me.m_finishColour, getAngle(x))

                g.FillRectangle(lgb, rects(x))

                '
                ' Draw a rect around it.
                '
                If x = Me.m_direction Then
                    p = New Pen(Color.Black, 3)
                Else
                    p = New Pen(Color.Black, 1)
                End If

                g.DrawRectangle(p, rects(x))

            Finally
                If Not lgb Is Nothing Then lgb.Dispose()
                If Not p Is Nothing Then p.Dispose()
            End Try

        Next


    End Sub ' blendSamplePanel_Paint


    '=----------------------------------------------------------------------=
    ' getAngle
    '=----------------------------------------------------------------------=
    ' Returns an angle for a LinearGradientBrush given a direction/style
    '
    ' Parameters:
    '       Integer         - [in]  style/direction
    '
    ' Returns:
    '       Single          - angle to draw.
    '
    Private Function getAngle(ByVal in_direction As Integer) As Single

        Select Case in_direction

            Case BlendStyle.Horizontal
                If Me.m_reverse = False Then
                    Return 0S
                Else
                    Return 180S
                End If

            Case BlendStyle.Vertical
                Return 90S

            Case BlendStyle.ForwardDiagonal
                If Me.m_reverse = False Then
                    Return 45S
                Else
                    Return 135S
                End If

            Case BlendStyle.BackwardDiagonal
                If Me.m_reverse = False Then
                    Return 135S
                Else
                    Return 45S
                End If

            Case Else
                System.Diagnostics.Debug.Fail("Bogus Direction")
                Return 0S
        End Select

    End Function ' getAngle


    '=----------------------------------------------------------------------=
    ' getPanelRects
    '=----------------------------------------------------------------------=
    ' Returns the rectangles in which to draw the samples.
    '
    ' Returns:
    '       Rectangle()
    '
    Private Function getPanelRects() As Rectangle()

        Dim rects() As Rectangle
        Dim w, h As Integer

        w = blendSamplePanel.Width / 2 - 8
        h = blendSamplePanel.Height / 2 - 8
        rects = New Rectangle(3) {}

        rects(0) = New Rectangle(4, 4, w, h)
        rects(1) = New Rectangle(w + 8, 4, w, h)
        rects(2) = New Rectangle(4, h + 8, w, h)
        rects(3) = New Rectangle(w + 8, h + 8, w, h)

        Return rects

    End Function ' getPanelRects


    '=----------------------------------------------------------------------=
    ' directionComboBox_SelectedIndexChanged
    '=----------------------------------------------------------------------=
    ' Update the sample panel with the new selection
    '
    '
    Private Sub directionComboBox_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles directionComboBox.SelectedIndexChanged

        Me.m_direction = Me.directionComboBox.SelectedIndex
        Me.blendSamplePanel.Refresh()

    End Sub ' directionComboBox_SelectedIndexChanged


    '=----------------------------------------------------------------------=
    ' finishColourList_SelectedIndexChanged
    '=----------------------------------------------------------------------=
    ' update the sample box.
    '
    Private Sub finishColourList_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles finishColourList.SelectedIndexChanged

        Dim canli As ColourAndNameListItem

        canli = CType(Me.finishColourList.Items(Me.finishColourList.SelectedIndex), ColourAndNameListItem)
        If Not canli Is Nothing Then
            Me.m_finishColour = canli.Colour
        End If

        Me.blendSamplePanel.Refresh()

    End Sub ' finishColourList_SelectedIndexChanged


    '=----------------------------------------------------------------------=
    ' startColourList_SelectedIndexChanged
    '=----------------------------------------------------------------------=
    ' update the sample box.
    '
    Private Sub startColourList_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles startColourList.SelectedIndexChanged

        Dim canli As ColourAndNameListItem

        canli = CType(Me.startColourList.Items(Me.startColourList.SelectedIndex), ColourAndNameListItem)
        If Not canli Is Nothing Then
            Me.m_startColour = canli.Colour
        End If

        Me.blendSamplePanel.Refresh()

    End Sub ' startColourList_SelectedIndexChanged


    '=----------------------------------------------------------------------=
    ' blendSamplePanel_MouseUp
    '=----------------------------------------------------------------------=
    ' They've clicked on the sample panel.  Update the selection if necessary
    '
    '
    Private Sub blendSamplePanel_MouseUp(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles blendSamplePanel.MouseUp
        Dim rects() As Rectangle

        rects = getPanelRects()

        For x As Integer = 0 To rects.Length - 1
            If rects(x).Contains(e.X, e.Y) Then
                Me.m_direction = x
                Me.blendSamplePanel.Refresh()
                Me.directionComboBox.SelectedIndex = x
            End If
        Next

    End Sub ' blendSamplePanel_MouseUp


    '=----------------------------------------------------------------------=
    ' blendSamplePanel_DoubleClick
    '=----------------------------------------------------------------------=
    ' close down the editor
    '
    Private Sub blendSamplePanel_DoubleClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles blendSamplePanel.DoubleClick

        If Not Me.m_svc Is Nothing Then
            Me.m_svc.CloseDropDown()
        End If

    End Sub ' blendSamplePanel_DoubleClick



    '=----------------------------------------------------------------------=
    ' startColourList_DoubleClick
    '=----------------------------------------------------------------------=
    ' close down the editor
    '
    Private Sub startColourList_DoubleClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles startColourList.DoubleClick

        If Not Me.m_svc Is Nothing Then
            Me.m_svc.CloseDropDown()
        End If

    End Sub ' startColourList_DoubleClick


    '=----------------------------------------------------------------------=
    ' finishColourList_DoubleClick
    '=----------------------------------------------------------------------=
    ' close down the editor
    '
    Private Sub finishColourList_DoubleClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles finishColourList.DoubleClick

        If Not Me.m_svc Is Nothing Then
            Me.m_svc.CloseDropDown()
        End If

    End Sub ' finishColourList_DoubleClick






    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '                           Private Types
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=
    '=----------------------------------------------------------------------=


    '=----------------------------------------------------------------------=
    ' ColourAndNameListItem
    '=----------------------------------------------------------------------=
    ' Wraps a list item in our two colour list boxes.
    '
    '
    Private Class ColourAndNameListItem

        Public Colour As Color
        Public Name As String

        Public Overrides Function ToString() As String
            Return Me.Name
        End Function

    End Class ' ColourAndNameListItem



End Class ' BlendFillEditorUI
