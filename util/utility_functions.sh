#!/bin/bash
extract_tarball() {
    tarball=$1
    ext=`echo $tarball | rev | cut -d. -f1 | rev`
    case "$ext" in
        gz|tgz)
            tar zxf $tarball ;;
        bz2|tbz)
            tar jxf $tarball ;;
        xz)
            tar Jxf $tarball ;;
    esac
}

download_tarball() {
    url=$1
    wget --no-check-certificate $url 2>&1 | tee /tmp/wget.log
    tarball=`grep 'Saving to: .' /tmp/wget.log | sed 's/Saving to: .\(.\+\)./\1/'`
    echo $tarball
}
