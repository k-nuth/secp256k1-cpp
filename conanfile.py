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

import os
# import sys
from conans import ConanFile, CMake
from conans import __version__ as conan_version
from conans.model.version import Version
from ci_utils import option_on_off, get_version, get_conan_req_version, march_conan_manip, pass_march_to_compiler

class Secp256k1Conan(ConanFile):
    name = "secp256k1"
    
    version = get_version()
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/bitprim/secp256k1"
    description = "Optimized C library for EC operations on curve secp256k1"
    settings = "os", "compiler", "build_type", "arch"

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
               "fix_march": [True, False],
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
        "fix_march=False", \
        "verbose=True"

        # "with_bignum=conan"
        # "with_asm='auto'", \
        # "with_field='auto'", \
        # "with_scalar='auto'"
        # "with_bignum='auto'"

    generators = "cmake"
    exports = "conan_*", "ci_utils/*"
    exports_sources = "src/*", "include/*", "CMakeLists.txt", "cmake/*", "secp256k1Config.cmake.in", "contrib/*", "test/*"
    build_policy = "missing"

    # with_benchmark = False
    # with_tests = True
    # with_openssl_tests = False

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
        if self.settings.arch != "x86_64":
            self.output.info("microarchitecture is disabled for architectures other than x86_64, your architecture: %s" % (self.settings.arch,))
            self.options.remove("microarchitecture")
            self.options.remove("fix_march")

        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")
            if self.options.shared and self.msvc_mt_build:
                self.options.remove("shared")

    def configure(self):
        del self.settings.compiler.libcxx       #Pure-C Library

        if self.settings.arch == "x86_64" and self.options.microarchitecture == "_DUMMY_":
            del self.options.fix_march
            # self.options.remove("fix_march")
            # raise Exception ("fix_march option is for using together with microarchitecture option.")

        if self.settings.arch == "x86_64":
            march_conan_manip(self)
            self.options["*"].microarchitecture = self.options.microarchitecture

    def package_id(self):
        self.info.options.with_benchmark = "ANY"
        self.info.options.with_tests = "ANY"
        self.info.options.with_openssl_tests = "ANY"
        self.info.options.verbose = "ANY"
        self.info.options.fix_march = "ANY"

        # if self.settings.compiler == "Visual Studio":
        #     self.info.options.microarchitecture = "ANY"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["USE_CONAN"] = option_on_off(True)
        cmake.definitions["NO_CONAN_AT_ALL"] = option_on_off(False)
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

        # cmake.definitions["WITH_ASM"] = option_on_off(self.options.with_asm)
        # cmake.definitions["WITH_FIELD"] = option_on_off(self.options.with_field)
        # cmake.definitions["WITH_SCALAR"] = option_on_off(self.options.with_scalar)
        # cmake.definitions["WITH_BIGNUM"] = option_on_off(self.options.with_bignum)


        cmake.definitions["MICROARCHITECTURE"] = self.options.microarchitecture
        cmake.definitions["BITPRIM_PROJECT_VERSION"] = self.version

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



        pass_march_to_compiler(self, cmake)

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
