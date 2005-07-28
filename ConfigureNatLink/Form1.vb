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
    Friend WithEvents lblDNSVersion As System.Windows.Forms.Label
    Friend WithEvents cmdEnable As System.Windows.Forms.Button
    Friend WithEvents txtPath As System.Windows.Forms.TextBox
    Friend WithEvents Label1 As System.Windows.Forms.Label
    Friend WithEvents txtVersion As System.Windows.Forms.TextBox
    Friend WithEvents Label2 As System.Windows.Forms.Label
    Friend WithEvents txtIniPath As System.Windows.Forms.TextBox
    Friend WithEvents Label3 As System.Windows.Forms.Label
    Friend WithEvents txtIsEnabled As System.Windows.Forms.TextBox
    <System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(EnableNL))
		Me.lblDNSVersion = New System.Windows.Forms.Label
		Me.cmdEnable = New System.Windows.Forms.Button
		Me.txtVersion = New System.Windows.Forms.TextBox
		Me.txtPath = New System.Windows.Forms.TextBox
		Me.Label1 = New System.Windows.Forms.Label
		Me.Label2 = New System.Windows.Forms.Label
		Me.txtIniPath = New System.Windows.Forms.TextBox
		Me.Label3 = New System.Windows.Forms.Label
		Me.txtIsEnabled = New System.Windows.Forms.TextBox
		Me.SuspendLayout()
		'
		'lblDNSVersion
		'
		Me.lblDNSVersion.Location = New System.Drawing.Point(8, 8)
		Me.lblDNSVersion.Name = "lblDNSVersion"
		Me.lblDNSVersion.Size = New System.Drawing.Size(80, 23)
		Me.lblDNSVersion.TabIndex = 0
		Me.lblDNSVersion.Text = "DNS Version"
		'
		'cmdEnable
		'
		Me.cmdEnable.Location = New System.Drawing.Point(472, 104)
		Me.cmdEnable.Name = "cmdEnable"
		Me.cmdEnable.Size = New System.Drawing.Size(88, 23)
		Me.cmdEnable.TabIndex = 2
		'
		'txtVersion
		'
		Me.txtVersion.Location = New System.Drawing.Point(120, 8)
		Me.txtVersion.Name = "txtVersion"
		Me.txtVersion.ReadOnly = True
		Me.txtVersion.Size = New System.Drawing.Size(440, 20)
		Me.txtVersion.TabIndex = 3
		Me.txtVersion.Text = "txtVersion"
		'
		'txtPath
		'
		Me.txtPath.Location = New System.Drawing.Point(120, 37)
		Me.txtPath.Name = "txtPath"
		Me.txtPath.ReadOnly = True
		Me.txtPath.Size = New System.Drawing.Size(440, 20)
		Me.txtPath.TabIndex = 4
		Me.txtPath.Text = ""
		'
		'Label1
		'
		Me.Label1.Location = New System.Drawing.Point(8, 37)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(80, 23)
		Me.Label1.TabIndex = 5
		Me.Label1.Text = "Install Path"
		'
		'Label2
		'
		Me.Label2.Location = New System.Drawing.Point(8, 66)
		Me.Label2.Name = "Label2"
		Me.Label2.Size = New System.Drawing.Size(80, 23)
		Me.Label2.TabIndex = 7
		Me.Label2.Text = "ini File Path"
		'
		'txtIniPath
		'
		Me.txtIniPath.Location = New System.Drawing.Point(120, 66)
		Me.txtIniPath.Name = "txtIniPath"
		Me.txtIniPath.ReadOnly = True
		Me.txtIniPath.Size = New System.Drawing.Size(440, 20)
		Me.txtIniPath.TabIndex = 6
		Me.txtIniPath.Text = ""
		'
		'Label3
		'
		Me.Label3.Location = New System.Drawing.Point(8, 104)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(96, 23)
		Me.Label3.TabIndex = 9
		Me.Label3.Text = "NatLink Enabled?"
		'
		'txtIsEnabled
		'
		Me.txtIsEnabled.Location = New System.Drawing.Point(120, 104)
		Me.txtIsEnabled.Name = "txtIsEnabled"
		Me.txtIsEnabled.ReadOnly = True
		Me.txtIsEnabled.Size = New System.Drawing.Size(40, 20)
		Me.txtIsEnabled.TabIndex = 8
		Me.txtIsEnabled.Text = ""
		'
		'EnableNL
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(570, 136)
		Me.Controls.Add(Me.Label3)
		Me.Controls.Add(Me.txtIsEnabled)
		Me.Controls.Add(Me.txtIniPath)
		Me.Controls.Add(Me.txtPath)
		Me.Controls.Add(Me.txtVersion)
		Me.Controls.Add(Me.Label2)
		Me.Controls.Add(Me.Label1)
		Me.Controls.Add(Me.cmdEnable)
		Me.Controls.Add(Me.lblDNSVersion)
		Me.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.KeyPreview = True
		Me.MaximizeBox = False
		Me.MinimizeBox = False
		Me.Name = "EnableNL"
		Me.Text = "Enable/Disable NatLink"
		Me.ResumeLayout(False)

	End Sub

#End Region


	Dim nle As NatLinkEnv
    Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load

		Try
			nle = New NatLinkEnv
			txtIniPath.Text = nle.DnsIniFilePath
			txtVersion.Text = nle._dnsName
			txtPath.Text = nle._dnsPath
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

	End Sub
	Private Sub Button1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cmdEnable.Click
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


	Private Sub EnableNL_KeyDown(ByVal sender As Object, ByVal e As System.Windows.Forms.KeyEventArgs) Handles MyBase.KeyDown
		If e.KeyCode = Keys.Escape Then
			Me.Close()
		End If
	End Sub
End Class
