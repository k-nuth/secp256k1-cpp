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

import os
from conans import ConanFile, CMake
from conans import __version__ as conan_version
from conans.model.version import Version
import importlib


# import cpuid
cpuid_installed = False
import importlib
try:
    cpuid = importlib.import_module('cpuid')
    cpuid_installed = True
except ImportError:
    # print("*** cpuid could not be imported")
    cpuid_installed = False

def option_on_off(option):
    return "ON" if option else "OFF"
    
def get_content(file_name):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    with open(file_path, 'r') as f:
        return f.read()

def get_version():
    return get_content('conan_version')

def get_channel():
    return get_content('conan_channel')

def get_conan_req_version():
    return get_content('conan_req_version')

microarchitecture_default = 'x86_64'

def get_cpuid():
    try:
        # print("*** cpuid OK")
        cpuid = importlib.import_module('cpuid')
        return cpuid
    except ImportError:
        # print("*** cpuid could not be imported")
        return None

def get_cpu_microarchitecture_or_default(default):
    cpuid = get_cpuid()
    if cpuid != None:
        # return '%s%s' % cpuid.cpu_microarchitecture()
        return '%s' % (''.join(cpuid.cpu_microarchitecture()))
    else:
        return default

def get_cpu_microarchitecture():
    return get_cpu_microarchitecture_or_default(microarchitecture_default)


class Secp256k1Conan(ConanFile):
    name = "secp256k1"
    version = get_version()
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/bitprim/secp256k1"
    description = "Optimized C library for EC operations on curve secp256k1"
    settings = "os", "compiler", "build_type", "arch"
    # settings = "os", "compiler", "build_type", "arch", "os_build", "arch_build"

    if Version(conan_version) < Version(get_conan_req_version()):
        raise Exception ("Conan version should be greater or equal than %s. Detected: %s." % (get_conan_req_version(), conan_version))


    #TODO(fernando): See what to do with shared/static option... (not supported yet in Cmake)
    
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "enable_experimental": [True, False],
               "enable_endomorphism": [True, False],
               "enable_ecmult_static_precomputation": [True, False],
               "enable_module_ecdh": [True, False],
               "enable_module_schnorr": [True, False],
               "enable_module_recovery": [True, False],
               "with_benchmark": [True, False],
               "with_tests": [True, False],
               "with_openssl_tests": [True, False],
               "with_bignum_lib": [True, False],
               "microarchitecture": "ANY", #["x86_64", "haswell", "ivybridge", "sandybridge", "bulldozer", ...]
               "verbose": [True, False],

               
            #    "with_bignum": ["conan", "auto", "system", "no"]

            #TODO(fernando): check what to do with with_asm, with_field and with_scalar 
            # Check CMake files and libbitcoin and bitcoin core makefiles

            #    "with_asm": ['x86_64', 'arm', 'no', 'auto'],
            #    "with_field": ['64bit', '32bit', 'auto'],
            #    "with_scalar": ['64bit', '32bit', 'auto'],
            #    "with_bignum": ['gmp', 'no', 'auto'],
    }

    # default_options = make_default_options_method()
    default_options = "shared=False", \
        "fPIC=True", \
        "enable_experimental=False", \
        "enable_endomorphism=False", \
        "enable_ecmult_static_precomputation=False", \
        "enable_module_ecdh=False", \
        "enable_module_schnorr=False", \
        "enable_module_recovery=True", \
        "with_benchmark=False", \
        "with_tests=False", \
        "with_openssl_tests=False", \
        "with_bignum_lib=True", \
        "microarchitecture=_DUMMY_",  \
        "verbose=True"

        # "with_bignum=conan"
        # "with_asm='auto'", \
        # "with_field='auto'", \
        # "with_scalar='auto'"
        # "with_bignum='auto'"

    generators = "cmake"
    build_policy = "missing"

    exports = "conan_channel", "conan_version", "conan_req_version"
    exports_sources = "src/*", "include/*", "CMakeLists.txt", "cmake/*", "secp256k1Config.cmake.in", "bitprimbuildinfo.cmake", "contrib/*", "test/*"


    # with_benchmark = False
    # with_tests = True
    # with_openssl_tests = False





    # https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html
    # echo "" | gcc -fsyntax-only -march=pepe -xc -
    # nocona core2 nehalem corei7 westmere sandybridge corei7-avx ivybridge core-avx-i haswell core-avx2 broadwell skylake skylake-avx512 bonnell atom silvermont slm knl x86-64 eden-x2 nano nano-1000 nano-2000 nano-3000 nano-x2 eden-x4 nano-x4 k8 k8-sse3 opteron opteron-sse3 athlon64 athlon64-sse3 athlon-fx amdfam10 barcelona bdver1 bdver2 bdver3 bdver4 znver1 btver1 btver2
    # marchs = ["x86_64", "nehalem", "sandybridge", "haswell", "skylake", "skylake-avx512"]

    # x86-64
    # A generic CPU with 64-bit extensions.

    # core2
    # Intel Core 2 CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3

    # nehalem
    # Intel Nehalem CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT

    # westmere
    # Intel Westmere CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL

    # sandybridge
    # Intel Sandy Bridge CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AES, PCLMUL

    # ivybridge
    # Intel Ivy Bridge CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AES, PCLMUL, FSGSBASE, RDRND, F16C

    # haswell
    # Intel Haswell CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C

    # broadwell
    # Intel Broadwell CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW

    # skylake
    # Intel Skylake CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, CLFLUSHOPT, XSAVEC, XSAVES

    # bonnell
    # Intel Bonnell CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3

    # silvermont
    # Intel Silvermont CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL, RDRND

    # knl
    # Intel Knights Landing CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, AVX512F, AVX512PF, AVX512ER, AVX512CD

    # knm
    # Intel Knights Mill CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, AVX512F, AVX512PF, AVX512ER, AVX512CD, AVX5124VNNIW, AVX5124FMAPS, AVX512VPOPCNTDQ

    # skylake-avx512
    # Intel Skylake Server CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, PKU, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, CLFLUSHOPT, XSAVEC, XSAVES, AVX512F, CLWB, AVX512VL, AVX512BW, AVX512DQ, AVX512CD

    # cannonlake
    # Intel Cannonlake Server CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, PKU, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, CLFLUSHOPT, XSAVEC, XSAVES, AVX512F, AVX512VL, AVX512BW, AVX512DQ, AVX512CD, AVX512VBMI, AVX512IFMA, SHA, UMIP

    # icelake-client
    # zIntel Icelake Client CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, PKU, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, CLFLUSHOPT, XSAVEC, XSAVES, AVX512F, AVX512VL, AVX512BW, AVX512DQ, AVX512CD, AVX512VBMI, AVX512IFMA, SHA, CLWB, UMIP, RDPID, GFNI, AVX512VBMI2, AVX512VPOPCNTDQ, AVX512BITALG, AVX512VNNI, VPCLMULQDQ, VAES

    # icelake-server
    # Intel Icelake Server CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, PKU, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, CLFLUSHOPT, XSAVEC, XSAVES, AVX512F, AVX512VL, AVX512BW, AVX512DQ, AVX512CD, AVX512VBMI, AVX512IFMA, SHA, CLWB, UMIP, RDPID, GFNI, AVX512VBMI2, AVX512VPOPCNTDQ, AVX512BITALG, AVX512VNNI, VPCLMULQDQ, VAES, PCONFIG, WBNOINVD


    # -----------------------------------


    # k8
    # opteron
    # athlon64
    # athlon-fx
    # Processors based on the AMD K8 core with x86-64 instruction set support, including the AMD Opteron, Athlon 64, and Athlon 64 FX processors. (This supersets MMX, SSE, SSE2, 3DNow!, enhanced 3DNow! and 64-bit instruction set extensions.)

    # k8-sse3
    # opteron-sse3
    # athlon64-sse3
    # Improved versions of AMD K8 cores with SSE3 instruction set support.

    # amdfam10
    # barcelona
    # CPUs based on AMD Family 10h cores with x86-64 instruction set support. (This supersets MMX, SSE, SSE2, SSE3, SSE4A, 3DNow!, enhanced 3DNow!, ABM and 64-bit instruction set extensions.)

    # bdver1
    # CPUs based on AMD Family 15h cores with x86-64 instruction set support. (This supersets FMA4, AVX, XOP, LWP, AES, PCL_MUL, CX16, MMX, SSE, SSE2, SSE3, SSE4A, SSSE3, SSE4.1, SSE4.2, ABM and 64-bit instruction set extensions.)

    # bdver2
    # AMD Family 15h core based CPUs with x86-64 instruction set support. (This supersets BMI, TBM, F16C, FMA, FMA4, AVX, XOP, LWP, AES, PCL_MUL, CX16, MMX, SSE, SSE2, SSE3, SSE4A, SSSE3, SSE4.1, SSE4.2, ABM and 64-bit instruction set extensions.)

    # bdver3
    # AMD Family 15h core based CPUs with x86-64 instruction set support. (This supersets BMI, TBM, F16C, FMA, FMA4, FSGSBASE, AVX, XOP, LWP, AES, PCL_MUL, CX16, MMX, SSE, SSE2, SSE3, SSE4A, SSSE3, SSE4.1, SSE4.2, ABM and 64-bit instruction set extensions.

    # bdver4
    # AMD Family 15h core based CPUs with x86-64 instruction set support. (This supersets BMI, BMI2, TBM, F16C, FMA, FMA4, FSGSBASE, AVX, AVX2, XOP, LWP, AES, PCL_MUL, CX16, MOVBE, MMX, SSE, SSE2, SSE3, SSE4A, SSSE3, SSE4.1, SSE4.2, ABM and 64-bit instruction set extensions.

    # znver1
    # AMD Family 17h core based CPUs with x86-64 instruction set support. (This supersets BMI, BMI2, F16C, FMA, FSGSBASE, AVX, AVX2, ADCX, RDSEED, MWAITX, SHA, CLZERO, AES, PCL_MUL, CX16, MOVBE, MMX, SSE, SSE2, SSE3, SSE4A, SSSE3, SSE4.1, SSE4.2, ABM, XSAVEC, XSAVES, CLFLUSHOPT, POPCNT, and 64-bit instruction set extensions.

    # btver1
    # CPUs based on AMD Family 14h cores with x86-64 instruction set support. (This supersets MMX, SSE, SSE2, SSE3, SSSE3, SSE4A, CX16, ABM and 64-bit instruction set extensions.)

    # btver2
    # CPUs based on AMD Family 16h cores with x86-64 instruction set support. This includes MOVBE, F16C, BMI, AVX, PCL_MUL, AES, SSE4.2, SSE4.1, CX16, ABM, SSE4A, SSSE3, SSE3, SSE2, SSE, MMX and 64-bit instruction set extensions.




    @property
    def msvc_mt_build(self):
        return "MT" in str(self.settings.compiler.runtime)

    @property
    def fPIC_enabled(self):
        if self.settings.compiler == "Visual Studio":
            return False
        else:
            return self.options.fPIC

    @property
    def is_shared(self):
        if self.options.shared and self.msvc_mt_build:
            return False
        else:
            return self.options.shared

    @property
    def bignum_lib_name(self):
        if self.options.with_bignum_lib:
            if self.settings.os == "Windows":
                return "mpir"
            else:
                return "gmp"
        else:
            return "no"

    # def fix_march(self, march):
        # marchs = ["x86_64", ''.join(cpuid.cpu_microarchitecture()), "haswell", "skylake", "skylake-avx512"]
        

    def requirements(self):
        if self.options.with_bignum_lib:
            if self.settings.os == "Windows":
                self.requires("mpir/3.0.0@bitprim/stable")
            else:
                self.requires("gmp/6.1.2@bitprim/stable")

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")
            if self.options.shared and self.msvc_mt_build:
                self.options.remove("shared")

    def configure(self):
        del self.settings.compiler.libcxx       #Pure-C Library

        if self.options.microarchitecture == "_DUMMY_":
            self.options.microarchitecture = get_cpu_microarchitecture()
            if get_cpuid() == None:
                march_from = 'default'
            else:
                march_from = 'taken from cpuid'
        else:
            march_from = 'user defined'

        # Temporary fix for GCC march. 
        # TODO(fernando): Do it better!

        # self.output.info("********* CLANG Version: %s" % (str(self.settings.compiler.version)))
        # if self.settings.compiler == "clang":
        #     self.output.info("********* CLANG Version: %s" % (str(self.settings.compiler.version)))
        # if self.settings.compiler == "apple-clang":
        #     self.output.info("********* APPLE-CLANG Version: %s" % (str(self.settings.compiler.version)))

        # MinGW
        if self.options.microarchitecture == 'skylake-avx512' and self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self.output.info("'skylake-avx512' microarchitecture is not supported by this compiler, fall back to 'skylake'")
            self.options.microarchitecture = 'skylake'

        # if self.options.microarchitecture == 'skylake' and self.settings.os == "Windows" and self.settings.compiler == "gcc":
        #     self.output.info("'skylake' microarchitecture is not supported by this compiler, fall back to 'haswell'")
        #     self.options.microarchitecture = 'haswell'

        if self.options.microarchitecture == 'skylake-avx512' and self.settings.compiler == "apple-clang" and float(str(self.settings.compiler.version)) < 8:
            self.output.info("'skylake-avx512' microarchitecture is not supported by this compiler, fall back to 'skylake'")
            self.options.microarchitecture = 'skylake'

        if self.options.microarchitecture == 'skylake' and self.settings.compiler == "apple-clang" and float(str(self.settings.compiler.version)) < 8:
            self.output.info("'skylake' microarchitecture is not supported by this compiler, fall back to 'haswell'")
            self.options.microarchitecture = 'haswell'

        if self.options.microarchitecture == 'skylake-avx512' and self.settings.compiler == "gcc" and float(str(self.settings.compiler.version)) < 6:
            self.output.info("'skylake-avx512' microarchitecture is not supported by this compiler, fall back to 'skylake'")
            self.options.microarchitecture = 'skylake'

        if self.options.microarchitecture == 'skylake' and self.settings.compiler == "gcc" and float(str(self.settings.compiler.version)) < 6:
            self.output.info("'skylake' microarchitecture is not supported by this compiler, fall back to 'haswell'")
            self.options.microarchitecture = 'haswell'

        # if self.options.microarchitecture == 'skylake-avx512' and self.settings.compiler == "gcc" and float(str(self.settings.compiler.version)) < 5:
        #     self.options.microarchitecture = 'haswell'

        self.options["*"].microarchitecture = self.options.microarchitecture
        self.output.info("Compiling for microarchitecture (%s): %s" % (march_from, self.options.microarchitecture))
        

    def package_id(self):
        self.info.options.with_benchmark = "ANY"
        self.info.options.with_tests = "ANY"
        self.info.options.with_openssl_tests = "ANY"
        self.info.options.verbose = "ANY"

        # if self.settings.compiler == "Visual Studio":
        #     self.info.options.microarchitecture = "ANY"

    def build(self):
        cmake = CMake(self)

        cmake.definitions["USE_CONAN"] = option_on_off(True)
        cmake.definitions["NO_CONAN_AT_ALL"] = option_on_off(False)
        # cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = option_on_off(False)
        cmake.verbose = self.options.verbose

        cmake.definitions["ENABLE_SHARED"] = option_on_off(self.is_shared)
        cmake.definitions["ENABLE_POSITION_INDEPENDENT_CODE"] = option_on_off(self.fPIC_enabled)

        cmake.definitions["ENABLE_BENCHMARK"] = option_on_off(self.options.with_benchmark)
        cmake.definitions["ENABLE_TESTS"] = option_on_off(self.options.with_tests)
        cmake.definitions["ENABLE_OPENSSL_TESTS"] = option_on_off(self.options.with_openssl_tests)
        # cmake.definitions["ENABLE_BENCHMARK"] = option_on_off(self.with_benchmark)
        # cmake.definitions["ENABLE_TESTS"] = option_on_off(self.with_tests)
        # cmake.definitions["ENABLE_OPENSSL_TESTS"] = option_on_off(self.with_openssl_tests)

        cmake.definitions["ENABLE_EXPERIMENTAL"] = option_on_off(self.options.enable_experimental)
        cmake.definitions["ENABLE_ENDOMORPHISM"] = option_on_off(self.options.enable_endomorphism)
        cmake.definitions["ENABLE_ECMULT_STATIC_PRECOMPUTATION"] = option_on_off(self.options.enable_ecmult_static_precomputation)
        cmake.definitions["ENABLE_MODULE_ECDH"] = option_on_off(self.options.enable_module_ecdh)
        cmake.definitions["ENABLE_MODULE_SCHNORR"] = option_on_off(self.options.enable_module_schnorr)
        cmake.definitions["ENABLE_MODULE_RECOVERY"] = option_on_off(self.options.enable_module_recovery)

        # if self.settings.os == "Windows":
        #     cmake.definitions["WITH_BIGNUM"] = "mpir"
        # else:
        #     cmake.definitions["WITH_BIGNUM"] = "gmp"

        cmake.definitions["WITH_BIGNUM"] = self.bignum_lib_name

        cmake.definitions["MICROARCHITECTURE"] = self.options.microarchitecture

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio" and (self.settings.compiler.version != 12):
                cmake.definitions["ENABLE_TESTS"] = option_on_off(False)   #Workaround. test broke MSVC

        # Pure-C Library, No CXX11 ABI
        # if self.settings.compiler == "gcc":
        #     if float(str(self.settings.compiler.version)) >= 5:
        #         cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(False)
        #     else:
        #         cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(True)
        # elif self.settings.compiler == "clang":
        #     if str(self.settings.compiler.libcxx) == "libstdc++" or str(self.settings.compiler.libcxx) == "libstdc++11":
        #         cmake.definitions["NOT_USE_CPP11_ABI"] = option_on_off(False)




        # cmake.definitions["WITH_ASM"] = option_on_off(self.options.with_asm)
        # cmake.definitions["WITH_FIELD"] = option_on_off(self.options.with_field)
        # cmake.definitions["WITH_SCALAR"] = option_on_off(self.options.with_scalar)
        # cmake.definitions["WITH_BIGNUM"] = option_on_off(self.options.with_bignum)

        if self.settings.compiler != "Visual Studio":
            gcc_march = str(self.options.microarchitecture).replace('_', '-')
            cmake.definitions["CONAN_CXX_FLAGS"] = cmake.definitions.get("CONAN_CXX_FLAGS", "") + " -march=" + gcc_march
            cmake.definitions["CONAN_C_FLAGS"] = cmake.definitions.get("CONAN_C_FLAGS", "") + " -march=" + gcc_march

        # microarchitecture_default

        cmake.definitions["BITPRIM_BUILD_NUMBER"] = os.getenv('BITPRIM_BUILD_NUMBER', '-')
        cmake.configure(source_dir=self.source_folder)
        cmake.build()


        #TODO(fernando): Cmake Tests and Visual Studio doesn't work
        #TODO(fernando): Secp256k1 segfaults al least on Windows
        # if self.options.with_tests:
        #     cmake.test()
        #     # cmake.test(target="tests")

    def package(self):
        self.copy("*.h", dst="include", src="include", keep_path=True)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["secp256k1"]
        if self.package_folder:
            self.env_info.CPATH = os.path.join(self.package_folder, "include")
            self.env_info.C_INCLUDE_PATH = os.path.join(self.package_folder, "include")
            self.env_info.CPLUS_INCLUDE_PATH = os.path.join(self.package_folder, "include")
