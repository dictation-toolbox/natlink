Imports System.ComponentModel
Imports System.Configuration.Install
<RunInstaller(True)> Public Class NatLinkInstaller
	Inherits System.Configuration.Install.Installer


#Region " Component Designer generated code "

	Public Sub New()
		MyBase.New()

		'This call is required by the Component Designer.
		InitializeComponent()

		'Add any initialization after the InitializeComponent() call
	End Sub

	'Installer overrides dispose to clean up the component list.
	Protected Overloads Overrides Sub Dispose(ByVal disposing As Boolean)
		If disposing Then
			If Not (components Is Nothing) Then
				components.Dispose()
			End If
		End If
		MyBase.Dispose(disposing)
	End Sub

	'Required by the Component Designer
	Private components As System.ComponentModel.IContainer

	'NOTE: The following procedure is required by the Component Designer
	'It can be modified using the Component Designer.  
	'Do not modify it using the code editor.
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		components = New System.ComponentModel.Container
	End Sub

#End Region

	Dim logListener As TextWriterTraceListener
	Dim logPath As String

	Private Sub InitLogListener()
		If Not Trace.Listeners.Contains(logListener) Then
			Dim pth As String = Environment.GetFolderPath(Environment.SpecialFolder.Personal)
			logPath = IO.Path.Combine(pth, "NatLinkInstallLog.txt")
			logListener = New TextWriterTraceListener(logPath)
			Trace.Listeners.Add(logListener)
		End If
	End Sub

	Private Sub CloseLogListener()
		Trace.Flush()
		logListener.Writer.Close()
		Trace.Listeners.Remove(logListener)
	End Sub

	Public Overrides Sub Install(ByVal stateSaver As System.Collections.IDictionary)
		MyBase.Install(stateSaver)

		InitLogListener()


		Trace.WriteLine("Installer -- install")

		Trace.WriteLine(System.Reflection.Assembly.GetExecutingAssembly.FullName)
		Trace.WriteLine(Environment.OSVersion.ToString)

		Trace.Indent()
		Try
			Trace.WriteLine(Now.ToLongDateString + " " + Now.ToShortTimeString)
			Dim nle As New NatLinkEnv
			Trace.Flush()
			nle.EnableNL()
			Trace.Flush()
			nle.SetPythonPath()
			Trace.Flush()
			Trace.WriteLine("Natlink Installed")
			CloseLogListener()
		Catch ex As Exception
			LogException(ex)
			Trace.WriteLine("Natlink installation failed.")
			Throw New ApplicationException("NatLink failed to install." + vbNewLine + "Please check 'My Documents\NatLinkInstallLog.txt' for reasons." + vbNewLine, ex)
		Finally
			Trace.Unindent()
			Trace.Flush()
		End Try
	End Sub

	Private Sub LogException(ByVal ex As Exception)
		Trace.Indent()
		Trace.WriteLine(ex.Message)
		Trace.WriteLine("")
		Trace.WriteLine(ex.StackTrace)
		Trace.Unindent()
		Trace.Flush()
	End Sub
	Public Overrides Sub Rollback(ByVal stateSaver As System.Collections.IDictionary)
		MyBase.Rollback(stateSaver)

		'		InitLogListener()
		Trace.WriteLine("Installer -- rollback")
		Trace.Indent()
		Try
			Dim nle As New NatLinkEnv
			nle.DisableNL()
			nle.ClearPythonPath()
			Trace.WriteLine("Natlink install successfully rolled back")
		Catch ex As Exception
			LogException(ex)
			Trace.WriteLine("Natlink rollback failed.")
		Finally
			Trace.Unindent()
			CloseLogListener()
		End Try
	End Sub



	Public Overrides Sub Uninstall(ByVal savedState As System.Collections.IDictionary)
		MyBase.Uninstall(savedState)

		InitLogListener()
		Trace.WriteLine("Installer -- Uninstall")
		Trace.Indent()
		Trace.WriteLine(Now.ToLongDateString + " " + Now.ToShortTimeString)

		Try
			Dim nle As New NatLinkEnv
			nle.DisableNL()
			nle.ClearPythonPath()
			Trace.WriteLine("Natlink Uninstalled")
		Catch ex As ApplicationException
			LogException(ex)
			Trace.WriteLine("Natlink failed to uninstall.")
			Throw
		Finally
			Trace.Unindent()
			CloseLogListener()
		End Try
	End Sub

End Class
