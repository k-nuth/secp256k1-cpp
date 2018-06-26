#
# Copyright (c) 2017-2018 Bitprim Inc.
#
# This file is part of Bitprim.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


function(_check_has_64bit_asm)
    if (DEFINED HAS_64BIT_ASM)
        return()
    endif()

    set(_filename "${CMAKE_BINARY_DIR}/${CMAKE_FILES_DIRECTORY}/_has_64bit_asm.c")
    file(WRITE ${_filename}
            "#include <stdint.h>
    int main() {
      uint64_t a = 11, tmp;
      __asm__ __volatile__(\"movq 0x100000000,%1; mulq %%rsi\" : \"+a\"(a) : \"S\"(tmp) : \"cc\", \"%rdx\");
    }")
    try_compile(HAS_64BIT_ASM "${CMAKE_BINARY_DIR}" ${_filename})
    set(HAS_64BIT_ASM ${HAS_64BIT_ASM} PARENT_SCOPE)
    file(REMOVE ${_filename})
endfunction()

function(_check_has_int128)
    if (DEFINED HAS_INT128)
        return()
    endif()

    set(_filename "${CMAKE_BINARY_DIR}/${CMAKE_FILES_DIRECTORY}/_has_int128_test.c")
    file(WRITE ${_filename}
            "int main() { __int128 x = 0; }")
    try_compile(HAS_INT128 "${CMAKE_BINARY_DIR}" ${_filename})
    set(HAS_INT128 ${HAS_INT128} PARENT_SCOPE)
    file(REMOVE ${_filename})
endfunction()

function(_check_has_gmp)
    if (DEFINED HAS_GMP)
        return()
    endif()

    find_package(GMP)
    set(HAS_GMP ${GMP_FOUND} PARENT_SCOPE)
endfunction()

