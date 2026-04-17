# Compiling Envoy proxy for istio on an aarch64 system and musl libc

I am using istio as gateway which embeds envoy proxy. Like for all other software I am building it from scratch
* in Gentoo image
* with musl libc
* on aarch64

I manage to succeed building istio including envoy proxy completely but it was a long journey over months (not only but also because each build of envoy took two days on my Raspberry PI 4 I used initially) and it was a hard journey to have the right configuration which works with the complex dependencies of envoy.
The setup worked for me compiling both, 1.28 and 1.29 releases except 1.29.1 which introduced a dependency issue on istio/proxyv2 side itself.

My setup:
* Raspberry PI with Gentoo
* Gentoo build container based on musl
* Bazel as build environment inside the container and finally
* building Envoy proxy using Bazel.

All the steps can be foudn in [the file I used to build the images](https://github.com/cainam/application-specifics/blob/main/istiod/vars/application_images.yaml)

## building phases
Each phase is implemented as a container image

### phase 1: bazel
* bazel is the tool which manages the complex build of envoy proxy
* building bazel requires java and a java distribution had to be taken which supports aarch64 as well as musl libc, so I choosed zulu
* envoy build up to version 1.29 at least is only compatible with bazel 7, not higher major releases
* it did not build out of the box, but some alpine patches solved the issue as alpine is building bazel, too

### phase 2: envoy-base
* provides addition dependencies required to build envoy:
  * software which is not well resolved within envoy build because e.g. no musl compatible package is available:
    * icu 
    * libevent
    * luajit
    * c-ares
    * zstd
    * nghttp2
    * zlib
  * clang and clang++ because missing llvm with gcc created some incompatibilities and my config is based on compiling envoy itself using llvm
  * a wrapper script for aarch64-unknown-linux-musl-ld.bfd to filter out incompatible options like --no-gdb-index, --start-lib and --end-lib

### phase 3: envoy
* tcmalloc=disabled because tcmalloc is not compatible with musl
* tools/jdk/ override repository to use the local java installation
* @rules_foreign_cc//toolchains:cmake_toolchain to support @platforms//cpu:aarch64
* WORKSPACE file modifications:
  * addressing a conflict between com_google_cel_spec and dev_cel:
    * add working com_google_cel_spec archive
    * add http_archive for com_github_cncf_xds with patches
  * include local_jdk override repository
  * add http_archive for rules_python with patches to use aarch64-unknown-linux-musl compatible version of python
  * register_toolchains("@toolchains_llvm//toolchain:all")
  * sed -i '/PATH/d' .bazelrc
  * sed -e '/googleurl/d' -i envoy.bazelrc
  * sed -e '/BAZEL_DO_NOT_DETECT_CPP_TOOLCH/d' -i envoy.bazelrc

### phase 4: proxyv2
a simple go build of istio/pilot/cmd/pilot-agent

### phase 5: pilot
a simple go build of istio/pilot/cmd/pilot-discovery
 
## what remains to be done
* improve the ld wrapper script, esp. to avoid hardcoded libraries
* verify again the WORKSPACE modifications to reduce them further again

## conclusion
Building envoy proxy from scratch on a Gentoo musl aarch64 systems is not trivial.

Up to now it requires quite some additional effort to maintain all the modifications which had to be made.

There is also no guarantee that the build gets quickly broken again by a new istio/proxyv2 release.

