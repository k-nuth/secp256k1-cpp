from conans import ConanFile, CMake
import os

class Secp256k1Conan(ConanFile):
    name = "secp256k1"
    version = "0.1"
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/bitprim/secp256k1"
    description = "Optimized C library for EC operations on curve secp256k1"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    build_policy = "missing"
    exports_sources = "src/*", "include/*", "CMakeLists.txt", "cmake/*", "secp256k1Config.cmake.in", "contrib/*", "test/*"

    def build_requirements(self):
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            self.build_requires("gmp/6.1.2@bitprim/stable")

    def build(self):
        cmake = CMake(self)
        if self.settings.os == "Windows":
            cmake.definitions["WITH_BIGNUM"]="no"
        else:
            cmake.definitions["WITH_BIGNUM"]="gmp"
        cmake.configure(source_dir=self.conanfile_directory, args=cmake_args)
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
        self.env_info.CPATH = os.path.join(self.package_folder, "include")
        self.env_info.C_INCLUDE_PATH = os.path.join(self.package_folder, "include")
        self.env_info.CPLUS_INCLUDE_PATH = os.path.join(self.package_folder, "include")
