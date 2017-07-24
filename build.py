import os
from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(username="dario-ramos", channel="stable")
    builder.password = os.getenv("CONAN_PASSWORD")
    builder.add_common_builds()
    builder.run()
