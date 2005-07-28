Imports System.Text
Imports System.Collections.Specialized
Imports System.Runtime.InteropServices
Public Class IniManager
    <DllImport("kernel32.dll")> _
    Private Shared Function GetPrivateProfileSection(ByVal lpAppName As String, ByVal buff As IntPtr, ByVal nSize As Int32, ByVal iniFile As String) As Int32
    End Function
	<DllImport("kernel32.dll", EntryPoint:="GetPrivateProfileSectionNamesA")> _
 Private Shared Function GetPrivateProfileSectionNames( _
 ByVal lpszReturnBuffer As IntPtr, ByVal nSize As System.Int32, ByVal lpFileName As String) As System.Int32
	End Function

	<DllImport("kernel32.dll")> _
	Private Shared Function WritePrivateProfileString(ByVal sectionName As String, ByVal keyName As String, ByVal value As String, ByVal iniFile As String) As Int32
	End Function

	Public Const MaxBuff = (32 * 1024) - 1	'32,767 
	Private _iniFile As String

	Public Sub New(ByVal iniFile As String)
		_iniFile = iniFile
		If Not IO.File.Exists(iniFile) Then
			Throw New ApplicationException("File '" + iniFile + "' does not exist")
		End If
	End Sub

	Private _sections As Collections.Hashtable
	Public ReadOnly Property Sections() As Hashtable
		Get
			If _sections Is Nothing Then
				GetSectionNames()
			End If
			Return _sections
		End Get
	End Property

	Private Sub GetSectionNames()
		Dim profiles As New Collections.Specialized.StringCollection
		Dim ptr As IntPtr = Marshal.StringToHGlobalAnsi(New String(vbNullChar, MaxBuff))
		Dim len As Int32 = GetPrivateProfileSectionNames(ptr, MaxBuff, _iniFile)
		Dim buff As String = Marshal.PtrToStringAnsi(ptr, len)
		Marshal.FreeHGlobal(ptr)
		Dim sb As New StringBuilder
		For ii As Integer = 0 To len - 1
			Dim c As Char = buff.Chars(ii)
			If c = vbNullChar Then
				profiles.Add(sb.ToString)
				sb.Length = 0
			Else
				sb.Append(c)
			End If
		Next

		If profiles.Count = 0 Then
			Throw New ApplicationException("'" + _iniFile + "' has no sections")
		End If
		_sections = New Hashtable(profiles.Count)
		For Each secName As String In profiles
			_sections.Add(secName, New IniSection(_iniFile, secName))
		Next
	End Sub

	Public Sub Add(ByVal sectionName As String, ByVal keyName As String, ByVal value As String)
		WritePrivateProfileString(sectionName, keyName, value, _iniFile)
	End Sub

	Default Public ReadOnly Property Item(ByVal key As String) As IniSection
		Get
			Return Sections(key)
		End Get
	End Property


	Public Class IniSection
		Private _section As String
		Private _iniFile As String
		Private _kv As NameValueCollection = Nothing

		Public Sub New(ByVal iniFile As String, ByVal sectionName As String)
			_section = sectionName
			_iniFile = iniFile
		End Sub

		Public ReadOnly Property SectionName() As String
			Get
				Return _section
			End Get
		End Property

		Public ReadOnly Property Sections() As NameValueCollection
			Get
				If _kv Is Nothing Then
					ReadSection()
				End If
				Return _kv
			End Get
		End Property
		Default Public ReadOnly Property Item(ByVal key As String) As String
			Get
				Return Sections(key)
			End Get
		End Property

		Private Sub ReadSection()
			Dim ptr As IntPtr = Marshal.StringToHGlobalAnsi(New String(vbNullChar, MaxBuff))
			Dim len As Int32 = GetPrivateProfileSection(_section, ptr, MaxBuff, _iniFile)

			If len = MaxBuff - 2 OrElse len = 0 Then
				Throw New ApplicationException("Failed to read profile section, " + _section)
			End If

			Dim buff As String = Marshal.PtrToStringAnsi(ptr, len)
			Marshal.FreeHGlobal(ptr)


			_kv = New NameValueCollection

			Dim sb As New StringBuilder

			For ii As Integer = 0 To len - 1
				Dim c As Char = buff.Chars(ii)
				If c = vbNullChar Then
					Dim s As String = sb.ToString
					Dim ind As Integer = s.IndexOf("="c)
					_kv.Add(s.Substring(0, ind), s.Substring(ind + 1))
					sb.Length = 0
				Else
					sb.Append(c)
				End If
			Next
		End Sub

		Sub Delete()
			WritePrivateProfileString(_section, Nothing, Nothing, _iniFile)
		End Sub
		Sub DeleteKey(ByVal key As String)
			WritePrivateProfileString(_section, key, Nothing, _iniFile)
		End Sub
		Sub Add(ByVal key As String, ByVal value As String)
			WritePrivateProfileString(_section, key, value, _iniFile)
			_kv(key) = value
		End Sub

	End Class

End Class
