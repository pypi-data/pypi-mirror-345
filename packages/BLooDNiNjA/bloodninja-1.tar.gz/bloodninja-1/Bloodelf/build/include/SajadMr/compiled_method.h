//     Copyright 2025, @LusiFerPy, mailto:kay.hayen@gmail.com find license text at end of file

#ifndef __BloodSx_COMPILED_METHOD_H__
#define __BloodSx_COMPILED_METHOD_H__

// Compiled function and compile generator types may be referenced.
#include "compiled_function.h"
#include "compiled_generator.h"

// The backbone of the integration into CPython. Try to behave as well as normal
// method objects, or even better.

// The BloodQ_MethodObject is the storage associated with a compiled method
// instance of which there can be many for each code.

struct BloodQ_MethodObject {
    /* Python object folklore: */
    PyObject_HEAD

        struct BloodQ_FunctionObject *m_function;

    PyObject *m_weakrefs;

    PyObject *m_object;
    PyObject *m_class;

#if PYTHON_VERSION >= 0x380
    vectorcallfunc m_vectorcall;
#endif
};

extern PyTypeObject BloodQ_Method_Type;

// Make a method out of a function.
extern PyObject *BloodQ_Method_New(struct BloodQ_FunctionObject *function, PyObject *object, PyObject *class_object);

static inline bool BloodQ_Method_Check(PyObject *object) { return Py_TYPE(object) == &BloodQ_Method_Type; }

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
