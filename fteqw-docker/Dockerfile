# Source Ubuntu for better package sourcing
FROM ubuntu:18.04

# Currently broken macOS SDK
COPY MacOSX10.14.sdk.tar.xz /

# Set up some EMSDK variables
ARG EMSCRIPTEN_VERSION=tot
ENV EMSDK /emsdk

WORKDIR /

# For building 32 bit binaries
RUN dpkg --add-architecture i386

# First round of apt spam
RUN apt-get update \
 && apt-get install -y \
    build-essential \
    cmake \
    zip \
    git \
    wget \
    gcc-multilib \
    libasound2-dev \
    libbz2-dev \
    libegl1-mesa-dev \
    libbullet-dev \
    libfreetype6-dev \
    libgnutls28-dev \
    libjpeg-dev \
    libpng-dev \
    libvorbis-dev \
    libvulkan-dev \
    libwayland-dev \
    libxcursor-dev \
    libxkbcommon-dev \
    libxrandr-dev \
    libavdevice-dev \
    libxml2-dev \
    libssl-dev \
    libz-dev \
    clang \
    llvm \
    mingw-w64 \
    mingw-w64-common \
    mingw-w64-i686-dev \
    mingw-w64-x86-64-dev \
    mingw-w64-tools \
    linux-libc-dev:i386

# EMSDK apt spam (2nd round)
RUN apt-get install -y \
    binutils \
    ca-certificates \
    file \
    python3 \
    python3-pip

# Third wave + delete apt list to save space
RUN apt-get install -y \
    gcc-arm-linux-gnueabihf \
    gcc-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu \
 && rm -rf /var/lib/apt/lists/*

# Proceed with EMSDK install
RUN cd / && \
    git clone https://github.com/emscripten-core/emsdk && \
    cd ${EMSDK} && \
    ./emsdk install ${EMSCRIPTEN_VERSION}

# Set up OSXCross with the macOS SDK
RUN cd /opt \
 && git clone https://github.com/tpoechtrager/osxcross.git \
 && cd osxcross \
 && git checkout 16efae89925c5cee1a7ae946c036c570f688f852 \
 && mv /MacOSX10.14.sdk.tar.xz tarballs \
 && PORTABLE=1 UNATTENDED=1 ./build.sh

# OSXCross path
ENV PATH $PATH:/opt/osxcross/target/bin

# Edit path again, but for EMSDK
ENV EMSDK=/emsdk \
    EM_CONFIG=/emsdk/.emscripten \
    EMSDK_NODE=/emsdk/node/14.18.2_64bit/bin/node \
    PATH="/emsdk:/emsdk/upstream/emscripten:/emsdk/upstream/bin:/emsdk/node/14.18.2_64bit/bin:${PATH}"

# (Finally) create a config for emcc
RUN emcc --generate-config
