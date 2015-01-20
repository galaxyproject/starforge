FROM debian:squeeze

MAINTAINER Nate Coraor <nate@bx.psu.edu>

ENV DEBIAN_FRONTEND noninteractive

ADD http://downloads.sourceforge.net/project/samtools/samtools/0.1.19/samtools-0.1.19.tar.bz2 /build/

RUN apt-get -qq update && \
    apt-get install --no-install-recommends -y bzip2 make gcc libc6-dev zlib1g-dev libncurses5-dev && \
    cd /build && \
    tar jxf samtools-0.1.19.tar.bz2 && \
    cd samtools-0.1.19 && \
    make && \
    mkdir -p /build/dest/bin /build/dest/lib /build/dest/include/bam /build/dest/include/bcf && \
    cp samtools bcftools/bcftools bcftools/vcfutils.pl /build/dest/bin && \
    cp libbam.a bcftools/libbcf.a /build/dest/lib && \
    cp *.h /build/dest/include/bam && \
    cp bcftools/*.h /build/dest/include/bcf && \
    tar zcf /build/samtools-0.1.19-Linux-x86_64.tar.gz * -C /build/dest

