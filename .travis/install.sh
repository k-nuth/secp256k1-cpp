#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    brew update || brew update
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv
    brew install cmake || true

    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi

    pyenv install 3.6.1
    pyenv virtualenv 3.6.1 conan
    pyenv rehash
    pyenv activate conan
fi

############################################################################
# Install Guava
############################################################################
if [ ! -f $GUAVA_JAR ]; then wget $GUAVA_URL -O $GUAVA_JAR; fi
############################################################################
# All the dependencies are installed in /home/travis/deps/
############################################################################
DEPS_DIR="/home/travis/deps"
mkdir ${DEPS_DIR} && cd ${DEPS_DIR}
############################################################################
# Install a recent CMake
############################################################################
CMAKE_URL="https://cmake.org/files/v3.9/cmake-3.9.0-rc5-Linux-x86_64.tar.gz"
mkdir cmake && travis_retry wget --no-check-certificate --quiet -O - ${CMAKE_URL} | tar --strip-components=1 -xz -C cmake
echo 'Cmake 3.9.0 installed';
export PATH=${DEPS_DIR}/cmake/bin:${PATH}


pip install conan --upgrade
pip install conan_package_tools

conan remote add upload_repo "https://api.bintray.com/conan/bitprim/secp256k1"
conan user
