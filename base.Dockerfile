#############################################################################################
###       This Dockerfile build from source code: Poppler, Leptonica and Tesseract.       ###
###      In this way, you can set the desired versions (even the most recent ones).       ###
###                                                                                       ###
###   With 'curl' command, if you have TLS issues, use '--no-check-certificate' option.   ###
#############################################################################################
FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm

WORKDIR /
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# === Install OS Dependencies and Set Timezone === #
RUN apt update && \
    apt install -y build-essential && \
    apt install -y curl git unzip wget && \
    apt install -y python3-dev && \
    apt install -y gobject-introspection pkg-config && \
    apt install -y autoconf automake cmake libtool && \
    apt install -y  \
        gettext  \
        libarchive-dev  \
        libboost-dev  \
        libcairo2-dev  \
        libcurl4-openssl-dev  \
        libfontconfig1-dev  \
        libfreetype6-dev  \
        libgif-dev  \
        libglib2.0-dev  \
        libgpgme-dev  \
        libicu-dev  \
        libjpeg-dev  \
        libjpeg62-turbo-dev  \
        liblcms2-dev  \
        liblcms2-utils  \
        libnspr4  \
        libnss3  \
        libnss3-dev  \
        libopenjp2-7-dev  \
        libopenjp2-tools  \
        libpango1.0-dev  \
        libpng-dev  \
        libtiff-dev  \
        libtiff5-dev  \
        libturbojpeg0  \
        libwebp-dev  \
        libwebpdemux2  \
        qt6-base-dev  \
        qtbase5-dev  \
        webp  \
        zlib1g-dev && \
    apt clean && \
    rm -rf /etc/localtime && \
    ln -s /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone

# === Build Leptonica from Source === #
ENV MY_LEPTONICA_VERSION=1.85.0
RUN wget https://github.com/DanBloomberg/leptonica/archive/${MY_LEPTONICA_VERSION}.zip && \
    unzip ${MY_LEPTONICA_VERSION}.zip && \
    rm -f ${MY_LEPTONICA_VERSION}.zip && \
    cd leptonica-${MY_LEPTONICA_VERSION} && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    make clean && \
    cd ${WORKDIR}

# === Build Tesseract from Source === #
ENV MY_TESSERACT_VERSION=5.4.1
RUN wget https://github.com/tesseract-ocr/tesseract/archive/${MY_TESSERACT_VERSION}.zip && \
    unzip ${MY_TESSERACT_VERSION}.zip && \
    rm -f ${MY_TESSERACT_VERSION}.zip && \
    cd tesseract-${MY_TESSERACT_VERSION} && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    make clean && \
    cd ${WORKDIR}

# === Download External Linguistic Resources for Tesseract Engine === #
# valid values: tessdata | tessdata_best | tessdata_fast
ENV TESSDATA_TYPE=tessdata
RUN wget -O /usr/local/share/tessdata/osd.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/osd.traineddata && \
    wget -O /usr/local/share/tessdata/eng.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/eng.traineddata && \
    wget -O /usr/local/share/tessdata/ita.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/ita.traineddata && \
    wget -O /usr/local/share/tessdata/spa.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/spa.traineddata && \
    wget -O /usr/local/share/tessdata/fra.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/fra.traineddata && \
    wget -O /usr/local/share/tessdata/deu.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/deu.traineddata && \
    wget -O /usr/local/share/tessdata/por.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/por.traineddata && \
    wget -O /usr/local/share/tessdata/nld.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/nld.traineddata && \
    wget -O /usr/local/share/tessdata/equ.traineddata https://github.com/tesseract-ocr/${TESSDATA_TYPE}/raw/main/equ.traineddata

# === Build Poppler from Source === #
ENV MY_POPPLER_VERSION=24.10.0
RUN wget https://poppler.freedesktop.org/poppler-${MY_POPPLER_VERSION}.tar.xz && \
    tar -xvf poppler-${MY_POPPLER_VERSION}.tar.xz && \
    rm -f poppler-${MY_POPPLER_VERSION}.tar.xz && \
    cd poppler-${MY_POPPLER_VERSION} && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DTESTDATADIR=${PWD}/testfiles -DCMAKE_BUILD_TYPE=release -DENABLE_GPGME=OFF && \
    make && \
    make install && \
    make clean && \
    cd ${WORKDIR}

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONPATH=$PYTHONPATH:/
