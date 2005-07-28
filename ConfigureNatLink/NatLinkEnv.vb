Imports System.Runtime.InteropServices
Imports System.Text
Imports System.Text.RegularExpressions
Imports Microsoft.Win32

Public Class NatLinkEnv

#Region "Constants"
	Private Const NSSystemIni As String = "nssystem.ini"
	Private Const NSAppsIni As String = "nsapps.ini"
    Public Const NATLINK_CLSID As String = "{dd990001-bb89-11d2-b031-0060088dc929}"

	Private Const NSExt73Path As String = "ScanSoft\NaturallySpeaking"
	Private Const NSExt8Path As String = "ScanSoft\NaturallySpeaking8"

#End Region

	Private Shared DNSrx As New Regex("^NaturallySpeaking\s+(\d+\.\d+)$", RegexOptions.Compiled)

#Region "System32 declarations"

	Private Const CSIDL_WINDOWS As Integer = &H24
	<DllImport("shell32.dll")> _
	Private Shared Function SHGetFolderPath(ByVal hwndOwner As IntPtr, ByVal nFolder As Int32, ByVal hToken As IntPtr, ByVal dwFlags As Int32, ByVal pszPath As StringBuilder) As Int32
	End Function

	<DllImport("kernel32.dll")> _
	  Private Shared Function GetWindowsDirectory(ByVal path As StringBuilder, ByVal size As Int32) As Int32
	End Function


	<DllImport("kernel32.dll")> _
	Private Shared Function GetLongPathName(ByVal lpszShortPath As String, ByVal lpszLongPath As StringBuilder, ByVal cchBuffer As Int32) As Int32
	End Function

	Private Function ExpandPath(ByVal path As String) As String
		Dim sb As New StringBuilder(600)
		Try
			If GetLongPathName(IO.Path.GetFullPath(path), sb, sb.Capacity) = 0 Then
				If GetLongPathName(path, sb, sb.Capacity) = 0 Then
					Trace.WriteLine("Unable to expand path")
					'				Throw New ApplicationException("Unable to expand path '" + path + "'")
					Return path
				End If
			End If
		Catch ex As EntryPointNotFoundException
			Trace.WriteLine("Unable to expand path, no such entry point")
			Return path
		End Try
		Return sb.ToString
	End Function
#End Region

	Private _pythonVersion As String
	Private _dnsVersion As Double
	Friend _dnsName As String
	Friend _dnsPath As String
	Private _dnsIniFilePath As String = ""



	ReadOnly Property NSInstalledIniFile() As String
		Get
			Dim winPath As New StringBuilder(300)

			Try
				If SHGetFolderPath(Nothing, CSIDL_WINDOWS, Nothing, 0, winPath) <> 0 Then
					Throw New ApplicationException("Unable to locate Windows directory")
				End If
			Catch ex As EntryPointNotFoundException
				If GetWindowsDirectory(winPath, 300) = 0 Then
					Throw New ApplicationException("Unable to locate Windows directory")
				End If
			End Try
			Return IO.Path.Combine(winPath.ToString, "Speech\Dragon\nsinstalled.ini")
		End Get
	End Property


	Public Sub New()
		Trace.WriteLine("NatLinkEnv.New()")
		Trace.Indent()
		Trace.Unindent()
	End Sub


	Public Sub FindNS8InstallVersion()
		Trace.WriteLine("FindNS8InstallVersion")
		Trace.Indent()
		Try

			Dim basekey As String = "SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products\"

			Dim rkenum As RegistryKey = Registry.LocalMachine.OpenSubKey(basekey, False)
			If rkenum Is Nothing Then Exit Sub
			For Each prod As String In rkenum.GetSubKeyNames
				Dim rkprod As RegistryKey = rkenum.OpenSubKey(prod + "\InstallProperties")
				If Not rkprod Is Nothing Then
					Dim dispName As String = rkprod.GetValue("DisplayName")
					If dispName Is Nothing Then dispName = "(Null)"
					Trace.WriteLine(dispName)
					If dispName = "Dragon NaturallySpeaking 8" Then
						_dnsName = rkprod.GetValue("DisplayName")
						_dnsPath = rkprod.GetValue("InstallLocation")
					End If
					rkprod.Close()
				End If
			Next
			rkenum.Close()
		Finally
			Trace.Unindent()
		End Try
	End Sub


	Public ReadOnly Property DnsIniFilePath() As String
		Get
			If _dnsIniFilePath <> "" Then Return _dnsIniFilePath

			Trace.WriteLine("DnsIniFilePath()")
			Trace.Indent()
			Try

				Dim appData As String = _
				Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData)

				If appData = "" Then
					Throw New ApplicationException("Unable to find CommonApplicationData directory")
				End If
				Trace.WriteLine("CommonApplicationData Dir = " + appData)

				' Check ver 8
				Dim p1 As String = IO.Path.Combine(appData, NSExt8Path)
				Dim p As String = IO.Path.Combine(p1, NSSystemIni)
				If IO.File.Exists(p) Then
					FindNS8InstallVersion()
					_dnsIniFilePath = p1
					Return _dnsIniFilePath
				End If

				FindOlderVersions()

				' Check ver 7
				p1 = IO.Path.Combine(appData, NSExt73Path)
				p = IO.Path.Combine(p1, NSSystemIni)
				If IO.File.Exists(p) Then
					_dnsIniFilePath = IO.Path.Combine(appData, NSExt73Path)
					Return _dnsIniFilePath
				End If

				p = IO.Path.Combine(_dnsPath, NSSystemIni)
				If IO.File.Exists(p) Then
					_dnsIniFilePath = _dnsPath
					Return _dnsIniFilePath
				End If


				Throw New ApplicationException("Unable to locate nssystem.ini in either " + vbNewLine + _
				"'" + p1 + "' or '" + _dnsPath + "'. Please ensure you have Dragon NaturallySpeaking installed.")


			Finally
				Trace.Unindent()
			End Try

		End Get
	End Property

	Private Sub FindOlderVersions()
		Trace.WriteLine("NatLinkEnv.FindOlderVersions()")
		Trace.Indent()

		Dim IniPath As String = Me.NSInstalledIniFile
		Try
			Trace.WriteLine("NSInstalled -- " + IniPath)

			Dim im As New IniManager(IniPath)
			Dim ver As Double = 0

			Dim CandidatesSB As New StringBuilder
			For Each s As IniManager.IniSection In im.Sections.Values

				If s.SectionName.Trim <> "" Then

					Trace.WriteLine("DNS candidiate -- " + s.SectionName)
					CandidatesSB.Append(s.SectionName).Append(vbNewLine)

					Dim m As Match = DNSrx.Match(s.SectionName)
					Trace.WriteLine("Match status=" + m.Success.ToString)
					Trace.WriteLine("Match val=" + m.Groups(1).Value)

					If m.Success Then
						ver = Double.Parse(m.Groups(1).Value, System.Globalization.CultureInfo.InvariantCulture)

						Trace.WriteLine("Parsed=" + ver.ToString)

						If ver > _dnsVersion AndAlso ver >= 5.0 Then
							_dnsVersion = ver
							Dim instPath As String = s("Install")

							Trace.WriteLine("Version = '" + _dnsVersion.ToString + "'")
							Trace.WriteLine("InstPath = '" + instPath + "'")

							If instPath <> "" Then
								_dnsPath = ExpandPath(instPath)
								_dnsName = s.SectionName
								If _dnsPath = "" OrElse Not IO.Directory.Exists(_dnsPath) Then
									_dnsPath = ""
									_dnsName = ""
									Throw New ApplicationException("Unable to find directory '" + instPath + "'" + vbNewLine + _
									"Please ensure Dragon NaturallySpeaking is installed.")
								End If
							End If

						End If
					End If

				End If

			Next

			If _dnsName = "" Then
				Dim candString As String
				If CandidatesSB.Length > 0 Then
					candString = "Possible candidates were:" + vbNewLine + CandidatesSB.ToString
				End If
				Throw New ApplicationException("Unable to find a valid Dragon NaturallySpeaking installation in configuration file '" + IniPath + "'" + vbNewLine + vbNewLine + candString)
			End If

		Finally
			Trace.Unindent()
		End Try

	End Sub

	Public Sub EnableNL()
		Dim im As New IniManager(IO.Path.Combine(DnsIniFilePath, NSSystemIni))
		im.Add("Global Clients", ".NatLink", "Python Macro System")

		im = New IniManager(IO.Path.Combine(DnsIniFilePath, NSAppsIni))
		im.Add(".NatLink", "App Support GUID", NATLINK_CLSID)

	End Sub

	Public Sub DisableNL()
		Dim im As New IniManager(IO.Path.Combine(DnsIniFilePath, NSSystemIni))
		im("Global Clients").DeleteKey(".NatLink")
		im = New IniManager(IO.Path.Combine(DnsIniFilePath, NSAppsIni))
		im(".NatLink").Delete()
	End Sub

	Public ReadOnly Property IsEnabled() As Boolean
		Get
			Dim im As New IniManager(IO.Path.Combine(DnsIniFilePath, NSSystemIni))
			If im("Global Clients")(".NatLink") <> "Python Macro System" Then Return False
			im = New IniManager(IO.Path.Combine(DnsIniFilePath, NSAppsIni))
			If im(".NatLink")("App Support GUID") <> NATLINK_CLSID Then Return False

			Return True

		End Get
	End Property

#Region "Python"
	Public Sub SetPythonPath()
		Trace.WriteLine("Installer -- SetPythonPath")
		Trace.Indent()
		Dim clsID As RegistryKey
		Dim pp As RegistryKey
		Dim nlK As RegistryKey
		Try

			clsID = Registry.ClassesRoot.OpenSubKey("CLSID\" + NatLinkEnv.NATLINK_CLSID)
			If clsID Is Nothing Then
				Throw New ApplicationException("Fatal error, unable to locate registry key for NatLink")
			End If

			Dim instPath As String = clsID.OpenSubKey("InprocServer32").GetValue("")
			instPath = IO.Path.GetDirectoryName(instPath)
			Trace.WriteLine("Install path =" + instPath)

			Dim ind As Integer = instPath.LastIndexOf("\"c)
			Dim nlPPath As String = instPath + ";"
			nlPPath += IO.Path.Combine(instPath.Substring(0, ind), "MiscScripts")
			Trace.WriteLine("nl path = " + nlPPath)

			pp = Registry.LocalMachine.OpenSubKey("Software\Python\PythonCore\2.3\PythonPath", True)
			If pp Is Nothing Then
				Throw New ApplicationException("Unable to locate Python version 2.3")
			End If
			nlK = pp.CreateSubKey("NatLink")
			nlK.SetValue("", nlPPath)
		Finally
			If Not clsID Is Nothing Then clsID.Close()
			If Not nlK Is Nothing Then nlK.Close()
			If Not pp Is Nothing Then pp.Close()
			Trace.Unindent()
		End Try
	End Sub

	Public Sub ClearPythonPath()
		Trace.WriteLine("Installer -- ClearPythonPath")
		Trace.Indent()
		Dim pp As RegistryKey
		Try
			pp = Registry.LocalMachine.OpenSubKey("Software\Python\PythonCore\2.3\PythonPath", True)
			If pp Is Nothing Then
				Throw New ApplicationException("Unable to locate Python version 2.3")
			End If
			pp.DeleteSubKey("NatLink")
		Finally
			If Not pp Is Nothing Then pp.Close()
			Trace.Unindent()
		End Try
	End Sub
#End Region


End Class
