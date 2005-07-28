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
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(EnableNL))
		Me.GroupBox1 = New System.Windows.Forms.GroupBox
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
		Me.TxtVocCmdSeqEna = New System.Windows.Forms.TextBox
		Me.Label6 = New System.Windows.Forms.Label
		Me.cmdVocCmdSeqEnabled = New System.Windows.Forms.Button
		Me.txtIsEnabled = New System.Windows.Forms.TextBox
		Me.Label3 = New System.Windows.Forms.Label
		Me.cmdEnable = New System.Windows.Forms.Button
		Me.txtNatLinkPath = New System.Windows.Forms.TextBox
		Me.Label7 = New System.Windows.Forms.Label
		Me.GroupBox1.SuspendLayout()
		Me.GroupBox2.SuspendLayout()
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
		Me.GroupBox2.Controls.Add(Me.TxtVocCmdSeqEna)
		Me.GroupBox2.Controls.Add(Me.Label6)
		Me.GroupBox2.Controls.Add(Me.cmdVocCmdSeqEnabled)
		Me.GroupBox2.Controls.Add(Me.txtIsEnabled)
		Me.GroupBox2.Controls.Add(Me.Label3)
		Me.GroupBox2.Controls.Add(Me.cmdEnable)
		Me.GroupBox2.Location = New System.Drawing.Point(8, 176)
		Me.GroupBox2.Name = "GroupBox2"
		Me.GroupBox2.Size = New System.Drawing.Size(584, 144)
		Me.GroupBox2.TabIndex = 0
		Me.GroupBox2.TabStop = False
		Me.GroupBox2.Text = "Configuration"
		'
		'TxtVocCmdSeqEna
		'
		Me.TxtVocCmdSeqEna.Location = New System.Drawing.Point(128, 64)
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
		Me.cmdVocCmdSeqEnabled.Location = New System.Drawing.Point(480, 64)
		Me.cmdVocCmdSeqEnabled.Name = "cmdVocCmdSeqEnabled"
		Me.cmdVocCmdSeqEnabled.Size = New System.Drawing.Size(88, 23)
		Me.cmdVocCmdSeqEnabled.TabIndex = 1
		'
		'txtIsEnabled
		'
		Me.txtIsEnabled.Location = New System.Drawing.Point(128, 32)
		Me.txtIsEnabled.Name = "txtIsEnabled"
		Me.txtIsEnabled.ReadOnly = True
		Me.txtIsEnabled.Size = New System.Drawing.Size(40, 20)
		Me.txtIsEnabled.TabIndex = 18
		Me.txtIsEnabled.Text = ""
		'
		'Label3
		'
		Me.Label3.Location = New System.Drawing.Point(16, 32)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(96, 23)
		Me.Label3.TabIndex = 19
		Me.Label3.Text = "NatLink Enabled?"
		'
		'cmdEnable
		'
		Me.cmdEnable.Location = New System.Drawing.Point(480, 32)
		Me.cmdEnable.Name = "cmdEnable"
		Me.cmdEnable.Size = New System.Drawing.Size(88, 23)
		Me.cmdEnable.TabIndex = 0
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
		'EnableNL
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(594, 328)
		Me.Controls.Add(Me.GroupBox2)
		Me.Controls.Add(Me.GroupBox1)
		Me.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.KeyPreview = True
		Me.MaximizeBox = False
		Me.MinimizeBox = False
		Me.Name = "EnableNL"
		Me.Text = "Configure NatLink & Vocola"
		Me.GroupBox1.ResumeLayout(False)
		Me.GroupBox2.ResumeLayout(False)
		Me.ResumeLayout(False)

	End Sub

#End Region


	Friend WithEvents nle As NatLinkEnv
    Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load

		Try
			nle = New NatLinkEnv
			txtIniPath.Text = nle.DnsIniFilePath
			txtVersion.Text = nle._dnsName
			txtPath.Text = nle._dnsPath
			txtNLVer.Text = nle.NatLinkVersion
			txtVocVer.Text = nle.VocolaVersion
			txtNatLinkPath.Text = nle.NatLinkInstallPath

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
End Class
