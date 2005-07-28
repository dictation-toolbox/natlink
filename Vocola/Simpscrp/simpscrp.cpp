// Made by Paulo Soares - psoares@consiste.pt
// Use in whatever ways you want.

#include "stdafx.h"
#include "Python.h"
#include "PlayKeys.h"

BOOL APIENTRY DllMain( HANDLE hModule, 
                       DWORD  ul_reason_for_call, 
                       LPVOID lpReserved
					 )
{
    return TRUE;
}


static BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam)
{
    char buf[300];

    int rc = GetWindowText(hwnd, buf, sizeof(buf));
    if (rc)
    {
        PyObject* list = (PyObject*)lParam;
        PyObject* tuple = PyTuple_New(2);
        PyTuple_SetItem(tuple, 0, PyInt_FromLong((long)hwnd));
        PyTuple_SetItem(tuple, 1, PyString_FromString(buf));
        PyList_Append(list, tuple);
    }
    return TRUE;
}


extern "C"{
static PyObject* send_keys(PyObject* self, PyObject* args)
{
    char* buf;
    UINT d;
    UINT erro;

    if (!PyArg_ParseTuple(args, "s", &buf))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    erro = PlayKeys(buf, &d);
    Py_END_ALLOW_THREADS
    return PyInt_FromLong((long)erro);
}

static PyObject* message_box(PyObject* self, PyObject* args)
{
    char* buf;
    int result;
    UINT type = MB_OK;

    if (!PyArg_ParseTuple(args, "s|i", &buf, &type))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    result = MessageBox(GetForegroundWindow(), buf, "Message", type);
    Py_END_ALLOW_THREADS
    return PyInt_FromLong((long)result);
}

static PyObject* enum_windows(PyObject* self, PyObject* args)
{
    if (PyTuple_Size(args))
        return NULL;
    PyObject* list = PyList_New(0);
    EnumWindows(EnumWindowsProc, (LPARAM)list);
    return list;
}

static PyObject* set_foreground_window(PyObject* self, PyObject* args)
{
    long window;
    HWND hwnd;
    long result;

    if (!PyArg_ParseTuple(args, "i", &window))
        return NULL;
    hwnd = (HWND)window;
    if (IsWindow(hwnd))
    {
        SetForegroundWindow(hwnd);
        result = 0;
    }
    else
        result = 1;
    return PyInt_FromLong((long)result);
}

static PyObject* exec_app(PyObject* self, PyObject* args)
{
    char* buf;
    long wait = 0;
    int error;

    if (!PyArg_ParseTuple(args, "s|i", &buf, &wait))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    STARTUPINFO          sui;
    PROCESS_INFORMATION  pi;
    memset(&sui, 0, sizeof(sui));
    sui.cb               = sizeof (STARTUPINFO);
/* This will hide the window */
    sui.dwFlags          = STARTF_USESHOWWINDOW;
    sui.wShowWindow      = SW_HIDE;
/*****************************/

    if (error = CreateProcess (NULL, buf, NULL, NULL,
        FALSE, CREATE_DEFAULT_ERROR_MODE,
        NULL, NULL, &sui, &pi ))
    {
        WaitForInputIdle(pi.hProcess, 30000);
        if (wait)
            WaitForSingleObject(pi.hProcess, INFINITE);
    }
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    Py_END_ALLOW_THREADS
    return PyInt_FromLong((long)(error == 0));
}

static PyMethodDef simpscrp_methods[] =
{
    {"SendKeys", send_keys, 1, "SendKeys(keys)\nSend keys to the window with focus. The sintax is the same as VB.\nReturns 0 if successeful."},
    {"MessageBox", message_box, 1, "MessageBox(message, type)\nShow a message box. See the win api for the values\nof type and return. Type defaults to MB_OK."},
    {"EnumWindows", enum_windows, 1, "EnumWindows()\nReturns a list of the top windows in the format (hwnd, caption)."},
    {"SetForegroundWindow", set_foreground_window, 1, "SetForegroundWindow(hwnd)\nMake a window the focus window. Returns 0 if successeful."},
    {"Exec", exec_app, 1, "Exec(command,wait)\nExecutes a command and optionally waits for it's completion.\nWait defaults to 0. Returns 0 if successeful."},
    {NULL, NULL}
};

__declspec(dllexport) void initsimpscrp()
{
    Py_InitModule3("simpscrp", simpscrp_methods,
        "Module simpscrp - Simple scripting functions.\n"
        "Made by Paulo Soares - psoares@consiste.pt\n"
        "Use in whatever ways you want.\n");
}
}