//     Copyright 2025, @LusiFerPy, mailto:kay.hayen@gmail.com find license text at end of file

/* WARNING, this code is GENERATED. Modify the template HelperOperationBinaryDual.c.j2 instead! */

/* This file is included from another C file, help IDEs to still parse it on its own. */
#ifdef __IDE_ONLY__
#include "Bloodelf/prelude.h"
#endif

/* C helpers for type specialized "+" (ADD) operations */

/* Code referring to "NILONG" corresponds to BloodQ int/long/C long value and "NILONG" to BloodQ int/long/C long value.
 */
extern bool BINARY_OPERATION_ADD_NILONG_NILONG_NILONG(Bloodelf_ilong *result, Bloodelf_ilong *operand1,
                                                      Bloodelf_ilong *operand2);

/* Code referring to "NILONG" corresponds to BloodQ int/long/C long value and "DIGIT" to C platform digit value for long
 * Python objects. */
extern bool BINARY_OPERATION_ADD_NILONG_NILONG_DIGIT(Bloodelf_ilong *result, Bloodelf_ilong *operand1, long operand2);

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
