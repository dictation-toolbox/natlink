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

	Public Overrides Sub Commit(ByVal savedState As System.Collections.IDictionary)
		MyBase.Commit(savedState)

		InitLogListener()
        Trace.Write("Installer -- Commit ")
        Dim dt As DateTime = AssemblyBuildDate(Me.GetType.Assembly)
        Trace.WriteLine(Me.GetType.Assembly.FullName + dt.ToShortDateString + " " + dt.ToShortTimeString)

		Trace.Indent()
		Try
			Dim nle As New NatLinkEnv
			Trace.Flush()
            'nle.UnRegisterNatLinkDLL()
			nle.RemoveOldNatLinkFiles()
			nle.EnableNL()
			Trace.Flush()
			nle.SetPythonPath()
			Trace.Flush()
			Trace.WriteLine("Natlink Commited")
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



	Public Overrides Sub Install(ByVal stateSaver As System.Collections.IDictionary)
		MyBase.Install(stateSaver)
		InitLogListener()
		Trace.Write("Installer -- install ")
		Trace.WriteLine(System.Reflection.Assembly.GetExecutingAssembly.FullName)
		Trace.Write(Environment.OSVersion.ToString)

		Trace.Indent()
		Try
			Trace.WriteLine(" " + Now.ToLongDateString + " " + Now.ToShortTimeString)
			Dim nle As New NatLinkEnv
			nle.SetDefaultUserDirectory()
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
		If Not ex.InnerException Is Nothing Then Trace.WriteLine(ex.InnerException.ToString)
		Trace.Unindent()
		Trace.Flush()
	End Sub
	Public Overrides Sub Rollback(ByVal stateSaver As System.Collections.IDictionary)
		MyBase.Rollback(stateSaver)

		Trace.Write("Installer -- rollback ")
		Trace.WriteLine(System.Reflection.Assembly.GetExecutingAssembly.FullName)
		Trace.Indent()
		Try
			Dim nle As New NatLinkEnv(False)
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
		Trace.WriteLine(System.Reflection.Assembly.GetExecutingAssembly.FullName)
		Trace.Indent()
		Trace.WriteLine(Now.ToLongDateString + " " + Now.ToShortTimeString)
		Dim nle As New NatLinkEnv(False)

		Try

			Try
				nle.DisableNL()
			Catch ex As Exception
				LogException(ex)
				Trace.WriteLine("Natlink failed to DisableNL.")
			End Try

			Try
				nle.ClearPythonPath()
			Catch ex As Exception
				LogException(ex)
				Trace.WriteLine("Natlink failed to Clear Python Path.")
			End Try

			Try
				nle.RemoveCompiledFiles()
			Catch ex As Exception
				LogException(ex)
				Trace.WriteLine("Natlink failed to Remove Compiled Files.")
			End Try

			Try
				nle.RemoveNatLinkConfigFile()
			Catch ex As Exception
				LogException(ex)
				Trace.WriteLine("Natlink failed to Remove NatLink config file.")
			End Try


			Try
				nle.UnRegisterNatLinkDLL()
			Catch ex As Exception
				LogException(ex)
				Trace.WriteLine("Natlink failed to UnRegisterNatLinkDLL.")
			End Try


		Finally
			Trace.WriteLine("Natlink Uninstalled")
			Trace.Unindent()
			CloseLogListener()
		End Try
	End Sub

    Private Function AssemblyBuildDate(ByVal objAssembly As System.Reflection.Assembly, _
           Optional ByVal blnForceFileDate As Boolean = False) As DateTime
        Dim objVersion As System.Version = objAssembly.GetName.Version
        Dim dtBuild As DateTime

        If blnForceFileDate Then
            dtBuild = AssemblyFileTime(objAssembly)
        Else
            dtBuild = CType("01/01/2000", DateTime). _
             AddDays(objVersion.Build). _
             AddSeconds(objVersion.Revision * 2)
            If TimeZone.IsDaylightSavingTime(DateTime.Now, TimeZone.CurrentTimeZone.GetDaylightChanges(DateTime.Now.Year)) Then
                dtBuild = dtBuild.AddHours(1)
            End If
            If dtBuild > DateTime.Now Or objVersion.Build < 730 Or objVersion.Revision = 0 Then
                dtBuild = AssemblyFileTime(objAssembly)
            End If
        End If

        Return dtBuild
    End Function
    Private Function AssemblyFileTime(ByVal objAssembly As System.Reflection.Assembly) As DateTime
        Try
            Return System.IO.File.GetLastWriteTime(objAssembly.Location)
        Catch ex As Exception
            Return DateTime.MaxValue
        End Try
    End Function


End Class
