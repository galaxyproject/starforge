#!/bin/bash
extract_tarball() {
    tarball=$1
    ext=`echo $tarball | rev | cut -d. -f1 | rev`
    echo $ext
    case "$ext" in
        gz|tgz)
            echo "tar zxf $tarball"
            tar zxf $tarball ;;
        bz2|tbz)
            echo "tar jxf $tarball"
            tar jxf $tarball ;;
        xz)
            echo "tar Jxf $tarball"
            tar Jxf $tarball ;;
    esac
}

download_tarball() {
    url=$1
    wget --no-check-certificate $url 2>&1 | tee /tmp/wget.log
    tarball=`grep 'Saving to: .' /tmp/wget.log | sed 's/Saving to: .\(.\+\)./\1/'`
    echo $tarball
}
