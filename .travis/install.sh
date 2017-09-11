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

    pyenv install 2.7.10
    pyenv virtualenv 2.7.10 conan
    pyenv rehash
    pyenv activate conan

    pip install conan --upgrade
    pip install conan_package_tools

else
    sudo -E pip install conan --upgrade
    # pip install conan==0.25.0
    sudo -E pip install conan_package_tools
fi

conan user
