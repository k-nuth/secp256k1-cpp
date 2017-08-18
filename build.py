from conan.packager import ConanMultiPackager
import os

if __name__ == "__main__":
    builder = ConanMultiPackager(username="bitprim", channel="stable",
                                 remotes="https://api.bintray.com/conan/bitprim/bitprim",
                                 archs=["x86_64"])

    builder.add_common_builds(shared_option_name="secp256k1:shared")
    # builder.password = os.getenv("CONAN_PASSWORD")

    print("---------------------------------------")
    print(builder.builds)
    print("---------------------------------------")

    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["build_type"] == "Release" \
                and not("secp256k1:shared" in options and options["secp256k1:shared"]):
            filtered_builds.append([settings, options, env_vars, build_requires])

    print("---------------------------------------")
    print(filtered_builds)
    print("---------------------------------------")

    builder.builds = filtered_builds
    builder.run()
