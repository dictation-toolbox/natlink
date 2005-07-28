Imports System.IO.IsolatedStorage
Imports System.Xml.Serialization
Imports System.ComponentModel

Public Class ConfigOptions

	Public Enum DisplayOptionsEnum
		SendMessageToWindow
		SendMessageToToaster
		HideMessages
	End Enum


	Dim _showSysTray As Boolean = True
	Public Property ShowSysTray() As Boolean
		Get
			Return _showSysTray
		End Get
		Set(ByVal Value As Boolean)
			_showSysTray = Value
		End Set
	End Property

	Dim _displayOption As DisplayOptionsEnum
	Public Property DisplayOption() As DisplayOptionsEnum
		Get
			Return _displayOption
		End Get
		Set(ByVal Value As DisplayOptionsEnum)
			_displayOption = Value
		End Set
	End Property

	Dim _errorDisplayOption As DisplayOptionsEnum
	Public Property ErrorDisplayOption() As DisplayOptionsEnum
		Get
			Return _errorDisplayOption
		End Get
		Set(ByVal Value As DisplayOptionsEnum)
			_errorDisplayOption = Value
		End Set
	End Property

	Dim _toasterTimeout As Integer = 5000
	<Bindable(True)> _
	Public Property ToasterTimeout() As Integer
		Get
			Return _toasterTimeout
		End Get
		Set(ByVal Value As Integer)
			_toasterTimeout = Value
		End Set
	End Property

	Dim _ignoreDupsDelay As Integer = 0
	Public Property IgnoreDupsDelay As integer
		Get
			Return _ignoreDupsDelay
		End Get
		Set(Byval Value As integer)
			_ignoreDupsDelay = Value
		End Set
	End Property

#Region "Window State"

	Dim _windowSize As Size
	Public Property WindowSize() As Size
		Get
			Return _windowSize
		End Get
		Set(ByVal Value As Size)
			_windowSize = Value
		End Set
	End Property
	Dim _windowLocation As Point
	Public Property WindowLocation() As Point
		Get
			Return _windowLocation
		End Get
		Set(ByVal Value As Point)
			_windowLocation = Value
		End Set
	End Property

	Dim _isErrorExpanded As Boolean
	Public Property IsErrorExpanded() As Boolean
		Get
			Return _isErrorExpanded
		End Get
		Set(ByVal Value As Boolean)
			_isErrorExpanded = Value
		End Set
	End Property
	Dim _isOutputExpanded As Boolean
	Public Property IsOutputExpanded() As Boolean
		Get
			Return _isOutputExpanded
		End Get
		Set(ByVal Value As Boolean)
			_isOutputExpanded = Value
		End Set
	End Property

	Dim _isConfigExpanded As Boolean
	Public Property IsConfigExpanded() As Boolean
		Get
			Return _isConfigExpanded
		End Get
		Set(ByVal Value As Boolean)
			_isConfigExpanded = Value
		End Set
	End Property
#End Region

#Region "save/load"

	Shared ReadOnly Property ConfigFile() As String
		Get
			Dim p As String
			p = IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "NatLink")
			IO.Directory.CreateDirectory(p)
			Return IO.Path.Combine(p, "Config.xml")
		End Get
	End Property

	'''REUSE ConfigOptionsBase
	Shared Function Load() As ConfigOptions
		'		Dim store As IsolatedStorageFile
		Dim stream As IO.StreamReader
		Dim xs As New XmlSerializer(GetType(ConfigOptions))
		Dim cfg As New ConfigOptions
		Try
			'			store = IsolatedStorageFile.GetUserStoreForDomain()
			'			store = IsolatedStorageFile.GetStore(IsolatedStorageScope.Assembly or IsolatedStorageScope.User ,null,
			'			stream = New IsolatedStorageFileStream("Config.xml", IO.FileMode.Open, store)
			stream = New IO.StreamReader(ConfigFile)

			cfg = DirectCast(xs.Deserialize(stream), ConfigOptions)
		Catch ex As IO.FileNotFoundException
		Catch ex As IsolatedStorageException
			MsgBox(ex.ToString)
		Finally

			If Not stream Is Nothing Then stream.Close()
			'		If Not store Is Nothing Then store.Close()
		End Try

		Return cfg

	End Function

	'''REUSE ConfigOptionsBase
	Shared Sub Save(ByVal cfg As ConfigOptions)
		'		Dim store As IsolatedStorageFile
		Dim stream As IO.StreamWriter
		Dim xs As New XmlSerializer(GetType(ConfigOptions))
		Try
			'			store = IsolatedStorageFile.GetUserStoreForDomain()
			'			stream = New IsolatedStorageFileStream("Config.xml", IO.FileMode.Create, store)
			stream = New IO.StreamWriter(ConfigFile, False)
			xs.Serialize(stream, cfg)
		Finally
			If Not stream Is Nothing Then stream.Close()
			'		If Not store Is Nothing Then store.Close()
		End Try
	End Sub
#End Region

End Class
