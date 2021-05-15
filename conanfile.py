# Copyright (c) 2016-2021 Knuth Project developers.
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
from conans import CMake
from kthbuild import option_on_off, march_conan_manip, pass_march_to_compiler
from kthbuild import KnuthConanFile

class Secp256k1Conan(KnuthConanFile):
    def recipe_dir(self):
        return os.path.dirname(os.path.abspath(__file__))

    name = "secp256k1"
    # version = get_version()
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/k-nuth/secp256k1"
    description = "Optimized C library for EC operations on curve secp256k1"
    settings = "os", "compiler", "build_type", "arch"


    #TODO(fernando): See what to do with shared/static option... (not supported yet in Cmake)

    options = {"shared": [True, False],
               "fPIC": [True, False],
               "enable_experimental": [True, False],
               "enable_endomorphism": [True, False],
               "enable_ecmult_static_precomputation": [True, False],
               "enable_module_ecdh": [True, False],
               "enable_module_schnorr": [True, False],
               "enable_module_recovery": [True, False],
               "enable_module_multiset": [True, False],
               "benchmark": [True, False],
               "tests": [True, False],
               "openssl_tests": [True, False],
               "bignum_lib": [True, False],
               "microarchitecture": "ANY", #["x86_64", "haswell", "ivybridge", "sandybridge", "bulldozer", ...]
               "fix_march": [True, False],
               "march_id": "ANY",
               "verbose": [True, False],
               "cxxflags": "ANY",
               "cflags": "ANY",
               "cmake_export_compile_commands": [True, False],



            #    "with_bignum": ["conan", "auto", "system", "no"]

            #TODO(fernando): check what to do with with_asm, with_field and with_scalar
            # Check CMake files and Legacy and bitcoin core makefiles

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
        "enable_module_schnorr=True", \
        "enable_module_recovery=True", \
        "enable_module_multiset=True", \
        "benchmark=False", \
        "tests=False", \
        "openssl_tests=False", \
        "bignum_lib=True", \
        "microarchitecture=_DUMMY_",  \
        "fix_march=False", \
        "march_id=_DUMMY_",  \
        "verbose=False",  \
        "cxxflags=_DUMMY_", \
        "cflags=_DUMMY_", \
        "cmake_export_compile_commands=False"

        # "with_bignum=conan"
        # "with_asm='auto'", \
        # "with_field='auto'", \
        # "with_scalar='auto'"
        # "with_bignum='auto'"

    generators = "cmake"
    exports = "conan_*", "ci_utils/*"
    exports_sources = "src/*", "include/*", "CMakeLists.txt", "cmake/*", "secp256k1Config.cmake.in", "contrib/*", "test/*"
    build_policy = "missing"

    @property
    def bignum_lib_name(self):
        if self.options.bignum_lib:
            if self.settings.os == "Windows":
                return "mpir"
            else:
                return "gmp"
        else:
            return "no"

    def requirements(self):
        if self.options.bignum_lib:
            if self.settings.os == "Windows":
                self.requires("mpir/3.0.0")
            else:
                self.requires("gmp/6.2.1")

    def config_options(self):
        KnuthConanFile.config_options(self)

        # if self.settings.arch != "x86_64":
        #     self.output.info("microarchitecture is disabled for architectures other than x86_64, your architecture: %s" % (self.settings.arch,))
        #     self.options.remove("microarchitecture")
        #     self.options.remove("fix_march")

        # if self.settings.compiler == "Visual Studio":
        #     self.options.remove("fPIC")
        #     if self.options.shared and self.msvc_mt_build:
        #         self.options.remove("shared")

    def configure(self):
        # del self.settings.compiler.libcxx       #Pure-C Library
        KnuthConanFile.configure(self, pure_c=False)

        # if self.settings.arch == "x86_64" and self.options.microarchitecture == "_DUMMY_":
        #     del self.options.fix_march
        #     # self.options.remove("fix_march")
        #     # raise Exception ("fix_march option is for using together with microarchitecture option.")

        # if self.settings.arch == "x86_64":
        #     march_conan_manip(self)
        #     self.options["*"].microarchitecture = self.options.microarchitecture

    def package_id(self):
        KnuthConanFile.package_id(self)

        self.info.options.benchmark = "ANY"
        self.info.options.openssl_tests = "ANY"


    def build(self):
        cmake = self.cmake_basis(pure_c=True)
        cmake.definitions["ENABLE_BENCHMARK"] = option_on_off(self.options.benchmark)
        cmake.definitions["ENABLE_TESTS"] = option_on_off(self.options.tests)
        cmake.definitions["ENABLE_OPENSSL_TESTS"] = option_on_off(self.options.openssl_tests)
        # cmake.definitions["ENABLE_BENCHMARK"] = option_on_off(self.benchmark)
        # cmake.definitions["ENABLE_TESTS"] = option_on_off(self.tests)
        # cmake.definitions["ENABLE_OPENSSL_TESTS"] = option_on_off(self.openssl_tests)
        cmake.definitions["ENABLE_EXPERIMENTAL"] = option_on_off(self.options.enable_experimental)
        cmake.definitions["ENABLE_ENDOMORPHISM"] = option_on_off(self.options.enable_endomorphism)
        cmake.definitions["ENABLE_ECMULT_STATIC_PRECOMPUTATION"] = option_on_off(self.options.enable_ecmult_static_precomputation)
        cmake.definitions["ENABLE_MODULE_ECDH"] = option_on_off(self.options.enable_module_ecdh)
        cmake.definitions["ENABLE_MODULE_SCHNORR"] = option_on_off(self.options.enable_module_schnorr)
        cmake.definitions["ENABLE_MODULE_RECOVERY"] = option_on_off(self.options.enable_module_recovery)
        cmake.definitions["ENABLE_MODULE_MULTISET"] = option_on_off(self.options.enable_module_multiset)

        self.output.info("Bignum lib selected: %s" % (self.bignum_lib_name,))
        cmake.definitions["WITH_BIGNUM"] = self.bignum_lib_name
        # cmake.definitions["WITH_ASM"] = option_on_off(self.options.with_asm)
        # cmake.definitions["WITH_FIELD"] = option_on_off(self.options.with_field)
        # cmake.definitions["WITH_SCALAR"] = option_on_off(self.options.with_scalar)
        # cmake.definitions["WITH_BIGNUM"] = option_on_off(self.options.with_bignum)

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio" and (self.settings.compiler.version != 12):
                cmake.definitions["ENABLE_TESTS"] = option_on_off(False)   #Workaround. test broke MSVC

        cmake.configure(source_dir=self.source_folder)
        cmake.build()

        #TODO(fernando): Cmake Tests and Visual Studio doesn't work
        #TODO(fernando): Secp256k1 segfaults al least on Windows
        # if self.options.tests:
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
