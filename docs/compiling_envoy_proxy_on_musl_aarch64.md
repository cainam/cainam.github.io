# Compiling Envoy proxy for istio on an aarch64 system and musl libc

I didn't succeed! Each single step forward was tricky, but I managed to move quite far but in the end I didn't manage to get it done.

This is how I tried to build Envoy:
* Raspberry PI with Gentoo
* Gentoo build container based on musl
* Bazel as build environment inside the container and finally
* building Envoy proxy using Bazel.

The following is a sequence I was trying to get bazel compiled on aarch64 with musl:
- I managed to get bazel using local python installation
- I managed to get bazel using local JDK
but I failed for the C-Compiler.

this compile works without gdb-index AND -nostdlib removal but I didn't manage to get bazel configured changing the options
I also didn't manage to get bazel reconfigured for using gcc so I gave up

### compiling bazel inside a container

The very first challenge was to get a usable jdk, but zulu turned out to work well:
```
tar xfz zulu21.44.17-ca-jdk21.0.8-linux_musl_aarch64.tar.gz 
export JAVA_HOME=/root/zulu21.44.17-ca-jdk21.0.8-linux_musl_aarch64
export PATH=$JAVA_HOME/bin/:$PATH 
```

Preparing bazel from source:
```
cd bazel
unzip ../bazel-8.3.1-dist.zip 
emerge app-arch/zip
sed -i '/nano/d' /etc/portage/profile/package.provided | grep nano
emerge --usepkg app-editors/nano
```

Bazel requires some fixes because it is not compatible with aarch64 and musl, but these fixes are already made available by Alpine (`patch -p1 < 0001-off64t-fix.patch`):
* bazel 8 apply https://gitlab.alpinelinux.org/alpine/aports/-/blob/e49daeab5c9554e8cb7ca23547037d6659d7be43/testing/bazel8/0001-off64t-fix.patch
* bazel 7 apply https://gitlab.alpinelinux.org/alpine/aports/-/blob/e49daeab5c9554e8cb7ca23547037d6659d7be43/testing/bazel7/0001-off64t-fix.patch but remove abuild subdirectory

Building and putting in place bazel:
```
env EXTRA_BAZEL_ARGS="--tool_java_runtime_version=local_jdk" bash ./compile.sh
cp -dp output/bazel $JAVA_HOME/bin
```

### compiling Envoy proxy using bazel
```
emerge -v llvm-core/clang llvm-runtimes/libcxx #llvm-runtimes/libcxxabi
git clone https://github.com/istio/proxy.git
cd proxy && git checkout release-1.26
echo "build --define tcmalloc=gperftools # in .bazelrc" >> .bazelrc 

export JAVA_HOME=/root/zulu21.44.17-ca-jdk21.0.8-linux_musl_aarch64
PATH=/usr/lib/llvm/20/bin/:${JAVA_HOME}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export CC=/usr/lib/llvm/20/bin/clang
sed -i '/PATH/d' .bazelrc
```

+ files in bazel directory!!!

.bazelrc contains: build:linux --action_env=PATH=/usr/lib/llvm/bin:/usr/local/bin:/bin:/usr/bin => try to comment this line
```
bazel build --verbose_failures --strip=always --config=sizeopt --noenable_bzlmod -- //:envoy 
time bazel build --verbose_failures --strip=always --config=sizeopt --noenable_bzlmod  --python_path=/usr/sbin/python3 --host_force_python=PY3 --extra_toolchains=//tools/python:noop_python_toolchain --extra_toolchains=//tools/python:system_python_toolchain  --toolchain_resolution_debug=1 --sandbox_debug --copt=-Wno-error --java_runtime_version=local_jdk --tool_java_runtime_version=local_jdk   -- //:envoy 
```

this fails:
```
/usr/lib/llvm/20/bin/clang-20 -U_FORTIFY_SOURCE -fstack-protector -Wall -Wthread-safety -Wself-assign -Wunused-but-set-parameter -Wno-free-nonheap-object -fcolor-diagnostics -fno-omit-frame-pointer -g0 -O2 -D_FORTIFY_SOURCE=1 -DNDEBUG -ffunction-sections -fdata-sections -no-canonical-prefixes -Wno-builtin-macro-redefined -D__DATE__=redacted -D__TIMESTAMP__=redacted -D__TIME__=redacted -DABSL_MIN_LOG_LEVEL=4 -fdebug-types-section -fPIC -Wno-deprecated-declarations -Wno-error=deprecated-enum-enum-conversion -DNULL_PLUGIN -Os -Wno-error -fexceptions   -Wl,-S -fuse-ld=/usr/lib/llvm/20/bin/ld.lld -B/usr/lib/llvm/20/bin -Wl,-no-as-needed -Wl,-z,relro,-z,now -lm -pthread -Wl,--gc-sections -l:libstdc++.a -fuse-ld=lld -nostdlib -lpthread a.c  -Wl,--gdb-index -v
```

### bazel debug: 
bazel query --output=build @python3_12_host//...
 bazel query --output=build @base_pip3_jinja2//...
