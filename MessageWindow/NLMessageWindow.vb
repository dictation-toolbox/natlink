Public Class NLMessageWindow

	Private Shared mw As MessageWindow = MessageWindow.Instance
	Public Sub ShowError(ByVal msg As String)
		mw.ShowError(msg)
	End Sub

	Public Sub ShowMessage(ByVal msg As String)
		mw.ShowMessage(msg)
	End Sub


End Class
