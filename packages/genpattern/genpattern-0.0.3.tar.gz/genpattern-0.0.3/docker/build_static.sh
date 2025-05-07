#!/bin/sh
set -e

TARGETARCH=$(apk info --print-arch)
GCC_VERSION=$(basename $(ls -1d /usr/lib/gcc/${TARGETARCH}-alpine-linux-musl/* 2>/dev/null | head -n 1))

CC=clang
CXX=clang++
CFLAGS="-target ${TARGETARCH}-alpine-linux-musl -B/usr/lib/gcc/${TARGETARCH}-alpine-linux-musl/${GCC_VERSION} -fPIC"
CXXFLAGS="-stdlib=libc++ -target ${TARGETARCH}-alpine-linux-musl -B/usr/lib/gcc/${TARGETARCH}-alpine-linux-musl/${GCC_VERSION} -fPIC"
EXE_LD_FLAGS="-fuse-ld=lld -Wl,--no-undefined"
SHARED_LD_FLAGS="-fuse-ld=lld -L/usr/lib/gcc/${TARGETARCH}-alpine-linux-musl/${GCC_VERSION} -static -Wl,--no-undefined -Wl,/usr/lib/libc++.a -Wl,/usr/lib/libc++abi.a -Wl,--no-whole-archive"

cd /app
rm -rf build dist

python3 -m build --wheel --sdist --no-isolation \
  -Ccmake.define.BUILD_TESTS=ON \
  -Ccmake.define.CMAKE_C_COMPILER="${CC}" \
  -Ccmake.define.CMAKE_CXX_COMPILER="${CXX}" \
  -Ccmake.define.CMAKE_C_FLAGS="${CFLAGS}" \
  -Ccmake.define.CMAKE_CXX_FLAGS="${CXXFLAGS}" \
  -Ccmake.define.CMAKE_EXE_LINKER_FLAGS="${EXE_LD_FLAGS}" \
  -Ccmake.define.CMAKE_SHARED_LINKER_FLAGS="${SHARED_LD_FLAGS}" \
  -Ccmake.define.CMAKE_BUILD_TYPE=Release \
  -Cbuild-dir=build \
  --outdir dist

ctest --test-dir build --output-on-failure

pip install dist/*.whl
pytest -q

for whl in dist/*linux_${TARGETARCH}.whl; do
  python -m wheel tags --platform-tag manylinux_2_17_${TARGETARCH} "$whl"
  python -m wheel tags --platform-tag musllinux_1_2_${TARGETARCH} "$whl"
  rm "$whl"
done
