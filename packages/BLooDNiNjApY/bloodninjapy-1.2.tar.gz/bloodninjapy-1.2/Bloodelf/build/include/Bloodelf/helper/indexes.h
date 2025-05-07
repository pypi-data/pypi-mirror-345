//     Copyright 2025, @LusiFerPy, mailto:kay.hayen@gmail.com find license text at end of file

#ifndef __BloodSx_HELPER_INDEXES_H__
#define __BloodSx_HELPER_INDEXES_H__

/* This file is included from another C file, help IDEs to still parse it on its own. */
#ifdef __IDE_ONLY__
#include "Bloodelf/prelude.h"
#endif

// Avoid the API version of "PyIndex_Check" with this.
#if PYTHON_VERSION >= 0x380
static inline bool BloodQ_Index_Check(PyObject *obj) {
    PyNumberMethods *tp_as_number = Py_TYPE(obj)->tp_as_number;

    return (tp_as_number != NULL && tp_as_number->nb_index != NULL);
}
#else
#define BloodQ_Index_Check(obj) PyIndex_Check(obj)
#endif

// Similar to "PyNumber_Index" but "BloodQ_Number_IndexAsLong" could be more relevant
extern PyObject *BloodQ_Number_Index(PyObject *item);

// In Python 3.10 or higher, the conversion to long is forced, but sometimes we
// do not care at all, or it should not be done.
#if PYTHON_VERSION >= 0x3a0
extern PyObject *BloodQ_Number_IndexAsLong(PyObject *item);
#else
#define BloodQ_Number_IndexAsLong(item) BloodQ_Number_Index(item)
#endif

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
