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
        #print "TP-SELF\n"
        #pprint(vars(self))
        #print "TP-SELF.SETTINGS\n"
        #pprint(vars(self.settings))
        #print "TP-SELF.SETTINGS.COMPILER.VERSION\n"
        #pprint(vars(self.settings.compiler.version))
        print("TP\n")
        pprint(vars(self.settings.arch))

        os.environ["CC"] = "gcc-" + str(self.settings.compiler.version)
        os.environ["CXX"] = "gcc-" + str(self.settings.compiler.version)
        os.environ["CFLAGS"] = "-m32"
        cmake = CMake(self)

        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is in "test_package"
        cmake.configure(source_dir=self.conanfile_directory, build_dir="./")
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")

    def test(self):
        os.chdir("bin")
        self.run(".%sexample" % os.sep)
