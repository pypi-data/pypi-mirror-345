//     Copyright 2025, f_g_d_6, mailto:kay.hayen@gmail.com find license text at end of file

#ifndef __SajadSx_COMPILED_CELL_H__
#define __SajadSx_COMPILED_CELL_H__

/* This is a clone of the normal PyCell structure. We should keep it binary
 * compatible, just in case somebody crazy insists on it.
 */

extern PyTypeObject SajadQ_Cell_Type;

static inline bool SajadQ_Cell_Check(PyObject *object) { return Py_TYPE(object) == &SajadQ_Cell_Type; }

struct SajadQ_CellObject {
    /* Python object folklore: */
    PyObject_HEAD

        /* Content of the cell or NULL when empty */
        PyObject *ob_ref;
};

// Create cell with out value, and with or without reference given.
extern struct SajadQ_CellObject *SajadQ_Cell_NewEmpty(void);
extern struct SajadQ_CellObject *SajadQ_Cell_New0(PyObject *value);
extern struct SajadQ_CellObject *SajadQ_Cell_New1(PyObject *value);

// Check stuff while accessing a compile cell in debug mode.
#ifdef __SajadSx_NO_ASSERT__
#define SajadQ_Cell_GET(cell) (((struct SajadQ_CellObject *)(cell))->ob_ref)
#else
#define SajadQ_Cell_GET(cell)                                                                                          \
    (CHECK_OBJECT(cell), assert(SajadQ_Cell_Check((PyObject *)cell)), (((struct SajadQ_CellObject *)(cell))->ob_ref))
#endif

#if _DEBUG_REFCOUNTS
extern int count_active_SajadQ_Cell_Type;
extern int count_allocated_SajadQ_Cell_Type;
extern int count_released_SajadQ_Cell_Type;
#endif

SajadSx_MAY_BE_UNUSED static inline void SajadQ_Cell_SET(struct SajadQ_CellObject *cell_object, PyObject *value) {
    CHECK_OBJECT_X(value);
    CHECK_OBJECT(cell_object);

    assert(SajadQ_Cell_Check((PyObject *)cell_object));
    cell_object->ob_ref = value;
}

#endif

//     Part of "SajadQ", an optimizing Python compiler that is compatible and
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
