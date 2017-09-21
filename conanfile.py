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

def option_on_off(option):
    return "ON" if option else "OFF"

class Secp256k1Conan(ConanFile):
    name = "secp256k1"
    version = "0.1"
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/bitprim/secp256k1"
    description = "Optimized C library for EC operations on curve secp256k1"
    
    settings = "os", "compiler", "build_type", "arch"

    # options = {"shared": [True, False]}
    # default_options = "shared=False"

    #TODO(fernando): See what to do with shared/static option... (not supported yet in Cmake)
    
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "enable_benchmark": [True, False],
               "enable_tests": [True, False],
               "enable_openssl_tests": [True, False],
               "enable_experimental": [True, False],
               "enable_endomorphism": [True, False],
               "enable_ecmult_static_precomputation": [True, False],
               "enable_module_ecdh": [True, False],
               "enable_module_schnorr": [True, False],
               "enable_module_recovery": [True, False],

            #    "with_asm": ['x86_64', 'arm', 'no', 'auto'],
            #    "with_field": ['64bit', '32bit', 'auto'],
            #    "with_scalar": ['64bit', '32bit', 'auto'],
            #    "with_bignum": ['gmp', 'no', 'auto'],
    }

    
    default_options = "shared=False", \
        "fPIC=True", \
        "enable_benchmark=False", \
        "enable_tests=True", \
        "enable_openssl_tests=False", \
        "enable_experimental=False", \
        "enable_endomorphism=False", \
        "enable_ecmult_static_precomputation=True", \
        "enable_module_ecdh=False", \
        "enable_module_schnorr=False", \
        "enable_module_recovery=True"

        # "with_asm='auto'", \
        # "with_field='auto'", \
        # "with_scalar='auto'"
        # "with_bignum='auto'"

    generators = "cmake"
    build_policy = "missing"
    exports_sources = "src/*", "include/*", "CMakeLists.txt", "cmake/*", "secp256k1Config.cmake.in", "contrib/*", "test/*"

    def requirements(self):
        # if self.settings.os == "Linux" or self.settings.os == "Macos":
        if self.settings.os != "Windows":
            self.requires("gmp/6.1.2@bitprim/stable")

    def build(self):
        cmake = CMake(self)

        cmake.definitions["USE_CONAN"] = "ON"
        cmake.definitions["NO_CONAN_AT_ALL"] = "OFF"
        cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = "ON"

        cmake.definitions["ENABLE_POSITION_INDEPENDENT_CODE"] = option_on_off(self.options.fPIC)
        cmake.definitions["ENABLE_BENCHMARK"] = option_on_off(self.options.enable_benchmark)
        cmake.definitions["ENABLE_TESTS"] = option_on_off(self.options.enable_tests)
        cmake.definitions["ENABLE_OPENSSL_TESTS"] = option_on_off(self.options.enable_openssl_tests)
        cmake.definitions["ENABLE_EXPERIMENTAL"] = option_on_off(self.options.enable_experimental)
        cmake.definitions["ENABLE_ENDOMORPHISM"] = option_on_off(self.options.enable_endomorphism)
        cmake.definitions["ENABLE_ECMULT_STATIC_PRECOMPUTATION"] = option_on_off(self.options.enable_ecmult_static_precomputation)
        cmake.definitions["ENABLE_MODULE_ECDH"] = option_on_off(self.options.enable_module_ecdh)
        cmake.definitions["ENABLE_MODULE_SCHNORR"] = option_on_off(self.options.enable_module_schnorr)
        cmake.definitions["ENABLE_MODULE_RECOVERY"] = option_on_off(self.options.enable_module_recovery)

        if self.settings.os == "Windows":
            cmake.definitions["WITH_BIGNUM"] = "no"
            if self.settings.compiler == "Visual Studio" and (self.settings.compiler.version != 12):
                cmake.definitions["ENABLE_TESTS"] = "OFF"   #Workaround. test broke MSVC
        else:
            cmake.definitions["WITH_BIGNUM"] = "gmp"

        # cmake.definitions["WITH_ASM"] = option_on_off(self.options.with_asm)
        # cmake.definitions["WITH_FIELD"] = option_on_off(self.options.with_field)
        # cmake.definitions["WITH_SCALAR"] = option_on_off(self.options.with_scalar)
        # cmake.definitions["WITH_BIGNUM"] = option_on_off(self.options.with_bignum)


        cmake.configure(source_dir=self.conanfile_directory)
        cmake.build()

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
