Imports System.Runtime.InteropServices
Imports System.Text
Imports System.Text.RegularExpressions
Imports Microsoft.Win32
Imports NLInstaller

Public Class NatLinkEnv
	Inherits System.ComponentModel.Component

#Region "Constants"
	Private Const NSSystemIni As String = "nssystem.ini"
	Private Const NSAppsIni As String = "nsapps.ini"
	Private Const VocIniFile As String = "Vocola\Exec\vocola.ini"
	Public Const NATLINK_CLSID As String = "{dd990001-bb89-11d2-b031-0060088dc929}"
	Public Const defaultNatLinkDLLFile As String = "NatLink\macrosystem\core\natlink.dll"
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
	Private Dim _dnsName As String
	Private _dnsIniFilePath As String = ""

	Private _inInstall As Boolean

	Public Sub New(Optional ByVal installOrCommiting As Boolean = True)
		Trace.WriteLine("NatLinkEnv.New()")
		Trace.Indent()
		_inInstall = installOrCommiting
		Trace.WriteLine("install or committing = " + _inInstall.ToString)
		Trace.Unindent()
	End Sub



    Public Property DnsName() As String
        Get
            Return _dnsName
        End Get
        Set(ByVal value As String)
            _dnsName = value
        End Set
    End Property
    Public ReadOnly Property VocolaVersion() As String
        Get
			Return "2.5"
		End Get
	End Property

	Public ReadOnly Property NatLinkVersion() As String
		Get
			Try
				Dim v As FileVersionInfo = FileVersionInfo.GetVersionInfo(NatLinkDllPath)
				Return String.Format("{0}.{1}.{2}", v.ProductMajorPart, v.ProductMinorPart, v.ProductBuildPart)
			Catch ex As IO.FileNotFoundException
				Return "NA"
			End Try
		End Get
	End Property

	Public Property VocolaCommandSeqEnabled() As Boolean
		Get
			Dim vocini As String = IO.Path.Combine(NatLinkInstallPath, VocIniFile)
			Dim im As New IniManager(vocini)
			Return CBool(im("NatLink Generation Options")("Use Command Sequences"))
		End Get
		Set(ByVal Value As Boolean)
			Dim vocini As String = IO.Path.Combine(NatLinkInstallPath, VocIniFile)
			Dim im As New IniManager(vocini)
			im("NatLink Generation Options").DeleteKey("Use Command Sequences")
			Dim newval As String = CStr(IIf(Value, "1", "0"))
			im("NatLink Generation Options")("Use Command Sequences") = newval
		End Set
	End Property

#Region "User Directories"
	Private NatLinkRegPath As String = "Software\NatLink"
	Public ReadOnly Property DefaultUserDirectory() As String
		Get
			Return IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Personal), "NatLink")
		End Get
	End Property
	Public ReadOnly Property DefaultVocolaUserDirectory() As String
		Get
			Return IO.Path.Combine(DefaultUserDirectory, "Vocola")
		End Get
	End Property


	Public Property NatLinkUserDirectory() As String
		Get
			Dim nlrk As RegistryKey = Registry.CurrentUser.OpenSubKey(NatLinkRegPath)
			Try
				If nlrk Is Nothing Then
					Return ""
				Else
					Return CStr(nlrk.GetValue("UserDirectory"))
				End If
			Finally
				If Not nlrk Is Nothing Then nlrk.Close()
			End Try
		End Get
		Set(ByVal Value As String)
			Dim nlrk As RegistryKey = Registry.CurrentUser.OpenSubKey(NatLinkRegPath, True)
			If nlrk Is Nothing Then
				nlrk = Registry.CurrentUser.CreateSubKey(NatLinkRegPath)
			End If
			nlrk.SetValue("UserDirectory", Value)
			If Not nlrk Is Nothing Then nlrk.Close()
		End Set
	End Property

	Public Property VocolaUserDirectory() As String
		Get
			Dim nlrk As RegistryKey = Registry.CurrentUser.OpenSubKey(NatLinkRegPath)
			Try
				If nlrk Is Nothing Then
					Return ""
				Else
					Return CStr(nlrk.GetValue("VocolaUserDirectory"))
				End If
			Finally
				If Not nlrk Is Nothing Then nlrk.Close()
			End Try
		End Get
		Set(ByVal Value As String)
			Dim nlrk As RegistryKey = Registry.CurrentUser.OpenSubKey(NatLinkRegPath, True)
			If nlrk Is Nothing Then
				nlrk = Registry.CurrentUser.CreateSubKey(NatLinkRegPath)
			End If
			nlrk.SetValue("VocolaUserDirectory", Value)

			If Not nlrk Is Nothing Then nlrk.Close()
		End Set
	End Property

	Public Sub SetDefaultUserDirectory()
		If NatLinkUserDirectory = "" Then
			NatLinkUserDirectory = DefaultUserDirectory
		End If
		If Not IO.Directory.Exists(NatLinkUserDirectory) Then IO.Directory.CreateDirectory(NatLinkUserDirectory)
		If VocolaUserDirectory = "" Then
			VocolaUserDirectory = DefaultVocolaUserDirectory
		End If

		If Not IO.Directory.Exists(VocolaUserDirectory) Then IO.Directory.CreateDirectory(VocolaUserDirectory)
	End Sub
#End Region

#Region "DNS Install Info"

    Public ReadOnly Property SupportsCommandSeq() As Boolean
        Get
            If _dnsVersion = 0 Then Return False
            If _dnsVersion < 7 Then Return True
        End Get
    End Property


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
                    Dim dispName As String = CStr(rkprod.GetValue("DisplayName", "(Null)"))
                    If dispName = "Dragon NaturallySpeaking 8" Then
                        DnsName = CStr(rkprod.GetValue("DisplayName"))
                        _dNSPath = CStr(rkprod.GetValue("InstallLocation"))
                        Trace.WriteLine("DnsName=" + DnsName)
                        Trace.WriteLine("DnsPath=" + _dNSPath)
                    End If
                    rkprod.Close()
                End If
            Next
            rkenum.Close()
        Finally
            Trace.Unindent()
        End Try
    End Sub

    Private _dNSPath As String
    Public ReadOnly Property DNSPath() As String
        Get
            Dim t As String = DnsIniFilePath
            Return _dNSPath
        End Get
    End Property


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

                p = IO.Path.Combine(_dNSPath, NSSystemIni)
                If IO.File.Exists(p) Then
                    _dnsIniFilePath = _dNSPath
                    Return _dnsIniFilePath
                End If


                Throw New ApplicationException("Unable to locate nssystem.ini in either " + vbNewLine + _
                "'" + p1 + "' or '" + _dNSPath + "'. Please ensure you have Dragon NaturallySpeaking installed.")


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

                    Trace.Write("DNS candidiate -- " + s.SectionName)
                    CandidatesSB.Append(s.SectionName).Append(vbNewLine)

                    Dim m As Match = DNSrx.Match(s.SectionName)
                    Trace.Write(" Match status=" + m.Success.ToString)
                    Trace.Write(" Match val=" + m.Groups(1).Value)

                    If m.Success Then
                        ver = Double.Parse(m.Groups(1).Value, System.Globalization.CultureInfo.InvariantCulture)

                        Trace.WriteLine(" Parsed=" + ver.ToString)

                        If ver > _dnsVersion AndAlso ver >= 5.0 Then
                            _dnsVersion = ver
                            Dim instPath As String = s("Install")

                            Trace.Write(" Version = '" + _dnsVersion.ToString + "'")
                            Trace.WriteLine(" InstPath = '" + instPath + "'")

                            If instPath <> "" Then
                                _dNSPath = ExpandPath(instPath)
                                DnsName = s.SectionName
                                If _dNSPath = "" OrElse Not IO.Directory.Exists(_dNSPath) Then
                                    _dNSPath = ""
                                    DnsName = ""
                                    Throw New ApplicationException("Unable to find directory '" + instPath + "'" + vbNewLine + _
                                    "Please ensure Dragon NaturallySpeaking is installed.")
                                End If
                            End If

                        End If
                    End If
                    Trace.WriteLine("")
                End If
            Next

            If DnsName = "" Then
                Dim candString As String = Nothing
                If CandidatesSB.Length > 0 Then
                    candString = "Possible candidates were:" + vbNewLine + CandidatesSB.ToString
                End If
                Throw New ApplicationException("Unable to find a valid Dragon NaturallySpeaking installation in configuration file '" + IniPath + "'" + vbNewLine + vbNewLine + candString)
            End If

        Finally
            Trace.WriteLine("")
            Trace.Unindent()
        End Try

    End Sub

#End Region

#Region "DnsIniFile Management"
    Public Sub EnableNL()
        Try
            Trace.WriteLine("EnableNL()")
            Trace.Indent()
            Dim im As New IniManager(IO.Path.Combine(DnsIniFilePath, NSSystemIni))
            im.Add("Global Clients", ".NatLink", "Python Macro System")

            im = New IniManager(IO.Path.Combine(DnsIniFilePath, NSAppsIni))
            im.Add(".NatLink", "App Support GUID", NATLINK_CLSID)

        Finally
            Trace.Unindent()
        End Try
    End Sub

    Public Sub DisableNL()
        Trace.WriteLine("DisableNL()")
        Trace.Indent()
        Try
            Dim im As New IniManager(IO.Path.Combine(DnsIniFilePath, NSSystemIni))
            im("Global Clients").DeleteKey(".NatLink")
            im = New IniManager(IO.Path.Combine(DnsIniFilePath, NSAppsIni))
            im(".NatLink").Delete()
        Finally
            Trace.Unindent()
        End Try
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
#End Region

#Region "Natlink Install info"
    Public ReadOnly Property NatLinkInstallPath() As String
        Get
            Trace.WriteLine("NatLinkInstallPath()")
            Trace.Indent()
            Dim pth As String
            Try
                pth = IO.Path.GetDirectoryName(NatLinkDllPath)
                pth = IO.Path.Combine(pth, "..\..")
                pth = IO.Path.GetFullPath(pth)
                Trace.WriteLine("= " + pth)
            Finally
                Trace.Unindent()
            End Try
            Return pth
        End Get
    End Property



    Public ReadOnly Property NatLinkDllPath() As String
        Get
            Dim NLDllPath As String
            Trace.WriteLine("Installer -- NatLinkDllPath")
            Trace.Indent()
            Try

                Dim clsID As RegistryKey = Nothing
                Dim ips32 As RegistryKey = Nothing
                Try
                    clsID = Registry.ClassesRoot.OpenSubKey("CLSID\" + NatLinkEnv.NATLINK_CLSID)
                    If Not clsID Is Nothing Then
                        ips32 = clsID.OpenSubKey("InprocServer32")
                        If Not ips32 Is Nothing Then
                            NLDllPath = CStr(ips32.GetValue(""))
                            Trace.WriteLine("Via registry= " + NLDllPath)
                            Return NLDllPath
                        End If
                    End If
                Finally
                    If Not ips32 Is Nothing Then ips32.Close()
                    If Not clsID Is Nothing Then clsID.Close()
                End Try


                Dim p As String = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles)
                p = IO.Path.Combine(p, defaultNatLinkDLLFile)
                If IO.File.Exists(p) Then
                    RegisterDLL(p)
                    Trace.WriteLine("Via default= " + p)
                    Return p
                End If

                Throw New IO.FileNotFoundException("natlink.dll")

            Finally
                Trace.Unindent()
            End Try
        End Get
    End Property
#End Region

#Region "Python"
    Public Sub SetPythonPath()
        Trace.WriteLine("Installer -- SetPythonPath")
        Trace.Indent()

        Dim pp As RegistryKey = Nothing
        Dim nlK As RegistryKey = Nothing
        Try

            Dim instPath As String = NatLinkInstallPath
            Trace.WriteLine("Install path =" + instPath)

            Dim nlPPath As String = _
            IO.Path.Combine(NatLinkInstallPath, "macrosystem") + _
             ";" + _
             IO.Path.Combine(NatLinkInstallPath, "macrosystem\core")
            Trace.WriteLine("nl path = " + nlPPath)


            pp = Registry.LocalMachine.OpenSubKey("Software\Python\PythonCore\2.3\PythonPath", True)
            If pp Is Nothing Then
                Throw New ApplicationException("Unable to locate Python version 2.3")
            End If
            nlK = pp.CreateSubKey("NatLink")
            nlK.SetValue("", nlPPath)
        Finally
            If Not nlK Is Nothing Then nlK.Close()
            If Not pp Is Nothing Then pp.Close()
            Trace.Unindent()
        End Try
    End Sub

    Public Sub ClearPythonPath()
        Trace.WriteLine("Installer -- ClearPythonPath")
        Trace.Indent()
        Dim pp As RegistryKey = Nothing
        Try
            pp = Registry.LocalMachine.OpenSubKey("Software\Python\PythonCore\2.3\PythonPath", True)
            If Not pp Is Nothing Then
                pp.DeleteSubKey("NatLink", False)
            End If
        Finally
            If Not pp Is Nothing Then pp.Close()
            Trace.Unindent()
        End Try
    End Sub
#End Region

    Public Sub RemoveCompiledFiles()
        Trace.WriteLine("UnInstaller -- RemoveCompiledFiles")
        Trace.Indent()
        Try
            Dim p As String = IO.Path.GetDirectoryName(NatLinkDllPath)
            ClearFiles(p, "*.pyc")
            p = IO.Path.GetFullPath(IO.Path.Combine(p, ".."))
            ClearFiles(p, "*.pyc")
            ClearFiles(p, "*_vcl.py")
        Finally
            Trace.Unindent()
        End Try
        Trace.Unindent()
    End Sub

    Private Sub ClearFiles(ByVal path As String, ByVal pattern As String)
        If Not IO.Directory.Exists(path) Then Exit Sub
        For Each f As String In IO.Directory.GetFiles(path, pattern)
            Trace.WriteLine("deleting " + f)
            IO.File.Delete(IO.Path.Combine(path, f))
        Next
    End Sub

    Public Sub RemoveOldNatLinkFiles()
        Trace.WriteLine("Installer -- RemoveOldNatLinkFiles")
        Trace.Indent()
        Try
            Dim p As String = IO.Path.GetDirectoryName(NatLinkDllPath)
            ClearFiles(p, "*.pyc")
            p = IO.Path.GetFullPath(IO.Path.Combine(p, ".."))
            ClearFiles(p, "*.pyc")
            ClearFiles(p, "*_vcl.py")

            Dim oldFiles() As String = {"natlinkmain.py", "natlinkutils.py"}
            For Each f As String In oldFiles
                Dim df As String = IO.Path.Combine(p, f)

                If IO.File.Exists(df) Then
                    Trace.WriteLine("deleting " + f)
                    IO.File.Delete(df)
                End If
            Next

        Finally
            Trace.Unindent()
        End Try

    End Sub

    Friend Sub InstallNatLinkConfigFile()
        Try
            Trace.WriteLine("Installer -- InstallNatLinkConfigFile()")
            Trace.Indent()
            Dim Fsrc As String = IO.Path.Combine(NatLinkInstallPath, "macrosystem\core\natspeak.exe.config")
            Dim NSexePath As String = IO.Path.Combine(DNSPath, "natspeak.exe")
            Dim Fdst As String
            If IO.File.Exists(NSexePath) Then
                Fdst = IO.Path.Combine(DNSPath, "natspeak.exe.config")
            Else
                Fdst = IO.Path.Combine(DNSPath, "Program\natspeak.exe.config")
            End If
            Trace.WriteLine("Dest file=" + Fdst)
            IO.File.Copy(Fsrc, Fdst, True)
        Finally
            Trace.Unindent()
        End Try
    End Sub

    Public Sub RemoveNatLinkConfigFile()
        Try
            Trace.WriteLine("UnInstaller -- RemoveNatLinkConfigFile()")
            Trace.Indent()
            Dim Fdst As String = IO.Path.Combine(DNSPath, "natspeak.exe.config")
            If Not IO.File.Exists(Fdst) Then
                Fdst = IO.Path.Combine(DNSPath, "Program\natspeak.exe.config")
            End If
            If IO.File.Exists(Fdst) Then
                Trace.WriteLine("removing file=" + Fdst)
                IO.File.Delete(Fdst)
            End If
        Finally
            Trace.Unindent()
        End Try
    End Sub

    Public Sub UnRegisterNatLinkDLL()
        Try
            Trace.WriteLine("UnInstaller -- UnRegisterNatLinkDLL()")
            Trace.Indent()

            Dim f As String = NatLinkDllPath
            UnRegisterDLL(f)
        Catch ex As IO.FileNotFoundException
            Trace.WriteLine("NatLink dll does not exist")
            Exit Sub
        Finally
            Trace.Unindent()
        End Try

    End Sub


    Friend Sub UnRegisterDLL(ByVal f As String)
        Try
            Trace.WriteLine("UnInstaller -- UnregisterDLL()")
            Trace.Indent()

            If Not IO.File.Exists(f) Then Exit Sub
            Dim rs As String = Environment.GetFolderPath(Environment.SpecialFolder.System)
            rs = IO.Path.Combine(rs, "regsvr32.exe")

            Dim proc As Process = System.Diagnostics.Process.Start(rs, "/s /u " + """" + f + """")
            proc.WaitForExit()
            Trace.WriteLine("regsvr32 /s /u = " + proc.ExitCode.ToString + " for " + f)
        Finally
            Trace.Unindent()
        End Try
    End Sub

    Private Sub RegisterDLL(ByVal f As String)
        If Not _inInstall Then Exit Sub
        Try
            Trace.WriteLine("RegisterDLL()")
            Trace.Indent()

            If Not IO.File.Exists(f) Then Exit Sub
            Dim rs As String = Environment.GetFolderPath(Environment.SpecialFolder.System)
            rs = IO.Path.Combine(rs, "regsvr32.exe")

            Dim proc As Process = System.Diagnostics.Process.Start(rs, "/s " + """" + f + """")
            proc.WaitForExit()
            Trace.WriteLine("regsvr32 = " + proc.ExitCode.ToString + " for " + f)
        Finally
            Trace.Unindent()
        End Try
    End Sub


End Class
