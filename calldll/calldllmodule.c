/* -*- Mode: C++; tab-width: 4 -*- */

/* Copyright 1996-2001 by Sam Rushing <rushing@nightmare.com>
 * 
 *                         All Rights Reserved
 * 
 * Permission to use, copy, modify, and distribute this software and
 * its documentation for any purpose and without fee is hereby
 * granted, provided that the above copyright notice appear in all
 * copies and that both that copyright notice and this permission
 * notice appear in supporting documentation, and that the name of Sam
 * Rushing not be used in advertising or publicity pertaining to
 * distribution of the software without specific, written prior
 * permission.
 * 
 * SAM RUSHING DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
 * INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
 * NO EVENT SHALL SAM RUSHING BE LIABLE FOR ANY SPECIAL, INDIRECT OR
 * CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
 * OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
 * NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


Copyright (c) 1993-96 Massachusetts Institute of Technology

This material was developed by the Scheme project at the Massachusetts
Institute of Technology, Department of Electrical Engineering and
Computer Science.  Permission to copy this software, to redistribute
it, and to use it for any purpose is granted, subject to the following
restrictions and understandings.

1. Any copy made of this software must include this copyright notice
in full.

2. Users of this software agree to make their best efforts (a) to
return to the MIT Scheme project any improvements or extensions that
they make, so that these may be included in future releases; and (b)
to inform MIT of noteworthy uses of this software.

3. All materials developed as a consequence of the use of this
software shall duly acknowledge such use, in accordance with the usual
standards of acknowledging credit in academic research.

4. MIT has made no warrantee or representation that the operation of
this software will be error-free, and MIT is under no obligation to
provide any services, by way of maintenance, update, or otherwise.

5. In conjunction with products arising from the use of this material,
there shall be no use of the name of the Massachusetts Institute of
Technology nor of any adaptation thereof in any advertising,
promotional, or sales literature without prior written consent from
MIT in each case.
*/

#ifdef _WIN32
#  include <windows.h>
#else /* linux */
#  include <dlfcn.h>
#endif

#include "Python.h"

static PyObject *calldll_module_error;

#ifdef _WIN32

/* */
/* adapated from MIT Scheme, 7.3, microcode/ntgui.c. */
/* */

// SMR: not sure if the assembly tricks are still necessary...

static long
call_ff_really (long function_address,
				char * arg_format_string,
				PyObject * arg_tuple,
				long * result_addr)
{
  {
	/*	use a struct for locals that live across the foreign function call
		so that their position in the stack is the right end of the stack
		frame with respect to the stacked C arguments */
	struct {
	  long c_args[30];
	  long old_esp;
	} local;
	
	long result;

	/*	We save the stack pointer and restore it because the called function
		may pop the arguments (pascal/__stdcall) or expect us to (__cdecl). */

	/*	The stack pointer is saved in a static variable so that we can find
		it if the compiler does SP-relative addressing with a broken SP */
	
	/*	The implication is that things will break if this gets overwritten.
		This will happen if the foreign function directly or indirectly 
		allows a Scheme interrupt to be processed (eg by calling as scheme
		function with interrupts enabled and that function gets rescheduled
		in the threads package. */
	
	static long saved_esp;
	
	{
	  long *arg_sp = &local.c_args[10];
	  long	funadd = function_address;

	  if (!PyArg_ParseTuple (arg_tuple,
							 arg_format_string,
							 &local.c_args[10],
							 &local.c_args[11],
							 &local.c_args[12],
							 &local.c_args[13],
							 &local.c_args[14],
							 &local.c_args[15],
							 &local.c_args[16],
							 &local.c_args[17],
							 &local.c_args[18],
							 &local.c_args[19],
							 &local.c_args[20],
							 &local.c_args[21],
							 &local.c_args[22],
							 &local.c_args[23],
							 &local.c_args[24],
							 &local.c_args[25],
							 &local.c_args[26],
							 &local.c_args[27],
							 &local.c_args[28],
							 &local.c_args[29])) {
		return 0;
	  }

	  arg_sp = &local.c_args[10];
	  local.old_esp = saved_esp;

#ifndef __GNUC__
	  __asm
		{
		  /* Important: The order of these instructions guards against */
		  /* stack pointer relative addressing. */
		  mov	eax, dword ptr [funadd]
		  mov	dword ptr [saved_esp], esp
		  mov	esp, dword ptr [arg_sp]
		  call	eax
		  mov	esp, dword ptr [saved_esp]
		  mov	dword ptr [result], eax
		}
#else
	  __asm__ (
			   "
		movl %0, %%eax
		movl %%esp, %1
		movl %2, %%esp
		call *%%eax
		movl %1, %%esp
		movl %%eax, %3
"
			   : 
			   : "g" (funadd), "g" (saved_esp), "g" (arg_sp), "g" (result)
			   );
#endif
		saved_esp = local.old_esp;
		
		*result_addr = result;
		return 1;
	}
  }
}

#else

call_ff_really (
  long			function_address,
  char *		arg_format_string,
  PyObject *	arg_tuple,
  long *		result_addr
  )
{
  long args[10];

  if (!PyArg_ParseTuple (
        arg_tuple,
		arg_format_string,
		&args[0], &args[1], &args[2], &args[3], &args[4],
		&args[5], &args[6], &args[7], &args[8], &args[9]
		)
	  ) { 
	return 0;
  } else {
	(*result_addr) = ((long (*)())function_address) (
               args[0], args[1], args[2], args[3], args[4],
			   args[5], args[6], args[7], args[8], args[9]
			   );
	return 1;
  }
}

#endif

static
PyObject *
call_foreign_function (PyObject * self, PyObject * args)
{
  long function_address;
  char * arg_format_string;
  char * result_format_string;
  PyObject * arg_tuple;
  long result;

  if (!PyArg_ParseTuple (args, "lssO",
						 &function_address,
						 &arg_format_string,
						 &result_format_string,
						 &arg_tuple)) {
	return NULL;
  } else {
	if (!call_ff_really (function_address,
						 arg_format_string,
						 arg_tuple,
						 &result)) {
	  return NULL;
	} else {
	  return Py_BuildValue (result_format_string, result);
	}
  }
}

#ifdef _WIN32
static PyObject *
py_load_library (PyObject * self, PyObject * args)
{
  LPCTSTR name;
  if (!PyArg_ParseTuple (args, "s", &name)) {
	return NULL;
  } else {
	return Py_BuildValue ("l", LoadLibrary (name));
  }
}

static PyObject *
py_get_module_handle (PyObject * self, PyObject * args)
{
  LPCTSTR name;
  if (!PyArg_ParseTuple (args, "s", &name)) {
	return NULL;
  } else {
	return Py_BuildValue ("l", GetModuleHandle (name));
  }
}

static PyObject *
py_free_library (PyObject * self, PyObject * args)
{
  HMODULE dll_handle;
  if (!PyArg_ParseTuple (args, "l", &dll_handle)) {
	return NULL;
  } else {
	return Py_BuildValue ("i", (int) FreeLibrary (dll_handle));
  }
}

static PyObject *
py_get_proc_address (PyObject * self, PyObject * args)
{
  HMODULE dll_handle;
  LPCSTR proc_name;
  
  if (!PyArg_ParseTuple (args, "ls", &dll_handle, &proc_name)) {
	return NULL;
  } else {
	return Py_BuildValue ("l",  GetProcAddress (dll_handle, proc_name));
  }
}

#else

static PyObject *
py_load_library (PyObject * self, PyObject * args)
{
  char * name;
  if (!PyArg_ParseTuple (args, "s", &name)) {
	return NULL;
  } else {
	return Py_BuildValue ("l", (long) dlopen (name, RTLD_LAZY));
  }
}

static PyObject *
py_free_library (PyObject * self, PyObject * args)
{
  void * dll_handle;
  if (!PyArg_ParseTuple (args, "l", &dll_handle)) {
	return NULL;
  } else {
	return Py_BuildValue ("i", dlclose (dll_handle));
  }
}

static PyObject *
py_get_proc_address (PyObject * self, PyObject * args)
{
  void * dll_handle;
  char * proc_name;
  
  if (!PyArg_ParseTuple (args, "ls", &dll_handle, &proc_name)) {
	return NULL;
  } else {
	return Py_BuildValue ("l", (long) dlsym (dll_handle, proc_name));
  }
}

#endif


static PyObject *
py_read_long (PyObject * self, PyObject * args)
{
  void * address;

  if (!PyArg_ParseTuple (args, "l", &address)) {
	return NULL;
  } else {
	return Py_BuildValue ("l", *((long *)address));
  }
}

static PyObject *
py_read_byte (PyObject * self, PyObject * args)
{
  void * address;

  if (!PyArg_ParseTuple (args, "l", &address)) {
	return NULL;
  } else {
	return Py_BuildValue ("b", *((char *)address));
  }
}

static PyObject *
py_read_string (PyObject * self, PyObject * args)
{
  void * address;
  int length = 0;

  if (!PyArg_ParseTuple (args, "l|i", &address, &length)) {
	return NULL;
  } else if (length == 0) {
	return Py_BuildValue ("s", (char *)address);
  } else {
	return Py_BuildValue ("s#", (char *)address, length);
  }
}

/* =========================================================================== */
/* memory buffer objects */
/* =========================================================================== */

typedef struct {
	PyObject_HEAD
	void *	buffer;
	size_t	size;
} membuf_object;

static void
membuf_object_dealloc(membuf_object * m_obj)
{
  free (m_obj->buffer);
  PyMem_DEL(m_obj);
}

static PyObject *
membuf_read_method (membuf_object * self,
					PyObject * args)
{
  unsigned int offset = 0;
  unsigned int size = 0;
  
  if (!PyArg_ParseTuple (args, "|ii", &offset, &size)) {
    return(NULL);
  }

  if ((offset + size) > self->size) {
	PyErr_SetString (PyExc_ValueError, "offset+size is larger than buffer");
	return NULL;
  } else {
	return Py_BuildValue ("s#", ((char *)(self->buffer)) + offset, size ? size : self->size);
  }
}

static PyObject *
membuf_write_method (membuf_object * self,
					 PyObject * args)
{
  int offset=0;
  unsigned int length=0;
  int string_length;
  char * data;

  if (!PyArg_ParseTuple (args, "s#|ii", &data, &string_length, &offset, &length)) {
    return(NULL);
  } else if (length == 0) {
	length = string_length;
  }

  if (length > self->size) {
	PyErr_SetString (PyExc_ValueError, "input string size is larger than buffer");
	return NULL;
  } else {
	memcpy (((char *)(self->buffer))+offset, data, length);
	Py_INCREF (Py_None);
	return (Py_None);
  }
}

static PyObject *
membuf_size_method (membuf_object * self,
					PyObject * args)
{
  if (!PyArg_ParseTuple (args, "")) {
	return NULL;
  } else {
	return Py_BuildValue ("i", self->size);
  }
}

static PyObject *
membuf_address_method (membuf_object * self,
					   PyObject * args)
{
  if (!PyArg_ParseTuple (args, "")) {
	return NULL;
  } else {
	return Py_BuildValue ("l", (self->buffer));
  }
}

static struct PyMethodDef membuf_object_methods[] = {
  {"read",		(PyCFunction)	membuf_read_method,		1},
  {"write",		(PyCFunction)	membuf_write_method,	1},
  {"size",		(PyCFunction)	membuf_size_method,		1},
  {"address",	(PyCFunction)	membuf_address_method,	1},
  {"__int__",	(PyCFunction)	membuf_address_method,	1},
  {NULL,		NULL}		/* sentinel */
};

static PyObject *
membuf_object_getattr(membuf_object * self, char * name)
{
  return Py_FindMethod (membuf_object_methods, (PyObject *)self, name);
}

static PyTypeObject membuf_object_type = {
	PyObject_HEAD_INIT(NULL)
	0,							/* ob_size */
	"membuf",					/* tp_name */
	sizeof(membuf_object), 		/* tp_size */
	0,							/* tp_itemsize */
	/* methods */
	(destructor) membuf_object_dealloc,/* tp_dealloc */
	0,							/* tp_print */
	(getattrfunc) membuf_object_getattr, /* tp_getattr */
	0,							/* tp_setattr */
	0,							/* tp_compare */
	0,							/* tp_repr */
	0,							/* tp_as_number */
};

static PyObject *
new_membuf_object (PyObject * self, PyObject * args)
{
  membuf_object * m_obj;
  int size;
  void * buffer;

  if (!PyArg_ParseTuple (args, "i", &size)) {
	return NULL;
  } else {
	buffer = (void *) malloc (size);
	if (!buffer) {
	  PyErr_SetString (PyExc_MemoryError, "couldn't allocate memory for buffer");
	  return NULL;
	} else {
	  m_obj = PyObject_NEW (membuf_object, &membuf_object_type);
	  if (!m_obj) {
		free (buffer);
		PyErr_SetString (PyExc_MemoryError, "couldn't allocate memory for buffer object");
		return NULL;
	  } else {
		m_obj->size = size;
		m_obj->buffer = buffer;
		return (PyObject *) m_obj;
	  }
	}
  }
}

/* =========================================================================== */
/* */
/* =========================================================================== */

/* List of functions exported by this module */
static struct PyMethodDef calldll_functions[] = {
  {"call_foreign_function",	(PyCFunction) call_foreign_function,1},
  {"load_library",			(PyCFunction) py_load_library,		1},
  {"free_library",			(PyCFunction) py_free_library,		1},
#ifdef _WIN32
  {"get_module_handle",		(PyCFunction) py_get_module_handle, 1},  
#endif
  {"get_proc_address",		(PyCFunction) py_get_proc_address,	1},
  {"read_long",				(PyCFunction) py_read_long,			1},
  {"read_byte",				(PyCFunction) py_read_byte,			1},
  {"read_string",			(PyCFunction) py_read_string,		1},
  {"membuf",				(PyCFunction) new_membuf_object,	1},
  {NULL,			NULL}		 /* Sentinel */
};

__declspec(dllexport)  void initcalldll(void)
{
	PyObject *dict, *module;
	membuf_object_type.ob_type = &PyType_Type;
	module = Py_InitModule ("calldll", calldll_functions);
	dict = PyModule_GetDict (module);
	calldll_module_error = PyString_FromString ("calldll error");
	PyDict_SetItemString (dict, "error", calldll_module_error);
	PyDict_SetItemString (dict, "addrs",
						  Py_BuildValue ("(lll)",
										 &Py_BuildValue,
										 &PyInt_AsLong,
										 &PyEval_CallObject));
}
