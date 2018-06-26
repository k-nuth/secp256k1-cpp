# from conan.packager import ConanMultiPackager
# import copy
# import re
# import platform
import os
import cpuid
from ci_utils.utils import get_builder, handle_microarchs

if __name__ == "__main__":
    builder, name = get_builder()
    builder.add_common_builds(shared_option_name="%s:shared" % name, pure_c=True)

    filtered_builds = []
    # for settings, options, env_vars, build_requires in builder.builds:
    for settings, options, env_vars, build_requires, reference in builder.items:

        if settings["build_type"] == "Release" \
                and not("%s:shared"  % name in options and options["%s:shared" % name]):

            env_vars["BITPRIM_BUILD_NUMBER"] = os.getenv('BITPRIM_BUILD_NUMBER', '-')

            if os.getenv('BITPRIM_RUN_TESTS', 'false') == 'true':
                # options["%s:with_benchmark" % name] = "True"
                options["%s:with_tests" % name] = "True"
                # options["%s:with_openssl_tests" % name] = "True"

            marchs = ["x86_64", ''.join(cpuid.cpu_microarchitecture()), "haswell", "skylake", "skylake-avx512"]
            handle_microarchs("%s:microarchitecture" % name, marchs, filtered_builds, settings, options, env_vars, build_requires)
            # filtered_builds.append([settings, options, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
