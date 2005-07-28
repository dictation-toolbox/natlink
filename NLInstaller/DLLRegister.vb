Imports System
Imports System.Reflection
Imports System.Reflection.Emit
Imports System.Runtime.InteropServices


Public Class DllRegServer

	Private m_sDllFile As String
	Private Shared s_mb As ModuleBuilder
	Private m_tDllReg As Type


  Public  Sub New(ByVal dllFile As String)
		m_sDllFile = dllFile
		CreateDllRegType()
	End Sub


	Public Sub Register()
		InternalRegServer(False)
	End Sub

	Public Sub UnRegister()
		InternalRegServer(True)
	End Sub

	Private Sub InternalRegServer(ByVal fUnreg As Boolean)
		Dim sMemberName As String
		Dim hr As Integer

		If fUnreg Then
			sMemberName = "DllUnregisterServer"
		Else
			sMemberName = "DllRegisterServer"
		End If
		hr = CInt(m_tDllReg.InvokeMember(sMemberName, BindingFlags.InvokeMethod, Nothing, Activator.CreateInstance(m_tDllReg), Nothing))
		If hr <> 0 Then
			Marshal.ThrowExceptionForHR(hr)
		End If
	End Sub

	Private Sub CreateDllRegType()
		If s_mb Is Nothing Then
			' Create dynamic assembly    
			Dim an As AssemblyName = New AssemblyName
			an.Name = "DllRegServerAssembly" + Guid.NewGuid().ToString("N")
			Dim ab As AssemblyBuilder = AppDomain.CurrentDomain.DefineDynamicAssembly(an, AssemblyBuilderAccess.Run)
			s_mb = ab.DefineDynamicModule("DllRegServerModule")
		End If

		' Add class to module
		Dim tb As TypeBuilder = s_mb.DefineType("DllRegServerClass" + Guid.NewGuid().ToString("N"))

		Dim meb As MethodBuilder

		' Add PInvoke methods to class
		meb = tb.DefinePInvokeMethod("DllRegisterServer", m_sDllFile, _
		  MethodAttributes.Public Or MethodAttributes.Static Or MethodAttributes.PinvokeImpl, _
		  CallingConventions.Standard, GetType(Integer), Nothing, CallingConvention.StdCall, CharSet.Auto)

		' Apply preservesig metadata attribute so we can handle return HRESULT ourselves
		meb.SetImplementationFlags(MethodImplAttributes.PreserveSig Or meb.GetMethodImplementationFlags())

		meb = tb.DefinePInvokeMethod("DllUnregisterServer", m_sDllFile, _
		  MethodAttributes.Public Or MethodAttributes.Static Or MethodAttributes.PinvokeImpl, _
		  CallingConventions.Standard, GetType(Integer), Nothing, CallingConvention.StdCall, CharSet.Auto)

		' Apply preservesig metadata attribute so we can handle return HRESULT ourselves
		meb.SetImplementationFlags(MethodImplAttributes.PreserveSig Or meb.GetMethodImplementationFlags())

		' Create the type
		m_tDllReg = tb.CreateType()
	End Sub

End Class
