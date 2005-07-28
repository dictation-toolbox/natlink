Imports System.Runtime.InteropServices

Friend Class MessageWindow
	Inherits System.Windows.Forms.Form

	Private InInializeComponent As Boolean = True
#Region " Windows Form Designer generated code "


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
	Private WithEvents XpTaskPanel1 As SteepValley.Windows.Forms.ThemedControls.XPTaskPanel
	Private WithEvents systray As System.Windows.Forms.NotifyIcon
	Private WithEvents CM As System.Windows.Forms.ContextMenu
	Private WithEvents MenuItem1 As System.Windows.Forms.MenuItem
	Private WithEvents TBerror As SteepValley.Windows.Forms.ThemedControls.XPTaskBox
	Private WithEvents TBoutput As SteepValley.Windows.Forms.ThemedControls.XPTaskBox
	Private WithEvents TBCfg As SteepValley.Windows.Forms.ThemedControls.XPTaskBox
	Private WithEvents Toaster As NatLink.MessageWindow.NotificationWindow
	Friend WithEvents txtMsgs As System.Windows.Forms.RichTextBox
	Friend WithEvents txtErrors As System.Windows.Forms.RichTextBox
	Friend WithEvents XpCaption3 As SteepValley.Windows.Forms.XPCaption
	Friend WithEvents XpCaption1 As SteepValley.Windows.Forms.XPCaption
	Private WithEvents chkShowSysTray As System.Windows.Forms.CheckBox
	Friend WithEvents MessageOptionPane As SteepValley.Windows.Forms.XPCaptionPane
	Friend WithEvents rdoMH As System.Windows.Forms.RadioButton
	Friend WithEvents rdoMT As System.Windows.Forms.RadioButton
	Friend WithEvents rdoWO As System.Windows.Forms.RadioButton
	Friend WithEvents ErrorOptionPane As SteepValley.Windows.Forms.XPCaptionPane
	Friend WithEvents rdoET As System.Windows.Forms.RadioButton
	Friend WithEvents rdoEWO As System.Windows.Forms.RadioButton
	Friend WithEvents XpCaption2 As SteepValley.Windows.Forms.XPCaption
	Friend WithEvents NUPdupErrors As System.Windows.Forms.NumericUpDown
	Friend WithEvents NUPToasterTimeout As System.Windows.Forms.NumericUpDown
	Friend WithEvents XpBalloonTip1 As SteepValley.Windows.Forms.XPBalloonTip
	Friend WithEvents ErrorToaster As NatLink.MessageWindow.NotificationWindow
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Me.components = New System.ComponentModel.Container
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(MessageWindow))
		Me.systray = New System.Windows.Forms.NotifyIcon(Me.components)
		Me.CM = New System.Windows.Forms.ContextMenu
		Me.MenuItem1 = New System.Windows.Forms.MenuItem
		Me.XpTaskPanel1 = New SteepValley.Windows.Forms.ThemedControls.XPTaskPanel
		Me.TBerror = New SteepValley.Windows.Forms.ThemedControls.XPTaskBox
		Me.txtErrors = New System.Windows.Forms.RichTextBox
		Me.TBoutput = New SteepValley.Windows.Forms.ThemedControls.XPTaskBox
		Me.txtMsgs = New System.Windows.Forms.RichTextBox
		Me.TBCfg = New SteepValley.Windows.Forms.ThemedControls.XPTaskBox
		Me.XpCaption2 = New SteepValley.Windows.Forms.XPCaption
		Me.NUPdupErrors = New System.Windows.Forms.NumericUpDown
		Me.MessageOptionPane = New SteepValley.Windows.Forms.XPCaptionPane
		Me.rdoWO = New System.Windows.Forms.RadioButton
		Me.rdoMT = New System.Windows.Forms.RadioButton
		Me.rdoMH = New System.Windows.Forms.RadioButton
		Me.XpCaption3 = New SteepValley.Windows.Forms.XPCaption
		Me.NUPToasterTimeout = New System.Windows.Forms.NumericUpDown
		Me.chkShowSysTray = New System.Windows.Forms.CheckBox
		Me.ErrorOptionPane = New SteepValley.Windows.Forms.XPCaptionPane
		Me.rdoEWO = New System.Windows.Forms.RadioButton
		Me.rdoET = New System.Windows.Forms.RadioButton
		Me.Toaster = New NatLink.MessageWindow.NotificationWindow(Me.components)
		Me.XpCaption1 = New SteepValley.Windows.Forms.XPCaption
		Me.XpBalloonTip1 = New SteepValley.Windows.Forms.XPBalloonTip(Me.components)
		Me.ErrorToaster = New NatLink.MessageWindow.NotificationWindow(Me.components)
		Me.XpTaskPanel1.SuspendLayout()
		Me.TBerror.SuspendLayout()
		Me.TBoutput.SuspendLayout()
		Me.TBCfg.SuspendLayout()
		CType(Me.NUPdupErrors, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.MessageOptionPane.SuspendLayout()
		CType(Me.NUPToasterTimeout, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.ErrorOptionPane.SuspendLayout()
		Me.SuspendLayout()
		'
		'systray
		'
		Me.systray.Icon = CType(resources.GetObject("systray.Icon"), System.Drawing.Icon)
		Me.systray.Text = "NatLink Message Window"
		Me.systray.Visible = True
		'
		'CM
		'
		Me.CM.MenuItems.AddRange(New System.Windows.Forms.MenuItem() {Me.MenuItem1})
		'
		'MenuItem1
		'
		Me.MenuItem1.Index = 0
		Me.MenuItem1.Text = "&Open"
		'
		'XpTaskPanel1
		'
		Me.XpTaskPanel1.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
					Or System.Windows.Forms.AnchorStyles.Left) _
					Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.XpTaskPanel1.AutoScroll = True
		Me.XpTaskPanel1.BackColor = System.Drawing.Color.Transparent
		Me.XpTaskPanel1.Controls.Add(Me.TBerror)
		Me.XpTaskPanel1.Controls.Add(Me.TBoutput)
		Me.XpTaskPanel1.Controls.Add(Me.TBCfg)
		Me.XpTaskPanel1.DockPadding.Bottom = 8
		Me.XpTaskPanel1.DockPadding.Left = 8
		Me.XpTaskPanel1.DockPadding.Right = 8
		Me.XpTaskPanel1.Location = New System.Drawing.Point(0, 0)
		Me.XpTaskPanel1.Name = "XpTaskPanel1"
		Me.XpTaskPanel1.Size = New System.Drawing.Size(576, 846)
		Me.XpTaskPanel1.TabIndex = 1
		Me.XpTaskPanel1.ThemeFormat.BottomColor = System.Drawing.Color.FromArgb(CType(40, Byte), CType(91, Byte), CType(197, Byte))
		Me.XpTaskPanel1.ThemeFormat.TopColor = System.Drawing.Color.FromArgb(CType(82, Byte), CType(130, Byte), CType(210, Byte))
		'
		'TBerror
		'
		Me.TBerror.BackColor = System.Drawing.Color.Transparent
		Me.TBerror.Controls.Add(Me.txtErrors)
		Me.TBerror.Dock = System.Windows.Forms.DockStyle.Top
		Me.TBerror.DockPadding.Bottom = 4
		Me.TBerror.DockPadding.Left = 4
		Me.TBerror.DockPadding.Right = 4
		Me.TBerror.DockPadding.Top = 44
		Me.TBerror.HeaderText = "NatLink Errors"
		Me.TBerror.Location = New System.Drawing.Point(8, 488)
		Me.TBerror.Name = "TBerror"
		Me.TBerror.Size = New System.Drawing.Size(560, 240)
		Me.TBerror.TabIndex = 2
		Me.TBerror.ThemeFormat.BodyColor = System.Drawing.Color.FromArgb(CType(197, Byte), CType(210, Byte), CType(240, Byte))
		Me.TBerror.ThemeFormat.BodyFont = New System.Drawing.Font("Tahoma", 8.0!)
		Me.TBerror.ThemeFormat.BodyTextColor = System.Drawing.Color.FromArgb(CType(33, Byte), CType(93, Byte), CType(198, Byte))
		Me.TBerror.ThemeFormat.BorderColor = System.Drawing.Color.White
		Me.TBerror.ThemeFormat.ChevronDown = CType(resources.GetObject("resource.ChevronDown"), System.Drawing.Bitmap)
		Me.TBerror.ThemeFormat.ChevronDownHighlight = CType(resources.GetObject("resource.ChevronDownHighlight"), System.Drawing.Bitmap)
		Me.TBerror.ThemeFormat.ChevronUp = CType(resources.GetObject("resource.ChevronUp"), System.Drawing.Bitmap)
		Me.TBerror.ThemeFormat.ChevronUpHighlight = CType(resources.GetObject("resource.ChevronUpHighlight"), System.Drawing.Bitmap)
		Me.TBerror.ThemeFormat.HeaderFont = New System.Drawing.Font("Tahoma", 8.0!, System.Drawing.FontStyle.Bold)
		Me.TBerror.ThemeFormat.HeaderTextColor = System.Drawing.Color.Black
		Me.TBerror.ThemeFormat.HeaderTextHighlightColor = System.Drawing.Color.FromArgb(CType(66, Byte), CType(142, Byte), CType(255, Byte))
		Me.TBerror.ThemeFormat.LeftHeaderColor = System.Drawing.Color.FromArgb(CType(255, Byte), CType(165, Byte), CType(78, Byte))
		Me.TBerror.ThemeFormat.RightHeaderColor = System.Drawing.Color.FromArgb(CType(255, Byte), CType(225, Byte), CType(155, Byte))
		'
		'txtErrors
		'
		Me.txtErrors.Dock = System.Windows.Forms.DockStyle.Fill
		Me.txtErrors.ForeColor = System.Drawing.Color.FromArgb(CType(192, Byte), CType(64, Byte), CType(0, Byte))
		Me.txtErrors.Location = New System.Drawing.Point(4, 44)
		Me.txtErrors.Name = "txtErrors"
		Me.txtErrors.ReadOnly = True
		Me.txtErrors.Size = New System.Drawing.Size(552, 192)
		Me.txtErrors.TabIndex = 1
		Me.txtErrors.Text = ""
		'
		'TBoutput
		'
		Me.TBoutput.AutoScroll = True
		Me.TBoutput.BackColor = System.Drawing.Color.Transparent
		Me.TBoutput.Controls.Add(Me.txtMsgs)
		Me.TBoutput.Dock = System.Windows.Forms.DockStyle.Top
		Me.TBoutput.DockPadding.Bottom = 4
		Me.TBoutput.DockPadding.Left = 4
		Me.TBoutput.DockPadding.Right = 4
		Me.TBoutput.DockPadding.Top = 44
		Me.TBoutput.HeaderText = "NatLink Output"
		Me.TBoutput.Location = New System.Drawing.Point(8, 268)
		Me.TBoutput.Name = "TBoutput"
		Me.TBoutput.Size = New System.Drawing.Size(560, 220)
		Me.TBoutput.TabIndex = 3
		Me.TBoutput.ThemeFormat.BodyColor = System.Drawing.Color.FromArgb(CType(197, Byte), CType(210, Byte), CType(240, Byte))
		Me.TBoutput.ThemeFormat.BodyFont = New System.Drawing.Font("Tahoma", 8.0!)
		Me.TBoutput.ThemeFormat.BodyTextColor = System.Drawing.Color.FromArgb(CType(33, Byte), CType(93, Byte), CType(198, Byte))
		Me.TBoutput.ThemeFormat.BorderColor = System.Drawing.Color.White
		Me.TBoutput.ThemeFormat.ChevronDown = CType(resources.GetObject("resource.ChevronDown1"), System.Drawing.Bitmap)
		Me.TBoutput.ThemeFormat.ChevronDownHighlight = CType(resources.GetObject("resource.ChevronDownHighlight1"), System.Drawing.Bitmap)
		Me.TBoutput.ThemeFormat.ChevronUp = CType(resources.GetObject("resource.ChevronUp1"), System.Drawing.Bitmap)
		Me.TBoutput.ThemeFormat.ChevronUpHighlight = CType(resources.GetObject("resource.ChevronUpHighlight1"), System.Drawing.Bitmap)
		Me.TBoutput.ThemeFormat.HeaderFont = New System.Drawing.Font("Tahoma", 8.0!, System.Drawing.FontStyle.Bold)
		Me.TBoutput.ThemeFormat.HeaderTextColor = System.Drawing.Color.Black
		Me.TBoutput.ThemeFormat.HeaderTextHighlightColor = System.Drawing.Color.FromArgb(CType(66, Byte), CType(142, Byte), CType(255, Byte))
		Me.TBoutput.ThemeFormat.LeftHeaderColor = System.Drawing.Color.FromArgb(CType(255, Byte), CType(165, Byte), CType(78, Byte))
		Me.TBoutput.ThemeFormat.RightHeaderColor = System.Drawing.Color.FromArgb(CType(255, Byte), CType(225, Byte), CType(155, Byte))
		'
		'txtMsgs
		'
		Me.txtMsgs.Dock = System.Windows.Forms.DockStyle.Fill
		Me.txtMsgs.Location = New System.Drawing.Point(4, 44)
		Me.txtMsgs.Name = "txtMsgs"
		Me.txtMsgs.Size = New System.Drawing.Size(552, 172)
		Me.txtMsgs.TabIndex = 0
		Me.txtMsgs.Text = ""
		'
		'TBCfg
		'
		Me.TBCfg.BackColor = System.Drawing.Color.Transparent
		Me.TBCfg.Controls.Add(Me.XpCaption2)
		Me.TBCfg.Controls.Add(Me.NUPdupErrors)
		Me.TBCfg.Controls.Add(Me.MessageOptionPane)
		Me.TBCfg.Controls.Add(Me.XpCaption3)
		Me.TBCfg.Controls.Add(Me.NUPToasterTimeout)
		Me.TBCfg.Controls.Add(Me.chkShowSysTray)
		Me.TBCfg.Controls.Add(Me.ErrorOptionPane)
		Me.TBCfg.Dock = System.Windows.Forms.DockStyle.Top
		Me.TBCfg.DockPadding.Bottom = 4
		Me.TBCfg.DockPadding.Left = 4
		Me.TBCfg.DockPadding.Right = 4
		Me.TBCfg.DockPadding.Top = 44
		Me.TBCfg.HeaderText = "NatLink Output Window Configuration"
		Me.TBCfg.Location = New System.Drawing.Point(8, 0)
		Me.TBCfg.Name = "TBCfg"
		Me.TBCfg.Size = New System.Drawing.Size(560, 268)
		Me.TBCfg.TabIndex = 4
		Me.TBCfg.ThemeFormat.BodyColor = System.Drawing.Color.FromArgb(CType(197, Byte), CType(210, Byte), CType(240, Byte))
		Me.TBCfg.ThemeFormat.BodyFont = New System.Drawing.Font("Tahoma", 8.0!)
		Me.TBCfg.ThemeFormat.BodyTextColor = System.Drawing.Color.FromArgb(CType(33, Byte), CType(93, Byte), CType(198, Byte))
		Me.TBCfg.ThemeFormat.BorderColor = System.Drawing.Color.White
		Me.TBCfg.ThemeFormat.ChevronDown = CType(resources.GetObject("resource.ChevronDown2"), System.Drawing.Bitmap)
		Me.TBCfg.ThemeFormat.ChevronDownHighlight = CType(resources.GetObject("resource.ChevronDownHighlight2"), System.Drawing.Bitmap)
		Me.TBCfg.ThemeFormat.ChevronUp = CType(resources.GetObject("resource.ChevronUp2"), System.Drawing.Bitmap)
		Me.TBCfg.ThemeFormat.ChevronUpHighlight = CType(resources.GetObject("resource.ChevronUpHighlight2"), System.Drawing.Bitmap)
		Me.TBCfg.ThemeFormat.HeaderFont = New System.Drawing.Font("Tahoma", 8.0!, System.Drawing.FontStyle.Bold)
		Me.TBCfg.ThemeFormat.HeaderTextColor = System.Drawing.Color.Black
		Me.TBCfg.ThemeFormat.HeaderTextHighlightColor = System.Drawing.Color.FromArgb(CType(66, Byte), CType(142, Byte), CType(255, Byte))
		Me.TBCfg.ThemeFormat.LeftHeaderColor = System.Drawing.Color.FromArgb(CType(255, Byte), CType(165, Byte), CType(78, Byte))
		Me.TBCfg.ThemeFormat.RightHeaderColor = System.Drawing.Color.FromArgb(CType(255, Byte), CType(225, Byte), CType(155, Byte))
		'
		'XpCaption2
		'
		Me.XpCaption2.Font = New System.Drawing.Font("Arial", 9.0!, System.Drawing.FontStyle.Bold)
		Me.XpCaption2.Location = New System.Drawing.Point(236, 192)
		Me.XpCaption2.Name = "XpCaption2"
		Me.XpCaption2.Size = New System.Drawing.Size(180, 20)
		Me.XpCaption2.TabIndex = 15
		Me.XpCaption2.Text = "Ignore duplicate error delay"
		'
		'NUPdupErrors
		'
		Me.NUPdupErrors.Increment = New Decimal(New Integer() {500, 0, 0, 0})
		Me.NUPdupErrors.Location = New System.Drawing.Point(424, 192)
		Me.NUPdupErrors.Maximum = New Decimal(New Integer() {90000, 0, 0, 0})
		Me.NUPdupErrors.Minimum = New Decimal(New Integer() {1, 0, 0, -2147483648})
		Me.NUPdupErrors.Name = "NUPdupErrors"
		Me.NUPdupErrors.Size = New System.Drawing.Size(56, 20)
		Me.NUPdupErrors.TabIndex = 14
		Me.NUPdupErrors.Value = New Decimal(New Integer() {5000, 0, 0, 0})
		'
		'MessageOptionPane
		'
		'
		'MessageOptionPane.CaptionControl
		'
		Me.MessageOptionPane.CaptionControl.Active = True
		Me.MessageOptionPane.CaptionControl.ActiveGradientHighColor = System.Drawing.Color.FromArgb(CType(90, Byte), CType(135, Byte), CType(215, Byte))
		Me.MessageOptionPane.CaptionControl.ActiveGradientLowColor = System.Drawing.Color.FromArgb(CType(3, Byte), CType(55, Byte), CType(145, Byte))
		Me.MessageOptionPane.CaptionControl.ActiveTextColor = System.Drawing.Color.White
		Me.MessageOptionPane.CaptionControl.Dock = System.Windows.Forms.DockStyle.Top
		Me.MessageOptionPane.CaptionControl.Font = New System.Drawing.Font("Arial", 9.0!, System.Drawing.FontStyle.Bold)
		Me.MessageOptionPane.CaptionControl.Location = New System.Drawing.Point(1, 1)
		Me.MessageOptionPane.CaptionControl.Name = "caption"
		Me.MessageOptionPane.CaptionControl.Size = New System.Drawing.Size(198, 20)
		Me.MessageOptionPane.CaptionControl.TabIndex = 0
		Me.MessageOptionPane.CaptionControl.Text = "Display options"
		Me.MessageOptionPane.CaptionText = "Display options"
		Me.MessageOptionPane.Controls.Add(Me.rdoWO)
		Me.MessageOptionPane.Controls.Add(Me.rdoMT)
		Me.MessageOptionPane.Controls.Add(Me.rdoMH)
		Me.MessageOptionPane.Controls.Add(Me.MessageOptionPane.CaptionControl)
		Me.MessageOptionPane.DockPadding.All = 1
		Me.MessageOptionPane.Location = New System.Drawing.Point(12, 48)
		Me.MessageOptionPane.Name = "MessageOptionPane"
		Me.MessageOptionPane.Size = New System.Drawing.Size(200, 124)
		Me.MessageOptionPane.TabIndex = 10
		'
		'rdoWO
		'
		Me.rdoWO.Location = New System.Drawing.Point(8, 32)
		Me.rdoWO.Name = "rdoWO"
		Me.rdoWO.Size = New System.Drawing.Size(152, 24)
		Me.rdoWO.TabIndex = 10
		Me.rdoWO.Text = "Always open window"
		'
		'rdoMT
		'
		Me.rdoMT.Location = New System.Drawing.Point(8, 60)
		Me.rdoMT.Name = "rdoMT"
		Me.rdoMT.Size = New System.Drawing.Size(172, 24)
		Me.rdoMT.TabIndex = 11
		Me.rdoMT.Text = "Send messages to ""toaster"""
		'
		'rdoMH
		'
		Me.rdoMH.Location = New System.Drawing.Point(8, 88)
		Me.rdoMH.Name = "rdoMH"
		Me.rdoMH.Size = New System.Drawing.Size(152, 24)
		Me.rdoMH.TabIndex = 12
		Me.rdoMH.Text = "Ignore output"
		'
		'XpCaption3
		'
		Me.XpCaption3.Font = New System.Drawing.Font("Arial", 9.0!, System.Drawing.FontStyle.Bold)
		Me.XpCaption3.Location = New System.Drawing.Point(8, 192)
		Me.XpCaption3.Name = "XpCaption3"
		Me.XpCaption3.Size = New System.Drawing.Size(136, 20)
		Me.XpCaption3.TabIndex = 6
		Me.XpCaption3.Text = "Toaster timeout (ms)"
		'
		'NUPToasterTimeout
		'
		Me.NUPToasterTimeout.Increment = New Decimal(New Integer() {500, 0, 0, 0})
		Me.NUPToasterTimeout.Location = New System.Drawing.Point(156, 192)
		Me.NUPToasterTimeout.Maximum = New Decimal(New Integer() {90000, 0, 0, 0})
		Me.NUPToasterTimeout.Minimum = New Decimal(New Integer() {500, 0, 0, 0})
		Me.NUPToasterTimeout.Name = "NUPToasterTimeout"
		Me.NUPToasterTimeout.Size = New System.Drawing.Size(56, 20)
		Me.NUPToasterTimeout.TabIndex = 3
		Me.NUPToasterTimeout.Value = New Decimal(New Integer() {5000, 0, 0, 0})
		'
		'chkShowSysTray
		'
		Me.chkShowSysTray.Checked = True
		Me.chkShowSysTray.CheckState = System.Windows.Forms.CheckState.Checked
		Me.chkShowSysTray.Location = New System.Drawing.Point(8, 228)
		Me.chkShowSysTray.Name = "chkShowSysTray"
		Me.chkShowSysTray.Size = New System.Drawing.Size(152, 24)
		Me.chkShowSysTray.TabIndex = 2
		Me.chkShowSysTray.Text = "Show SysTray icon"
		'
		'ErrorOptionPane
		'
		'
		'ErrorOptionPane.CaptionControl
		'
		Me.ErrorOptionPane.CaptionControl.Active = True
		Me.ErrorOptionPane.CaptionControl.ActiveGradientHighColor = System.Drawing.Color.FromArgb(CType(90, Byte), CType(135, Byte), CType(215, Byte))
		Me.ErrorOptionPane.CaptionControl.ActiveGradientLowColor = System.Drawing.Color.FromArgb(CType(3, Byte), CType(55, Byte), CType(145, Byte))
		Me.ErrorOptionPane.CaptionControl.ActiveTextColor = System.Drawing.Color.White
		Me.ErrorOptionPane.CaptionControl.Dock = System.Windows.Forms.DockStyle.Top
		Me.ErrorOptionPane.CaptionControl.Font = New System.Drawing.Font("Arial", 9.0!, System.Drawing.FontStyle.Bold)
		Me.ErrorOptionPane.CaptionControl.Location = New System.Drawing.Point(1, 1)
		Me.ErrorOptionPane.CaptionControl.Name = "caption"
		Me.ErrorOptionPane.CaptionControl.Size = New System.Drawing.Size(162, 20)
		Me.ErrorOptionPane.CaptionControl.TabIndex = 0
		Me.ErrorOptionPane.CaptionControl.Text = "Error display options"
		Me.ErrorOptionPane.CaptionText = "Error display options"
		Me.ErrorOptionPane.Controls.Add(Me.rdoEWO)
		Me.ErrorOptionPane.Controls.Add(Me.rdoET)
		Me.ErrorOptionPane.Controls.Add(Me.ErrorOptionPane.CaptionControl)
		Me.ErrorOptionPane.DockPadding.All = 1
		Me.ErrorOptionPane.Location = New System.Drawing.Point(240, 52)
		Me.ErrorOptionPane.Name = "ErrorOptionPane"
		Me.ErrorOptionPane.Size = New System.Drawing.Size(164, 124)
		Me.ErrorOptionPane.TabIndex = 13
		'
		'rdoEWO
		'
		Me.rdoEWO.Location = New System.Drawing.Point(8, 32)
		Me.rdoEWO.Name = "rdoEWO"
		Me.rdoEWO.Size = New System.Drawing.Size(152, 24)
		Me.rdoEWO.TabIndex = 10
		Me.rdoEWO.Text = "Always open window"
		'
		'rdoET
		'
		Me.rdoET.Location = New System.Drawing.Point(8, 60)
		Me.rdoET.Name = "rdoET"
		Me.rdoET.Size = New System.Drawing.Size(152, 24)
		Me.rdoET.TabIndex = 11
		Me.rdoET.Text = "Send errors to ""toaster"""
		'
		'Toaster
		'
		Me.Toaster.Blend = New NatLink.MessageWindow.BlendFill(NatLink.MessageWindow.BlendStyle.Vertical, System.Drawing.SystemColors.InactiveCaption, System.Drawing.SystemColors.Window)
		Me.Toaster.CloseButton = True
		Me.Toaster.CornerImage = CType(resources.GetObject("Toaster.CornerImage"), System.Drawing.Image)
		Me.Toaster.DefaultText = Nothing
		Me.Toaster.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Toaster.ForeColor = System.Drawing.SystemColors.ControlText
		Me.Toaster.RightToLeft = System.Windows.Forms.RightToLeft.No
		Me.Toaster.ShowStyle = NatLink.MessageWindow.NotificationShowStyle.Immediately
		'
		'XpCaption1
		'
		Me.XpCaption1.Font = New System.Drawing.Font("Arial", 9.0!, System.Drawing.FontStyle.Bold)
		Me.XpCaption1.Location = New System.Drawing.Point(204, 52)
		Me.XpCaption1.Name = "XpCaption1"
		Me.XpCaption1.Size = New System.Drawing.Size(150, 20)
		Me.XpCaption1.TabIndex = 4
		'
		'XpBalloonTip1
		'
		Me.XpBalloonTip1.Enabled = True
		'
		'ErrorToaster
		'
		Me.ErrorToaster.Blend = New NatLink.MessageWindow.BlendFill(NatLink.MessageWindow.BlendStyle.Vertical, System.Drawing.Color.Red, System.Drawing.SystemColors.Window)
		Me.ErrorToaster.CloseButton = True
		Me.ErrorToaster.CornerImage = CType(resources.GetObject("ErrorToaster.CornerImage"), System.Drawing.Image)
		Me.ErrorToaster.DefaultText = Nothing
		Me.ErrorToaster.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.ErrorToaster.ForeColor = System.Drawing.SystemColors.ControlText
		Me.ErrorToaster.RightToLeft = System.Windows.Forms.RightToLeft.No
		Me.ErrorToaster.ShowStyle = NatLink.MessageWindow.NotificationShowStyle.Immediately
		'
		'MessageWindow
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(576, 846)
		Me.Controls.Add(Me.XpTaskPanel1)
		Me.FormBorderStyle = System.Windows.Forms.FormBorderStyle.SizableToolWindow
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.KeyPreview = True
		Me.Name = "MessageWindow"
		Me.Text = "NatLink/Vocola Messages"
		Me.XpTaskPanel1.ResumeLayout(False)
		Me.TBerror.ResumeLayout(False)
		Me.TBoutput.ResumeLayout(False)
		Me.TBCfg.ResumeLayout(False)
		CType(Me.NUPdupErrors, System.ComponentModel.ISupportInitialize).EndInit()
		Me.MessageOptionPane.ResumeLayout(False)
		CType(Me.NUPToasterTimeout, System.ComponentModel.ISupportInitialize).EndInit()
		Me.ErrorOptionPane.ResumeLayout(False)
		Me.ResumeLayout(False)

	End Sub

#End Region

#Region "Singleton"

	Private Shared _instance As MessageWindow = Nothing
	Private Shared _lock As Object = New Object
	Public Shared ReadOnly Property Instance() As MessageWindow
		Get
			If _instance Is Nothing Then
				SyncLock _lock
					If _instance Is Nothing Then
						_instance = New MessageWindow
					End If
				End SyncLock
			End If
			Return _instance
		End Get
	End Property
#End Region

	Private Sub New()
		MyBase.New()
		Application.EnableVisualStyles()
		CFG = ConfigOptions.Load()
		InInializeComponent = True
		InitializeComponent()
	End Sub
	Dim CFG As ConfigOptions

#Region "UI Code"

	Protected Overrides Sub OnLoad(ByVal e As System.EventArgs)
		chkShowSysTray.Checked = CFG.ShowSysTray
		Me.Location = CFG.WindowLocation

		If CFG.IsErrorExpanded Then
			Me.TBerror.Expand()
		Else
			Me.TBerror.Collapse()
		End If

		If CFG.IsOutputExpanded Then
			Me.TBoutput.Expand()
		Else
			Me.TBoutput.Collapse()
		End If
		If CFG.IsConfigExpanded Then
			TBCfg.Expand()
		Else
			TBCfg.Collapse()
		End If

		CType(ErrorOptionPane.Controls(CInt(CFG.ErrorDisplayOption)), RadioButton).Checked = True
		CType(MessageOptionPane.Controls(CInt(CFG.DisplayOption)), RadioButton).Checked = True



		NUPdupErrors.DataBindings.Add("Value", CFG, "IgnoreDupsDelay")
		NUPToasterTimeout.DataBindings.Add("Value", CFG, "ToasterTimeout")
		
		InInializeComponent = False
		DoAutoResize()


	End Sub

	Protected Overrides Sub OnClosing(ByVal e As System.ComponentModel.CancelEventArgs)
		MyBase.OnClosing(e)
		e.Cancel = True

		CFG.IsErrorExpanded = Me.TBerror.IsExpanded
		CFG.IsOutputExpanded = Me.TBoutput.IsExpanded
		CFG.IsConfigExpanded = Me.TBCfg.IsExpanded
		ConfigOptions.Save(CFG)
		Me.Hide()
	End Sub


	Private Sub MenuItem1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MenuItem1.Click
		Me.Show()
	End Sub


	Protected Overrides Sub Finalize()
		systray.Icon = Nothing
		systray.Visible = False
		MyBase.Finalize()
	End Sub

	Protected Overrides Sub OnMove(ByVal e As System.EventArgs)
		MyBase.OnMove(e)
		If Not Me.InInializeComponent Then CFG.WindowLocation = Me.Location
	End Sub


	Protected Overrides Sub OnKeyUp(ByVal e As System.Windows.Forms.KeyEventArgs)
		MyBase.OnMove(e)
		If e.KeyCode = Keys.Escape Then
			Me.Close()
		End If
	End Sub

	Private Sub TB_Collapsed(ByVal sender As Object, ByVal e As System.EventArgs) Handles TBCfg.Collapsed, TBerror.Collapsed, TBoutput.Collapsed
		DoAutoResize()
	End Sub

	Private Sub TB_Expanded(ByVal sender As Object, ByVal e As System.EventArgs) Handles TBCfg.Expanded, TBerror.Expanded, TBoutput.Expanded
		DoAutoResize()
		TBCfg.Invalidate()
		TBerror.Invalidate()
		TBoutput.Invalidate()
	End Sub

	Sub DoAutoResize()
		If Me.InInializeComponent Then Exit Sub
		Dim max As Integer
		For Each c As Control In XpTaskPanel1.Controls
			If (c.Top + c.Height) > max Then max = (c.Top + c.Height)
		Next
		Me.Height = max + 40
	End Sub

	Private Sub chkShowSysTray_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles chkShowSysTray.CheckedChanged
		systray.Visible = chkShowSysTray.Checked
		If Not Me.InInializeComponent Then CFG.ShowSysTray = chkShowSysTray.Checked
	End Sub

	Private Sub Toaster_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles Toaster.Click, ErrorToaster.Click
		Me.Show()
		Me.Activate()
	End Sub

	Private Sub rdo_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles rdoWO.CheckedChanged, rdoMH.CheckedChanged, rdoMT.CheckedChanged
		For ii As Integer = 0 To Me.MessageOptionPane.Controls.Count - 1
			If MessageOptionPane.Controls(ii) Is sender Then
				CFG.DisplayOption = CType(ii, ConfigOptions.DisplayOptionsEnum)
			End If
		Next

	End Sub

	Private Sub rdoE_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles rdoEWO.CheckedChanged, rdoET.CheckedChanged
		For ii As Integer = 0 To ErrorOptionPane.Controls.Count - 1
			If ErrorOptionPane.Controls(ii) Is sender Then
				CFG.ErrorDisplayOption = CType(ii, ConfigOptions.DisplayOptionsEnum)
			End If
		Next
	End Sub
	Private Sub NumericUpDown1_ValueChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles NUPToasterTimeout.ValueChanged
		Toaster.DefaultTimeout = CFG.ToasterTimeout
		ErrorToaster.DefaultTimeout = CFG.ToasterTimeout
	End Sub
	Protected Overrides Sub OnActivated(ByVal e As System.EventArgs)
		MyBase.OnActivated(e)
		ScrollToEnd(txtMsgs)
		ScrollToEnd(txtErrors)
	End Sub

	Private Sub systray_MouseDown(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles systray.MouseDown
		Me.Show()
		Me.Activate()
	End Sub

#End Region

#Region "Message Code"
	Dim lstmsgtime As DateTime = Now
	Dim MsgList As New Collections.Specialized.StringCollection
	Dim msgbuff As New System.Text.StringBuilder


	Public Sub ShowMessage(ByVal msg As String)
		If msg = "" Then Exit Sub

		If msg.Trim = "" Then
			msgbuff.Append(msg)
			Exit Sub
		End If


		msgbuff.Insert(0, txtMsgs.Text, 1)
		msgbuff.Append(msg)

		txtMsgs.Text = msgbuff.ToString

		Select Case CFG.DisplayOption

			Case ConfigOptions.DisplayOptionsEnum.HideMessages
			Case ConfigOptions.DisplayOptionsEnum.SendMessageToToaster
				Toaster.Notify(msg)
			Case ConfigOptions.DisplayOptionsEnum.SendMessageToWindow
				Me.Show()
				TBoutput.Expand()
				Me.Activate()
		End Select
		msgbuff.Length = 0
	End Sub


	Public Sub ShowError(ByVal msg As String)
		If msg.Trim = "" Then Exit Sub
		Try

			If MsgList.Contains(msg) AndAlso (CFG.IgnoreDupsDelay = -1 OrElse Now.Subtract(lstmsgtime).TotalMilliseconds < CFG.IgnoreDupsDelay) Then
				Exit Sub
			End If

			txtErrors.Text += msg

			Select Case CFG.ErrorDisplayOption
				Case ConfigOptions.DisplayOptionsEnum.HideMessages, ConfigOptions.DisplayOptionsEnum.SendMessageToToaster
					ErrorToaster.Notify(msg)
				Case ConfigOptions.DisplayOptionsEnum.SendMessageToWindow
					Me.Show()
					TBerror.Expand()
					Me.Activate()
			End Select
		Finally
			If Not MsgList.Contains(msg) Then MsgList.Add(msg)
			lstmsgtime = Now
		End Try
	End Sub

	Sub ScrollToEnd(ByVal tb As TextBoxBase)
		With tb
			.Focus()
			.SelectionStart = tb.TextLength
			.SelectionLength = 0
			.ScrollToCaret()
			.Refresh()
		End With
	End Sub

	Private Sub XpCaption2_MouseHover(ByVal sender As Object, ByVal e As System.EventArgs) Handles XpCaption2.MouseHover
		XpBalloonTip1.Show(XpCaption2, "", "Use -1 for always ignore", SteepValley.Windows.Forms.BalloonTipAPI.ToolTipIcon.Info, 1000)
	End Sub
#End Region

End Class
