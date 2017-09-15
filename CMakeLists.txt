#
# Copyright (c) 2017 Bitprim developers (see AUTHORS)
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

cmake_minimum_required(VERSION 3.4)

# secp256k1
#==============================================================================
project(secp256k1
  VERSION 0.2
  LANGUAGES C)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

# Process options.
#==============================================================================
# Implement --use-conan
#------------------------------------------------------------------------------
option(USE_CONAN "Use Conan Build Tool." OFF)
option(NO_CONAN_AT_ALL "Conan totally disabled." OFF)

if (NO_CONAN_AT_ALL)
  set(USE_CONAN OFF)
endif()


option(ENABLE_BENCHMARK "Compile benchmark." OFF)
option(ENABLE_TESTS "Compile tests." ON)
option(ENABLE_OPENSSL_TESTS "Enable OpenSSL tests, if OpenSSL is available" OFF)
option(ENABLE_EXPERIMENTAL "Alloc experimental configure options" OFF)
option(ENABLE_ENDOMORPHISM "Enable endomorphism" OFF)
option(ENABLE_ECMULT_STATIC_PRECOMPUTATION "Enable precomputed ecmult table for signing" ON)
option(ENABLE_MODULE_ECDH "Enable ECDH shared secret computation (experimental)." OFF)
option(ENABLE_MODULE_SCHNORR "Enable Schnorr signature module (experimental)." OFF)
option(ENABLE_MODULE_RECOVERY "Enable ECDSA pubkey recovery module." ON)

message(${ENABLE_TESTS})



# option(WITH_BIGNUM "")

#TODO(fernando): Implement the following with_... as options
set(WITH_ASM "auto" CACHE STRING "Specify assembly optimizations to use (x86_64|arm|no|auto).")
set(WITH_FIELD "auto" CACHE STRING "Specify Field Implementation (64bit|32bit|auto).")
set(WITH_SCALAR "auto" CACHE STRING "Specify scalar implementation (64bit|32bit|auto).")
set(WITH_BIGNUM "auto" CACHE STRING "Specify Bignum Implementation (gmp|no|auto).")

message(${WITH_BIGNUM})

if (NOT NO_CONAN_AT_ALL)
  if(EXISTS ${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
      include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
      conan_basic_setup()
  else()
      message(WARNING "The file conanbuildinfo.cmake doesn't exist, you have to run conan install first")
  endif()
endif()


set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

include(Secp256k1Tools)


# Implement --with-asm
#------------------------------------------------------------------------------
if (WITH_ASM STREQUAL "auto")
  _check_has_64bit_asm()
  if (HAS_64BIT_ASM)
    set(WITH_ASM "x86_64")
  else()
    set(WITH_ASM "no")
  endif()
elseif (WITH_ASM STREQUAL "x86_64")
  _check_has_64bit_asm()
  if (NOT HAS_64BIT_ASM)
    message(FATAL_ERROR "x86_64 assembly optimization requested but not available")
  endif()
elseif (NOT WITH_ASM STREQUAL "arm" AND NOT WITH_ASM STREQUAL "no")
  message(FATAL_ERROR "Invalid assembly optimization selection: ${WITH_ASM}")
endif()

# Implement --with-field
#------------------------------------------------------------------------------
if (WITH_FIELD STREQUAL "auto")
  if (WITH_ASM STREQUAL "x86_64")
    set (WITH_FIELD "64bit")
  else()
    _check_has_int128()
    if (HAS_INT128)
      set(WITH_FIELD "64bit")
    else()
      set(WITH_FIELD "32bit")
    endif()
  endif()
elseif (WITH_FIELD STREQUAL "64bit")
  if (NOT WITH_ASM STREQUAL "x86_64")
    _check_has_int128()
    if (NOT HAS_INT128)
      message(FATAL_ERROR "64bit field explicitly requested but neither __int128 support or x86_64 assembly available")
    endif()
  endif()
elseif (NOT WITH_FIELD STREQUAL "32bit")
  message(FATAL_ERROR "Invalid field implementation: ${WITH_FIELD}")
endif()

# Implement --with-scalar
#------------------------------------------------------------------------------
if (WITH_SCALAR STREQUAL "auto")
  _check_has_int128()
  if (HAS_INT128)
    set(WITH_SCALAR "64bit")
  else()
    set(WITH_SCALAR "32bit")
  endif()
elseif (WITH_FIELD STREQUAL "64bit")
  _check_has_int128()
  if (NOT HAS_INT128)
    message(FATAL_ERROR "64bit scalar explicitly requested but __int128 support not available")
  endif()
elseif (NOT WITH_FIELD STREQUAL "32bit")
  message(FATAL_ERROR "Invalid scalar implementation: ${WITH_SCALAR}")
endif()

#TODO(fernando): Bignum for Windows. See MPR (or something like this) that is a GMP for Windows.
# Implement --with-bignum
#------------------------------------------------------------------------------
if (NO_CONAN_AT_ALL)
  if (${WITH_BIGNUM} STREQUAL "auto")
    _check_has_gmp()
    if (HAS_GMP)
      set(WITH_BIGNUM "gmp")
    else()
      set(WITH_BIGNUM "no")
    endif()
  elseif (WITH_BIGNUM STREQUAL "gmp")
    _check_has_gmp()
    if (NOT HAS_GMP)
      message(FATAL_ERROR "gmp bignum explicitly requested but libgmp not available")
    endif()
  elseif (NOT ${WITH_BIGNUM} STREQUAL "no")
    message(FATAL_ERROR "Invalid bignum implementation: ${WITH_BIGNUM}")
  endif()
endif()


# Build
#==============================================================================
add_library(secp256k1 STATIC
  include/secp256k1.h
  src/secp256k1.c)

set_property(TARGET secp256k1 PROPERTY POSITION_INDEPENDENT_CODE ON)
  
target_include_directories(secp256k1 PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR})

target_include_directories(secp256k1 PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

_check_has_int128()
if (HAS_INT128)
  target_compile_definitions(secp256k1 PUBLIC -DHAVE___INT128=1)
endif()

if (WITH_ASM STREQUAL "x86_64")
  target_compile_definitions(secp256k1 PUBLIC -DUSE_ASM_X86_64=1)
elseif (WITH_FIELD STREQUAL "arm")
  target_compile_definitions(secp256k1 PUBLIC -DUSE_EXTERNAL_ASM=1)
  target_sources(secp256k1 PRIVATE "src/asm/field_10x26_arm.s")
endif()

if (WITH_FIELD STREQUAL "64bit")
  target_compile_definitions(secp256k1 PUBLIC -DUSE_FIELD_5X52=1)
elseif (WITH_FIELD STREQUAL "32bit")
  target_compile_definitions(secp256k1 PUBLIC -DUSE_FIELD_10X26=1)
endif()

if (WITH_SCALAR STREQUAL "64bit")
  target_compile_definitions(secp256k1 PUBLIC -DUSE_SCALAR_4X64=1)
elseif (WITH_SCALAR STREQUAL "32bit")
  target_compile_definitions(secp256k1 PUBLIC -DUSE_SCALAR_8X32=1)
endif()

message("fer WITH_BIGNUM: ")
message(WITH_ASM)
message(WITH_FIELD)
message(WITH_SCALAR)
message(${WITH_BIGNUM})

if (${WITH_BIGNUM} STREQUAL "auto")
  message("fer WITH_BIGNUM auto")
else()
  message("fer WITH_BIGNUM auto - FALSE")
endif()

message(WITH_BIGNUM)
message(${WITH_BIGNUM})
if (${WITH_BIGNUM} STREQUAL "gmp")
  target_compile_definitions(secp256k1 PUBLIC -DHAVE_LIBGMP=1)
  target_compile_definitions(secp256k1 PUBLIC -DUSE_NUM_GMP=1)
  target_compile_definitions(secp256k1 PUBLIC -DUSE_FIELD_INV_NUM=1)
  target_compile_definitions(secp256k1 PUBLIC -DUSE_SCALAR_INV_NUM=1)

  if (NO_CONAN_AT_ALL)
    target_include_directories(secp256k1 PUBLIC ${GMP_INCLUDE_DIR})
    target_link_libraries(secp256k1 ${GMP_LIBRARIES})
  endif()
elseif (${WITH_BIGNUM} STREQUAL "no")
  target_compile_definitions(secp256k1 PUBLIC -DUSE_NUM_NONE=1)
  target_compile_definitions(secp256k1 PUBLIC -DUSE_FIELD_INV_BUILTIN=1)
  target_compile_definitions(secp256k1 PUBLIC -DUSE_SCALAR_INV_BUILTIN=1)
endif()


# message(CONAN_LIBS)
# message(${CONAN_LIBS})

if (NOT NO_CONAN_AT_ALL)
  target_link_libraries(secp256k1 PUBLIC ${CONAN_LIBS})
endif()

if (ENABLE_MODULE_ECDH)
  target_compile_definitions(secp256k1 PUBLIC -DENABLE_MODULE_ECDH=1)
endif()
if (ENABLE_MODULE_SCHNORR)
  target_compile_definitions(secp256k1 PUBLIC -DENABLE_MODULE_SCHNORR=1)
endif()
if (ENABLE_MODULE_RECOVERY)
  target_compile_definitions(secp256k1 PUBLIC -DENABLE_MODULE_RECOVERY=1)
endif()

set_target_properties(secp256k1 PROPERTIES FOLDER "secp256k1")

# Benchmark
#==============================================================================
if (ENABLE_BENCHMARK)
  add_executable(bench_verify src/bench_verify.c)
  target_link_libraries(bench_verify secp256k1)
  set_target_properties(bench_verify PROPERTIES FOLDER "secp256k1")

  add_executable(bench_sign src/bench_sign.c)
  target_link_libraries(bench_sign secp256k1)
  set_target_properties(bench_sign PROPERTIES FOLDER "secp256k1")

  add_executable(bench_internal src/bench_internal.c)
  target_link_libraries(bench_internal secp256k1)
  set_target_properties(bench_internal PROPERTIES FOLDER "secp256k1")

  if (ENABLE_MODULE_ECDH)
    add_executable(bench_ecdh src/bench_ecdh.c)
    target_link_libraries(bench_ecdh secp256k1)
    set_target_properties(bench_ecdh PROPERTIES FOLDER "secp256k1")
  endif()

  if (ENABLE_MODULE_SCHNORR)
    add_executable(bench_schnorr_verify src/bench_schnorr_verify.c)
    target_link_libraries(bench_schnorr_verify secp256k1)
    set_target_properties(bench_schnorr_verify PROPERTIES FOLDER "secp256k1")
  endif()

  if (ENABLE_MODULE_RECOVERY)
    add_executable(bench_recover src/bench_recover.c)
    target_link_libraries(bench_recover secp256k1)
    set_target_properties(bench_recover PROPERTIES FOLDER "secp256k1")
  endif()
endif()

# Tests
#==============================================================================
if (ENABLE_TESTS)
  add_executable(tests
    src/tests.c)

  target_compile_definitions(tests PRIVATE -DVERIFY)
  target_include_directories(tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR})

  target_link_libraries(tests secp256k1)

  enable_testing()
  add_test(
    NAME test
    COMMAND tests)

  set_target_properties(tests PROPERTIES FOLDER "secp256k1")
endif()

# Install
#==============================================================================
install(TARGETS secp256k1
  EXPORT secp256k1
  ARCHIVE DESTINATION lib)
install(FILES include/secp256k1.h DESTINATION include)

if (ENABLE_MODULE_ECDH)
  install(FILES include/secp256k1_ecdh.h DESTINATION include)
endif()

if (ENABLE_MODULE_SCHNORR)
  install(FILES include/secp256k1_schnorr.h DESTINATION include)
endif()

if (ENABLE_MODULE_RECOVERY)
  install(FILES include/secp256k1_recovery.h DESTINATION include)
endif()

# Export
#==============================================================================
include(CMakePackageConfigHelpers)

export(EXPORT secp256k1
  FILE "${CMAKE_CURRENT_BINARY_DIR}/secp256k1Targets.cmake")
export(PACKAGE secp256k1)

if (UNIX)
  set(_config_package_location "lib/cmake")
elseif (WIN32)
  set(_config_package_location "cmake")
endif()

install(EXPORT secp256k1
  FILE secp256k1Targets.cmake
  DESTINATION ${_config_package_location})

configure_file(secp256k1Config.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/secp256k1Config.cmake"
  @ONLY)

write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/secp256k1ConfigVersion.cmake"
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY AnyNewerVersion)

install(
  FILES
    "${CMAKE_CURRENT_BINARY_DIR}/secp256k1Config.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/secp256k1ConfigVersion.cmake"
  DESTINATION ${_config_package_location})
