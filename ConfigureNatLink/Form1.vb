Imports CP.Windows.Forms
Imports Microsoft.Win32
Imports NLInstaller

Public Class EnableNL
	Inherits System.Windows.Forms.Form

#Region " Windows Form Designer generated code "

	Public Sub New()
		MyBase.New()

		'This call is required by the Windows Form Designer.
		InitializeComponent()

		'Add any initialization after the InitializeComponent() call

	End Sub

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
	Friend WithEvents GroupBox1 As System.Windows.Forms.GroupBox
	Friend WithEvents txtVocVer As System.Windows.Forms.TextBox
	Friend WithEvents txtNLVer As System.Windows.Forms.TextBox
	Friend WithEvents txtIniPath As System.Windows.Forms.TextBox
	Friend WithEvents txtPath As System.Windows.Forms.TextBox
	Friend WithEvents txtVersion As System.Windows.Forms.TextBox
	Friend WithEvents Label5 As System.Windows.Forms.Label
	Friend WithEvents Label4 As System.Windows.Forms.Label
	Friend WithEvents Label2 As System.Windows.Forms.Label
	Friend WithEvents Label1 As System.Windows.Forms.Label
	Friend WithEvents lblDNSVersion As System.Windows.Forms.Label
	Friend WithEvents GroupBox2 As System.Windows.Forms.GroupBox
	Friend WithEvents TxtVocCmdSeqEna As System.Windows.Forms.TextBox
	Friend WithEvents Label6 As System.Windows.Forms.Label
	Friend WithEvents txtIsEnabled As System.Windows.Forms.TextBox
	Friend WithEvents Label3 As System.Windows.Forms.Label
	Friend WithEvents cmdEnable As System.Windows.Forms.Button
	Friend WithEvents cmdVocCmdSeqEnabled As System.Windows.Forms.Button
	Friend WithEvents Label7 As System.Windows.Forms.Label
	Friend WithEvents txtNatLinkPath As System.Windows.Forms.TextBox
	Friend WithEvents Label8 As System.Windows.Forms.Label
	Friend WithEvents Label9 As System.Windows.Forms.Label
	Friend WithEvents btnNLReset As System.Windows.Forms.Button
	Friend WithEvents btnNLBrowse As System.Windows.Forms.Button
	Friend WithEvents btnVocReset As System.Windows.Forms.Button
	Friend WithEvents btnVocBrowse As System.Windows.Forms.Button
	Friend WithEvents txtVocUD As System.Windows.Forms.TextBox
	Friend WithEvents txtNLUD As System.Windows.Forms.TextBox
	Friend WithEvents fbd As CP.Windows.Forms.ShellFolderBrowser
	Friend WithEvents Label10 As System.Windows.Forms.Label
	Friend WithEvents txtDebugOut As System.Windows.Forms.TextBox
	Friend WithEvents cmdDebug As System.Windows.Forms.Button
	Friend WithEvents GroupBox3 As System.Windows.Forms.GroupBox
	Friend WithEvents ToolTip1 As System.Windows.Forms.ToolTip
	Friend WithEvents cmdRegister As System.Windows.Forms.Button
	Friend WithEvents txtRegOutput As System.Windows.Forms.TextBox
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Me.components = New System.ComponentModel.Container
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(EnableNL))
		Me.GroupBox1 = New System.Windows.Forms.GroupBox
		Me.txtNatLinkPath = New System.Windows.Forms.TextBox
		Me.Label7 = New System.Windows.Forms.Label
		Me.txtVocVer = New System.Windows.Forms.TextBox
		Me.txtNLVer = New System.Windows.Forms.TextBox
		Me.txtIniPath = New System.Windows.Forms.TextBox
		Me.txtPath = New System.Windows.Forms.TextBox
		Me.txtVersion = New System.Windows.Forms.TextBox
		Me.Label5 = New System.Windows.Forms.Label
		Me.Label4 = New System.Windows.Forms.Label
		Me.Label2 = New System.Windows.Forms.Label
		Me.Label1 = New System.Windows.Forms.Label
		Me.lblDNSVersion = New System.Windows.Forms.Label
		Me.GroupBox2 = New System.Windows.Forms.GroupBox
		Me.cmdDebug = New System.Windows.Forms.Button
		Me.txtDebugOut = New System.Windows.Forms.TextBox
		Me.Label10 = New System.Windows.Forms.Label
		Me.btnNLReset = New System.Windows.Forms.Button
		Me.btnNLBrowse = New System.Windows.Forms.Button
		Me.Label9 = New System.Windows.Forms.Label
		Me.btnVocReset = New System.Windows.Forms.Button
		Me.btnVocBrowse = New System.Windows.Forms.Button
		Me.Label8 = New System.Windows.Forms.Label
		Me.txtVocUD = New System.Windows.Forms.TextBox
		Me.txtNLUD = New System.Windows.Forms.TextBox
		Me.TxtVocCmdSeqEna = New System.Windows.Forms.TextBox
		Me.Label6 = New System.Windows.Forms.Label
		Me.cmdVocCmdSeqEnabled = New System.Windows.Forms.Button
		Me.txtIsEnabled = New System.Windows.Forms.TextBox
		Me.Label3 = New System.Windows.Forms.Label
		Me.cmdEnable = New System.Windows.Forms.Button
		Me.fbd = New CP.Windows.Forms.ShellFolderBrowser
		Me.GroupBox3 = New System.Windows.Forms.GroupBox
		Me.cmdRegister = New System.Windows.Forms.Button
		Me.ToolTip1 = New System.Windows.Forms.ToolTip(Me.components)
		Me.txtRegOutput = New System.Windows.Forms.TextBox
		Me.GroupBox1.SuspendLayout()
		Me.GroupBox2.SuspendLayout()
		Me.GroupBox3.SuspendLayout()
		Me.SuspendLayout()
		'
		'GroupBox1
		'
		Me.GroupBox1.Controls.Add(Me.txtNatLinkPath)
		Me.GroupBox1.Controls.Add(Me.Label7)
		Me.GroupBox1.Controls.Add(Me.txtVocVer)
		Me.GroupBox1.Controls.Add(Me.txtNLVer)
		Me.GroupBox1.Controls.Add(Me.txtIniPath)
		Me.GroupBox1.Controls.Add(Me.txtPath)
		Me.GroupBox1.Controls.Add(Me.txtVersion)
		Me.GroupBox1.Controls.Add(Me.Label5)
		Me.GroupBox1.Controls.Add(Me.Label4)
		Me.GroupBox1.Controls.Add(Me.Label2)
		Me.GroupBox1.Controls.Add(Me.Label1)
		Me.GroupBox1.Controls.Add(Me.lblDNSVersion)
		Me.GroupBox1.Location = New System.Drawing.Point(8, 8)
		Me.GroupBox1.Name = "GroupBox1"
		Me.GroupBox1.Size = New System.Drawing.Size(584, 152)
		Me.GroupBox1.TabIndex = 17
		Me.GroupBox1.TabStop = False
		Me.GroupBox1.Text = "Info"
		'
		'txtNatLinkPath
		'
		Me.txtNatLinkPath.Location = New System.Drawing.Point(128, 96)
		Me.txtNatLinkPath.Name = "txtNatLinkPath"
		Me.txtNatLinkPath.ReadOnly = True
		Me.txtNatLinkPath.Size = New System.Drawing.Size(440, 20)
		Me.txtNatLinkPath.TabIndex = 24
		Me.txtNatLinkPath.Text = ""
		'
		'Label7
		'
		Me.Label7.Location = New System.Drawing.Point(16, 96)
		Me.Label7.Name = "Label7"
		Me.Label7.Size = New System.Drawing.Size(104, 23)
		Me.Label7.TabIndex = 25
		Me.Label7.Text = "NatLink install path"
		'
		'txtVocVer
		'
		Me.txtVocVer.Location = New System.Drawing.Point(272, 120)
		Me.txtVocVer.Name = "txtVocVer"
		Me.txtVocVer.ReadOnly = True
		Me.txtVocVer.Size = New System.Drawing.Size(40, 20)
		Me.txtVocVer.TabIndex = 23
		Me.txtVocVer.Text = ""
		'
		'txtNLVer
		'
		Me.txtNLVer.Location = New System.Drawing.Point(128, 120)
		Me.txtNLVer.Name = "txtNLVer"
		Me.txtNLVer.ReadOnly = True
		Me.txtNLVer.Size = New System.Drawing.Size(40, 20)
		Me.txtNLVer.TabIndex = 22
		Me.txtNLVer.Text = ""
		'
		'txtIniPath
		'
		Me.txtIniPath.Location = New System.Drawing.Point(128, 72)
		Me.txtIniPath.Name = "txtIniPath"
		Me.txtIniPath.ReadOnly = True
		Me.txtIniPath.Size = New System.Drawing.Size(440, 20)
		Me.txtIniPath.TabIndex = 18
		Me.txtIniPath.Text = ""
		'
		'txtPath
		'
		Me.txtPath.Location = New System.Drawing.Point(128, 48)
		Me.txtPath.Name = "txtPath"
		Me.txtPath.ReadOnly = True
		Me.txtPath.Size = New System.Drawing.Size(440, 20)
		Me.txtPath.TabIndex = 16
		Me.txtPath.Text = ""
		'
		'txtVersion
		'
		Me.txtVersion.Location = New System.Drawing.Point(128, 24)
		Me.txtVersion.Name = "txtVersion"
		Me.txtVersion.ReadOnly = True
		Me.txtVersion.Size = New System.Drawing.Size(440, 20)
		Me.txtVersion.TabIndex = 15
		Me.txtVersion.Text = "txtVersion"
		'
		'Label5
		'
		Me.Label5.Location = New System.Drawing.Point(184, 120)
		Me.Label5.Name = "Label5"
		Me.Label5.Size = New System.Drawing.Size(80, 23)
		Me.Label5.TabIndex = 21
		Me.Label5.Text = "Vocola version"
		'
		'Label4
		'
		Me.Label4.Location = New System.Drawing.Point(16, 120)
		Me.Label4.Name = "Label4"
		Me.Label4.Size = New System.Drawing.Size(96, 23)
		Me.Label4.TabIndex = 20
		Me.Label4.Text = "NatLink version"
		'
		'Label2
		'
		Me.Label2.Location = New System.Drawing.Point(16, 72)
		Me.Label2.Name = "Label2"
		Me.Label2.Size = New System.Drawing.Size(88, 23)
		Me.Label2.TabIndex = 19
		Me.Label2.Text = "DNS .ini file path"
		'
		'Label1
		'
		Me.Label1.Location = New System.Drawing.Point(16, 48)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(88, 23)
		Me.Label1.TabIndex = 17
		Me.Label1.Text = "DNS install path"
		'
		'lblDNSVersion
		'
		Me.lblDNSVersion.Location = New System.Drawing.Point(16, 24)
		Me.lblDNSVersion.Name = "lblDNSVersion"
		Me.lblDNSVersion.Size = New System.Drawing.Size(80, 23)
		Me.lblDNSVersion.TabIndex = 14
		Me.lblDNSVersion.Text = "DNS version"
		'
		'GroupBox2
		'
		Me.GroupBox2.Controls.Add(Me.cmdDebug)
		Me.GroupBox2.Controls.Add(Me.txtDebugOut)
		Me.GroupBox2.Controls.Add(Me.Label10)
		Me.GroupBox2.Controls.Add(Me.btnNLReset)
		Me.GroupBox2.Controls.Add(Me.btnNLBrowse)
		Me.GroupBox2.Controls.Add(Me.Label9)
		Me.GroupBox2.Controls.Add(Me.btnVocReset)
		Me.GroupBox2.Controls.Add(Me.btnVocBrowse)
		Me.GroupBox2.Controls.Add(Me.Label8)
		Me.GroupBox2.Controls.Add(Me.txtVocUD)
		Me.GroupBox2.Controls.Add(Me.txtNLUD)
		Me.GroupBox2.Controls.Add(Me.TxtVocCmdSeqEna)
		Me.GroupBox2.Controls.Add(Me.Label6)
		Me.GroupBox2.Controls.Add(Me.cmdVocCmdSeqEnabled)
		Me.GroupBox2.Controls.Add(Me.txtIsEnabled)
		Me.GroupBox2.Controls.Add(Me.Label3)
		Me.GroupBox2.Controls.Add(Me.cmdEnable)
		Me.GroupBox2.Location = New System.Drawing.Point(8, 176)
		Me.GroupBox2.Name = "GroupBox2"
		Me.GroupBox2.Size = New System.Drawing.Size(584, 256)
		Me.GroupBox2.TabIndex = 0
		Me.GroupBox2.TabStop = False
		Me.GroupBox2.Text = "Configuration"
		'
		'cmdDebug
		'
		Me.cmdDebug.Location = New System.Drawing.Point(352, 40)
		Me.cmdDebug.Name = "cmdDebug"
		Me.cmdDebug.Size = New System.Drawing.Size(88, 23)
		Me.cmdDebug.TabIndex = 36
		'
		'txtDebugOut
		'
		Me.txtDebugOut.Location = New System.Drawing.Point(296, 40)
		Me.txtDebugOut.Name = "txtDebugOut"
		Me.txtDebugOut.ReadOnly = True
		Me.txtDebugOut.Size = New System.Drawing.Size(40, 20)
		Me.txtDebugOut.TabIndex = 35
		Me.txtDebugOut.Text = ""
		'
		'Label10
		'
		Me.Label10.Location = New System.Drawing.Point(296, 24)
		Me.Label10.Name = "Label10"
		Me.Label10.Size = New System.Drawing.Size(216, 16)
		Me.Label10.TabIndex = 34
		Me.Label10.Text = "Send NatLink debug output to Dragon.log"
		'
		'btnNLReset
		'
		Me.btnNLReset.Location = New System.Drawing.Point(480, 144)
		Me.btnNLReset.Name = "btnNLReset"
		Me.btnNLReset.Size = New System.Drawing.Size(75, 16)
		Me.btnNLReset.TabIndex = 33
		Me.btnNLReset.Text = "reset"
		'
		'btnNLBrowse
		'
		Me.btnNLBrowse.Location = New System.Drawing.Point(432, 144)
		Me.btnNLBrowse.Name = "btnNLBrowse"
		Me.btnNLBrowse.Size = New System.Drawing.Size(32, 16)
		Me.btnNLBrowse.TabIndex = 32
		Me.btnNLBrowse.Text = "..."
		Me.btnNLBrowse.TextAlign = System.Drawing.ContentAlignment.BottomCenter
		'
		'Label9
		'
		Me.Label9.Location = New System.Drawing.Point(8, 192)
		Me.Label9.Name = "Label9"
		Me.Label9.Size = New System.Drawing.Size(208, 23)
		Me.Label9.TabIndex = 31
		Me.Label9.Text = "Vocola user directory"
		'
		'btnVocReset
		'
		Me.btnVocReset.Location = New System.Drawing.Point(480, 216)
		Me.btnVocReset.Name = "btnVocReset"
		Me.btnVocReset.Size = New System.Drawing.Size(75, 16)
		Me.btnVocReset.TabIndex = 30
		Me.btnVocReset.Text = "reset"
		'
		'btnVocBrowse
		'
		Me.btnVocBrowse.Location = New System.Drawing.Point(432, 216)
		Me.btnVocBrowse.Name = "btnVocBrowse"
		Me.btnVocBrowse.Size = New System.Drawing.Size(32, 16)
		Me.btnVocBrowse.TabIndex = 28
		Me.btnVocBrowse.Text = "..."
		Me.btnVocBrowse.TextAlign = System.Drawing.ContentAlignment.BottomCenter
		'
		'Label8
		'
		Me.Label8.Location = New System.Drawing.Point(8, 120)
		Me.Label8.Name = "Label8"
		Me.Label8.Size = New System.Drawing.Size(208, 23)
		Me.Label8.TabIndex = 25
		Me.Label8.Text = "NatLink user directory"
		'
		'txtVocUD
		'
		Me.txtVocUD.Location = New System.Drawing.Point(8, 216)
		Me.txtVocUD.Name = "txtVocUD"
		Me.txtVocUD.Size = New System.Drawing.Size(416, 20)
		Me.txtVocUD.TabIndex = 24
		Me.txtVocUD.Text = "txtVocUD"
		'
		'txtNLUD
		'
		Me.txtNLUD.Location = New System.Drawing.Point(8, 144)
		Me.txtNLUD.Name = "txtNLUD"
		Me.txtNLUD.Size = New System.Drawing.Size(416, 20)
		Me.txtNLUD.TabIndex = 23
		Me.txtNLUD.Text = "txtNLUD"
		'
		'TxtVocCmdSeqEna
		'
		Me.TxtVocCmdSeqEna.Location = New System.Drawing.Point(128, 80)
		Me.TxtVocCmdSeqEna.Name = "TxtVocCmdSeqEna"
		Me.TxtVocCmdSeqEna.ReadOnly = True
		Me.TxtVocCmdSeqEna.Size = New System.Drawing.Size(40, 20)
		Me.TxtVocCmdSeqEna.TabIndex = 21
		Me.TxtVocCmdSeqEna.Text = ""
		'
		'Label6
		'
		Me.Label6.Location = New System.Drawing.Point(16, 64)
		Me.Label6.Name = "Label6"
		Me.Label6.Size = New System.Drawing.Size(96, 48)
		Me.Label6.TabIndex = 22
		Me.Label6.Text = "Vocola Command Sequences Enabled?"
		'
		'cmdVocCmdSeqEnabled
		'
		Me.cmdVocCmdSeqEnabled.Location = New System.Drawing.Point(184, 80)
		Me.cmdVocCmdSeqEnabled.Name = "cmdVocCmdSeqEnabled"
		Me.cmdVocCmdSeqEnabled.Size = New System.Drawing.Size(88, 23)
		Me.cmdVocCmdSeqEnabled.TabIndex = 1
		'
		'txtIsEnabled
		'
		Me.txtIsEnabled.Location = New System.Drawing.Point(128, 40)
		Me.txtIsEnabled.Name = "txtIsEnabled"
		Me.txtIsEnabled.ReadOnly = True
		Me.txtIsEnabled.Size = New System.Drawing.Size(40, 20)
		Me.txtIsEnabled.TabIndex = 18
		Me.txtIsEnabled.Text = ""
		'
		'Label3
		'
		Me.Label3.Location = New System.Drawing.Point(16, 24)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(96, 23)
		Me.Label3.TabIndex = 19
		Me.Label3.Text = "NatLink Enabled?"
		'
		'cmdEnable
		'
		Me.cmdEnable.Location = New System.Drawing.Point(184, 40)
		Me.cmdEnable.Name = "cmdEnable"
		Me.cmdEnable.Size = New System.Drawing.Size(88, 23)
		Me.cmdEnable.TabIndex = 0
		'
		'fbd
		'
		Me.fbd.BrowseFlags = CType(((((CP.Windows.Forms.BrowseFlags.ReturnOnlyFSDirs Or CP.Windows.Forms.BrowseFlags.DontGoBelowDomain) _
					Or CP.Windows.Forms.BrowseFlags.ShowStatusText) _
					Or CP.Windows.Forms.BrowseFlags.Validate) _
					Or CP.Windows.Forms.BrowseFlags.NewDialogStyle), CP.Windows.Forms.BrowseFlags)
		Me.fbd.Title = Nothing
		'
		'GroupBox3
		'
		Me.GroupBox3.Controls.Add(Me.txtRegOutput)
		Me.GroupBox3.Controls.Add(Me.cmdRegister)
		Me.GroupBox3.Location = New System.Drawing.Point(16, 456)
		Me.GroupBox3.Name = "GroupBox3"
		Me.GroupBox3.Size = New System.Drawing.Size(560, 100)
		Me.GroupBox3.TabIndex = 18
		Me.GroupBox3.TabStop = False
		Me.GroupBox3.Text = "Repair"
		'
		'cmdRegister
		'
		Me.cmdRegister.Location = New System.Drawing.Point(16, 24)
		Me.cmdRegister.Name = "cmdRegister"
		Me.cmdRegister.Size = New System.Drawing.Size(136, 23)
		Me.cmdRegister.TabIndex = 0
		Me.cmdRegister.Text = "Register NatLink DLL"
		Me.ToolTip1.SetToolTip(Me.cmdRegister, "If you receive ""Unable to load compatiblity module""")
		'
		'txtRegOutput
		'
		Me.txtRegOutput.Location = New System.Drawing.Point(16, 56)
		Me.txtRegOutput.Name = "txtRegOutput"
		Me.txtRegOutput.Size = New System.Drawing.Size(496, 20)
		Me.txtRegOutput.TabIndex = 1
		Me.txtRegOutput.Text = ""
		'
		'EnableNL
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(602, 568)
		Me.Controls.Add(Me.GroupBox3)
		Me.Controls.Add(Me.GroupBox2)
		Me.Controls.Add(Me.GroupBox1)
		Me.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.KeyPreview = True
		Me.MaximizeBox = False
		Me.MinimizeBox = False
		Me.Name = "EnableNL"
		Me.Text = "Configure NatLink & Vocola (beta)"
		Me.GroupBox1.ResumeLayout(False)
		Me.GroupBox2.ResumeLayout(False)
		Me.GroupBox3.ResumeLayout(False)
		Me.ResumeLayout(False)

	End Sub

#End Region


	Friend WithEvents nle As NatLinkEnv
	Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load

		Try
			nle = New NatLinkEnv(True)
			txtIniPath.Text = nle.DnsIniFilePath
            txtVersion.Text = nle.DnsName

			txtPath.Text = nle.DNSPath
			txtNLVer.Text = nle.NatLinkVersion
			txtVocVer.Text = nle.VocolaVersion
			txtNatLinkPath.Text = nle.NatLinkInstallPath

			nle.SetDefaultUserDirectory()

			txtNLUD.Text = nle.NatLinkUserDirectory
			txtVocUD.Text = nle.VocolaUserDirectory


			Me.Text += "        " + _
			Application.ProductVersion.Substring(0, Application.ProductVersion.LastIndexOf("."c))

			SetLabels()

		Catch ex As ApplicationException
			MessageBox.Show(ex.Message, "Installation Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
			Me.Close()
		End Try
	End Sub

	Private Sub SetLabels()
		If nle.IsEnabled Then
			cmdEnable.Text = "Disable"
			txtIsEnabled.Text = "Yes"
		Else
			cmdEnable.Text = "Enable"
			txtIsEnabled.Text = "No"
		End If

		If nle.VocolaCommandSeqEnabled Then
			cmdVocCmdSeqEnabled.Text = "Disable"
			TxtVocCmdSeqEna.Text = "Yes"
		Else
			cmdVocCmdSeqEnabled.Text = "Enable"
			TxtVocCmdSeqEna.Text = "No"
		End If


        If Not nle.SupportsCommandSeq Then
            cmdVocCmdSeqEnabled.Enabled = False
        End If

        If NatLinkDebug Then
            cmdDebug.Text = "Disable"
            txtDebugOut.Text = "Yes"
        Else
            cmdDebug.Text = "Enable"
            txtDebugOut.Text = "No"
        End If


	End Sub

	Private Sub EnableNL_KeyDown(ByVal sender As Object, ByVal e As System.Windows.Forms.KeyEventArgs) Handles MyBase.KeyDown
		If e.KeyCode = Keys.Escape Then
			Me.Close()
		End If
	End Sub

	Private Sub cmdEnable_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdEnable.Click
		Cursor.Current = Cursors.WaitCursor
		If nle.IsEnabled Then
			nle.DisableNL()
			nle.ClearPythonPath()
		Else
			nle.EnableNL()
			nle.SetPythonPath()
		End If
		SetLabels()
		Cursor.Current = Cursors.Arrow
	End Sub

	Private Sub cmdVocCmdSeqEnabled_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdVocCmdSeqEnabled.Click

		Cursor.Current = Cursors.WaitCursor
		If nle.VocolaCommandSeqEnabled Then
			nle.VocolaCommandSeqEnabled = False
		Else
			nle.VocolaCommandSeqEnabled = True
		End If
		SetLabels()
		Cursor.Current = Cursors.Arrow

	End Sub

	public readonly property  NatLinkDebug as integer 

		Get
            Dim rk As Microsoft.Win32.RegistryKey = Nothing
			Try
				rk = Registry.CurrentUser.OpenSubKey("Software\NatLink")
				Return rk.GetValue("NatLinkDebug", 0)
			Finally
				If Not rk Is Nothing Then rk.Close()
			End Try
		End Get
	End Property
	

	Private Sub cmdDebug_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdDebug.Click
		Cursor.Current = Cursors.WaitCursor

		Dim rk As Microsoft.Win32.RegistryKey
		rk = Registry.CurrentUser.OpenSubKey("Software\NatLink", True)

		If rk.GetValue("NatLinkDebug", 0) = 0 Then
			rk.SetValue("NatLinkDebug", 1)
		Else
			rk.SetValue("NatLinkDebug", 0)
		End If
		rk.Close()
		SetLabels()
		Cursor.Current = Cursors.Arrow
	End Sub


	Private Sub btnNLBrowse_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnNLBrowse.Click
		If fbd.ShowDialog(Me) AndAlso fbd.FolderPath <> "" Then
			txtNLUD.Text = fbd.FolderPath
			nle.NatLinkUserDirectory = fbd.FolderPath
		End If
	End Sub

	Private Sub btnVocBrowse_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnVocBrowse.Click
		If fbd.ShowDialog(Me) AndAlso fbd.FolderPath <> "" Then
			txtVocUD.Text = fbd.FolderPath
			nle.VocolaUserDirectory = fbd.FolderPath
		End If
	End Sub

	Private Sub btnNLReset_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnNLReset.Click
		txtNLUD.Text = nle.DefaultUserDirectory
		nle.NatLinkUserDirectory = nle.DefaultUserDirectory
		IO.Directory.CreateDirectory(nle.DefaultUserDirectory)
	End Sub

	Private Sub btnVocReset_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnVocReset.Click
		txtVocUD.Text = nle.DefaultVocolaUserDirectory
		nle.VocolaUserDirectory = nle.DefaultVocolaUserDirectory
		IO.Directory.CreateDirectory(nle.DefaultVocolaUserDirectory)
	End Sub

	Private Sub cmdReg_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdRegister.Click
		Dim dr As New DllRegServer(nle.NatLinkDllPath)
		Try
			dr.Register()
			txtRegOutput.Text = "OK"
		Catch ex As Exception
			If ex.InnerException Is Nothing Then
				txtRegOutput.Text = ex.Message
			Else
				txtRegOutput.Text = ex.InnerException.Message
			End If
		End Try
	End Sub
End Class
