# syntax=docker/dockerfile:1
ARG ALPINE_VERSION=3.21

##########################
# 1) Build stage: compile custom llvm-runtimes apk with -fPIC
##########################
FROM alpine:${ALPINE_VERSION} AS build-llvm-runtimes
ARG ALPINE_VERSION
ENV ALPINE_VERSION=${ALPINE_VERSION}

RUN apk update && apk add --no-cache \
    alpine-sdk \
    linux-headers \
    python3 \
    samurai \
    clang \
    clang-dev \
    llvm-dev \
    llvm-static \
    cmake \
    make \
    tar \
    wget \
    libc++-dev \
    lld \
    llvm-libunwind-dev

RUN adduser -D builder \
 && addgroup builder abuild \
 && echo "PACKAGER=\"builder <builder@local>\"" >> /etc/abuild.conf \
 && su builder -c "abuild-keygen -an" \
 && cp /home/builder/.abuild/*.pub /etc/apk/keys/

WORKDIR /home/builder

RUN wget -O- "https://gitlab.alpinelinux.org/alpine/aports/-/archive/${ALPINE_VERSION}-stable/aports-${ALPINE_VERSION}-stable.tar.gz?path=main/llvm-runtimes" \
    | tar -xvzf - \
 && wget -O- "https://gitlab.alpinelinux.org/alpine/aports/-/archive/${ALPINE_VERSION}-stable/aports-${ALPINE_VERSION}-stable.tar.gz?path=main/gtest" \
    | tar -xvzf -

RUN chown -R builder:abuild /home/builder

USER builder

WORKDIR /home/builder/aports-$ALPINE_VERSION-stable-main-llvm-runtimes/main/llvm-runtimes
RUN sed -i '/^options=/a CFLAGS="-fPIC"' APKBUILD \
 && sed -i '/^options=/a CXXFLAGS="-fPIC"' APKBUILD \
 && abuild checksum \
 && abuild -r

WORKDIR /home/builder/aports-$ALPINE_VERSION-stable-main-gtest/main/gtest
RUN sed -i '/^builddir=/a CXXFLAGS="-stdlib=libc++"\nLDFLAGS="-fuse-ld=lld"\nCXX=clang++\nCC=clang' APKBUILD \
 && abuild checksum \
 && abuild -r

RUN mv /home/builder/packages/main/$(apk info --print-arch) /home/builder/packages/main/packages

##########################
# 2) Final stage: unprivileged user + venv
##########################
FROM alpine:${ALPINE_VERSION}

RUN apk update && apk add --no-cache \
    clang clang-extra-tools \
    cmake make ninja musl-dev \
    libc++-dev libc++-static \
    lld \
    wget \
    python3 py3-pip

ENV VIRTUAL_ENV=/root/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY --from=build-llvm-runtimes /home/builder/packages/main/packages /tmp/packages
RUN apk add --allow-untrusted /tmp/packages/*.apk

COPY docker/build_static.sh /usr/local/bin/build.sh
COPY pyproject.toml python/ README.md LICENSE* ./

RUN python3 -m venv "$VIRTUAL_ENV" \
 && "$VIRTUAL_ENV/bin/pip" install --upgrade pip build \
 && "$VIRTUAL_ENV/bin/pip" install --no-cache-dir pip-tools \
 && pip-compile --all-build-deps --extra test -o /tmp/requirements.txt pyproject.toml \
 && pip-sync /tmp/requirements.txt

RUN chmod +x /usr/local/bin/build.sh

CMD ["/usr/local/bin/build.sh"]
