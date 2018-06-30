#  >> sudo -E docker run -e CONAN_GCC_VERSIONS="7" -e CONAN_DOCKER_IMAGE="lasote/conangcc7" -e CONAN_LOGIN_USERNAME="[secure]" -e CONAN_PASSWORD="[secure]" -e CONAN_CHANNEL="feature_ci_test_travis_stages" -e CONAN_REMOTES="https://api.bintray.com/conan/bitprim/bitprim@True@remote0" -e CONAN_REFERENCE="secp256k1/0.4.0@bitprim/feature_ci_test_travis_stages" -e CPT_PROFILE="@@include(default)@@@@[settings]@@arch=x86_64@@build_type=Release@@compiler=gcc@@compiler.version=7@@[options]@@secp256k1:shared=False@@secp256k1:with_tests=True@@secp256k1:microarchitecture=x86_64@@[env]@@BITPRIM_BUILD_NUMBER=------------------------------------------------------@@None@@None@@None@@describe@@v0.3.0-112-g54f9eda@@0.4.0@@------------------------------------------------------@@0.4.0@@BITPRIM_BRANCH=feature_ci_test_travis_stages@@BITPRIM_CONAN_CHANNEL=feature_ci_test_travis_stages@@BITPRIM_FULL_BUILD=0@@[build_requires]@@@@" -e CONAN_USERNAME="bitprim" -e CONAN_TEMP_TEST_FOLDER="1" -e PIP_DISABLE_PIP_VERSION_CHECK="1" --name conan_runner  lasote/conangcc7 /bin/sh -c "sudo -E pip install conan_package_tools==0.18.2 --upgrade --no-cache && sudo -E pip install conan==1.5.0 --no-cache"


# BITPRIM_BUILD_NUMBER=------------------------------------------------------@@None@@None@@None@@describe@@v0.3.0-112-g54f9eda@@0.4.0@@------------------------------------------------------@@0.4.0@@BITPRIM_BRANCH=feature_ci_test_travis_stages@@BITPRIM_CONAN_CHANNEL=feature_ci_test_travis_stages@@BITPRIM_FULL_BUILD=0@@[build_requires]@@@@" -e CONAN_USERNAME="bitprim" -e CONAN_TEMP_TEST_FOLDER="1" -e PIP_DISABLE_PIP_VERSION_CHECK="1" --name conan_runner  lasote/conangcc7 /bin/sh -c "sudo -E pip install conan_package_tools==0.18.2 --upgrade --no-cache && sudo -E pip install conan==1.5.0 --no-cache"

import os
import cpuid
from ci_utils.utils import get_builder, handle_microarchs, copy_env_vars

if __name__ == "__main__":

    # full_build_str = os.getenv('BITPRIM_FULL_BUILD', '0')
    full_build = os.getenv('BITPRIM_FULL_BUILD', '0') == '1'

    builder, name = get_builder()
    builder.add_common_builds(shared_option_name="%s:shared" % name, pure_c=True)

    filtered_builds = []
    for settings, options, env_vars, build_requires, reference in builder.items:

        if settings["build_type"] == "Release" \
                and not("%s:shared"  % name in options and options["%s:shared" % name]):

            copy_env_vars(env_vars)

            if os.getenv('BITPRIM_RUN_TESTS', 'false') == 'true':
                # options["%s:with_benchmark" % name] = "True"
                options["%s:with_tests" % name] = "True"
                # options["%s:with_openssl_tests" % name] = "True"
                marchs = ["x86_64"]
            else:
                if full_build:
                    marchs = ["x86_64", ''.join(cpuid.cpu_microarchitecture()), "haswell", "skylake", "skylake-avx512"]
                else:
                    marchs = ["x86_64"]

            handle_microarchs("%s:microarchitecture" % name, marchs, filtered_builds, settings, options, env_vars, build_requires)
            # filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
