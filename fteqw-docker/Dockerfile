# Source Debian for better package sourcing when cross-compiling
FROM debian:bookworm-slim

# For obtaining SDL when cross-compiling
RUN dpkg --add-architecture i386 \
 && dpkg --add-architecture armhf \
 && dpkg --add-architecture arm64

RUN apt-get update \
 && apt-get install -y \
    zip \
    git \
    wget \
    emscripten \
    build-essential \
    crossbuild-essential-i386 \
    crossbuild-essential-armhf \
    crossbuild-essential-arm64 \
    gcc-mingw-w64-i686 \
    gcc-mingw-w64-x86-64 \
    mingw-w64-i686-dev \
    mingw-w64-x86-64-dev \
    mingw-w64-tools \
    libsdl2-dev \
    libsdl2-dev:i386 \
    libsdl2-dev:arm64 \
    libsdl2-dev:armhf \
    libgnutls28-dev \
    libgnutls28-dev:i386 \
    libgnutls28-dev:arm64 \
    libgnutls28-dev:armhf
