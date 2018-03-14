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


def option_on_off(option):
    return "ON" if option else "OFF"

# def make_default_options_method():
#     defs = "shared=False", \
#         "fPIC=True", \
#         "with_benchmark=False", \
#         "with_tests=True", \
#         "with_openssl_tests=False", \
#         "enable_experimental=False", \
#         "enable_endomorphism=False", \
#         "enable_ecmult_static_precomputation=True", \
#         "enable_module_ecdh=False", \
#         "enable_module_schnorr=False", \
#         "enable_module_recovery=True", \
#         "with_bignum=conan"

#         # "with_asm='auto'", \
#         # "with_field='auto'", \
#         # "with_scalar='auto'"
#         # "with_bignum='auto'"


#     if cpuid_installed:
#         gmp_opt = "gmp:microarchitecture=%s" % (''.join(cpuid.cpu_microarchitecture()))
#         new_defs = defs + (gmp_opt,)
#         return new_defs

#     return defs
    
def get_content(file_name):
    # print(os.path.dirname(os.path.abspath(__file__)))
    # print(os.getcwd())
    # with open(path, 'r') as f:
    #     return f.read()
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    with open(file_path, 'r') as f:
        return f.read()

def get_version():
    return get_content('conan_version')

def get_channel():
    return get_content('conan_channel')

def get_conan_req_version():
    return get_content('conan_req_version')

class Secp256k1Conan(ConanFile):
    name = "secp256k1"
    version = get_version()
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/bitprim/secp256k1"
    description = "Optimized C library for EC operations on curve secp256k1"
    settings = "os", "compiler", "build_type", "arch"

    if conan_version < Version(get_conan_req_version()):
        raise Exception ("Conan version should be greater or equal than %s" % (get_conan_req_version(), ))


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

               
            #    "with_bignum": ["conan", "auto", "system", "no"]

            #TODO(fernando): check what to do with with_asm, with_field and with_scalar 
            # Check CMake files and libbitcoin and bitcoin core makefiles

            #    "with_asm": ['x86_64', 'arm', 'no', 'auto'],
            #    "with_field": ['64bit', '32bit', 'auto'],
            #    "with_scalar": ['64bit', '32bit', 'auto'],
            #    "with_bignum": ['gmp', 'no', 'auto'],
    }

    
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
        "with_bignum_lib=True"

        

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

    def package_id(self):
        self.info.options.with_benchmark = "ANY"
        self.info.options.with_tests = "ANY"
        self.info.options.with_openssl_tests = "ANY"

    def build(self):
        cmake = CMake(self)

        cmake.definitions["USE_CONAN"] = option_on_off(True)
        cmake.definitions["NO_CONAN_AT_ALL"] = option_on_off(False)
        # cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = option_on_off(False)
        cmake.verbose = False

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
