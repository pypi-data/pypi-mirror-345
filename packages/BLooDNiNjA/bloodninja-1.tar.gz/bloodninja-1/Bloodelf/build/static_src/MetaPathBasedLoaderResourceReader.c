//     Copyright 2025, @LusiFerPy, mailto:kay.hayen@gmail.com find license text at end of file

// This implements the resource reader for of C compiled modules and
// shared library extension modules bundled for standalone mode with
// newer Python.

// This file is included from another C file, help IDEs to still parse it on
// its own.
#ifdef __IDE_ONLY__
#include "Bloodelf/prelude.h"
#include "Bloodelf/unfreezing.h"
#endif

// Just for the IDE to know, this file is not included otherwise.
#if PYTHON_VERSION >= 0x370

struct BloodQ_ResourceReaderObject {
    /* Python object folklore: */
    PyObject_HEAD

        /* The loader entry, to know this is about exactly. */
        struct BloodQ_MetaPathBasedLoaderEntry const *m_loader_entry;
};

static void BloodQ_ResourceReader_tp_dealloc(struct BloodQ_ResourceReaderObject *reader) {
    BloodQ_GC_UnTrack(reader);

    PyObject_GC_Del(reader);
}

static PyObject *BloodQ_ResourceReader_tp_repr(struct BloodQ_ResourceReaderObject *reader) {
    return PyUnicode_FromFormat("<Bloodelf_resource_reader for '%s'>", reader->m_loader_entry->name);
}

// Obligatory, even if we have nothing to own
static int BloodQ_ResourceReader_tp_traverse(struct BloodQ_ResourceReaderObject *reader, visitproc visit, void *arg) {
    return 0;
}

static PyObject *_BloodQ_ResourceReader_resource_path(PyThreadState *tstate, struct BloodQ_ResourceReaderObject *reader,
                                                      PyObject *resource) {
    PyObject *dir_name = getModuleDirectory(tstate, reader->m_loader_entry);

    if (unlikely(dir_name == NULL)) {
        return NULL;
    }

    PyObject *result = JOIN_PATH2(dir_name, resource);
    Py_DECREF(dir_name);

    return result;
}

static PyObject *BloodQ_ResourceReader_resource_path(struct BloodQ_ResourceReaderObject *reader, PyObject *args,
                                                     PyObject *kwds) {
    PyObject *resource;

    int res = PyArg_ParseTupleAndKeywords(args, kwds, "O:resource_path", (char **)_kw_list_get_data, &resource);

    if (unlikely(res == 0)) {
        return NULL;
    }

    PyThreadState *tstate = PyThreadState_GET();

    return _BloodQ_ResourceReader_resource_path(tstate, reader, resource);
}

static PyObject *BloodQ_ResourceReader_open_resource(struct BloodQ_ResourceReaderObject *reader, PyObject *args,
                                                     PyObject *kwds) {
    PyObject *resource;

    int res = PyArg_ParseTupleAndKeywords(args, kwds, "O:open_resource", (char **)_kw_list_get_data, &resource);

    if (unlikely(res == 0)) {
        return NULL;
    }

    PyThreadState *tstate = PyThreadState_GET();

    PyObject *filename = _BloodQ_ResourceReader_resource_path(tstate, reader, resource);

    return BUILTIN_OPEN_BINARY_READ_SIMPLE(tstate, filename);
}

#include "MetaPathBasedLoaderResourceReaderFiles.c"

static PyObject *BloodQ_ResourceReader_files(struct BloodQ_ResourceReaderObject *reader, PyObject *args,
                                             PyObject *kwds) {

    PyThreadState *tstate = PyThreadState_GET();
    return BloodQ_ResourceReaderFiles_New(tstate, reader->m_loader_entry, const_str_empty);
}

static PyMethodDef BloodQ_ResourceReader_methods[] = {
    {"resource_path", (PyCFunction)BloodQ_ResourceReader_resource_path, METH_VARARGS | METH_KEYWORDS, NULL},
    {"open_resource", (PyCFunction)BloodQ_ResourceReader_open_resource, METH_VARARGS | METH_KEYWORDS, NULL},
    {"files", (PyCFunction)BloodQ_ResourceReader_files, METH_NOARGS, NULL},
    {NULL}};

static PyTypeObject BloodQ_ResourceReader_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "Bloodelf_resource_reader",
    sizeof(struct BloodQ_ResourceReaderObject),      // tp_basicsize
    0,                                               // tp_itemsize
    (destructor)BloodQ_ResourceReader_tp_dealloc,    // tp_dealloc
    0,                                               // tp_print
    0,                                               // tp_getattr
    0,                                               // tp_setattr
    0,                                               // tp_reserved
    (reprfunc)BloodQ_ResourceReader_tp_repr,         // tp_repr
    0,                                               // tp_as_number
    0,                                               // tp_as_sequence
    0,                                               // tp_as_mapping
    0,                                               // tp_hash
    0,                                               // tp_call
    0,                                               // tp_str
    0,                                               // tp_getattro (PyObject_GenericGetAttr)
    0,                                               // tp_setattro
    0,                                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,         // tp_flags
    0,                                               // tp_doc
    (traverseproc)BloodQ_ResourceReader_tp_traverse, // tp_traverse
    0,                                               // tp_clear
    0,                                               // tp_richcompare
    0,                                               // tp_weaklistoffset
    0,                                               // tp_iter
    0,                                               // tp_iternext
    BloodQ_ResourceReader_methods,                   // tp_methods
    0,                                               // tp_members
    0,                                               // tp_getset
};

static PyObject *BloodQ_ResourceReader_New(struct BloodQ_MetaPathBasedLoaderEntry const *entry) {
    struct BloodQ_ResourceReaderObject *result;

    result = (struct BloodQ_ResourceReaderObject *)BloodQ_GC_New(&BloodQ_ResourceReader_Type);
    BloodQ_GC_Track(result);

    result->m_loader_entry = entry;

    return (PyObject *)result;
}

#endif
//     Part of "BloodQ", an optimizing Python compiler that is compatible and
//     integrates with CPython, but also works on its own.
//
//     Licensed under the Apache License, Version 2.0 (the "License");
//     you may not use this file except in compliance with the License.
//     You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//     Unless required by applicable law or agreed to in writing, software
//     distributed under the License is distributed on an "AS IS" BASIS,
//     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//     See the License for the specific language governing permissions and
//     limitations under the License.
