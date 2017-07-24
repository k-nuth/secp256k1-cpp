from conans import ConanFile, CMake
from pprint import pprint
import os

channel = os.getenv("CONAN_CHANNEL", "stable")
username = os.getenv("CONAN_USERNAME", "dario-ramos")

class Secp256k1TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "secp256k1/0.1@%s/%s" % (username, channel)
    generators = "cmake"

    def build(self):
        pprint(vars(self))
        pprint(vars(self.settings))

        cmake = CMake(self)

        
        pprint(vars(cmake))

        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is in "test_package"
        cmake.configure(source_dir=self.conanfile_directory, build_dir="./")
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")

    def test(self):
        os.chdir("bin")
        self.run(".%sexample" % os.sep)
