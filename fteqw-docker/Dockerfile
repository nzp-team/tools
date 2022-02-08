FROM ubuntu:18.04

COPY MacOSX10.14.sdk.tar.xz /

WORKDIR /fteqw

RUN dpkg --add-architecture i386

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

RUN apt-get install -y \
    gcc-arm-linux-gnueabihf \
    gcc-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu \
 && rm -rf /var/lib/apt/lists/*

RUN cd /opt \
 && git clone https://github.com/tpoechtrager/osxcross.git \
 && cd osxcross \
 && git checkout 16efae89925c5cee1a7ae946c036c570f688f852 \
 && mv /MacOSX10.14.sdk.tar.xz tarballs \
 && PORTABLE=1 UNATTENDED=1 ./build.sh

ENV PATH $PATH:/opt/osxcross/target/bin