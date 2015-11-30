./build.sh debian:squeeze atlas
./build.sh debian:squeeze bcftools
./build.sh debian:squeeze bowtie2
./build.sh debian:squeeze emboos
./build.sh debian:squeeze jellyfish
./build.sh debian:squeeze kraken
./build.sh debian:squeeze ngninx
./build.sh debian:squeeze openms
./build.sh debian:squeeze perlgd
./build.sh debian:squeeze pkiss
./build.sh debian:squeeze rnashapes
./build.sh debian:squeeze samtools
./build.sh debian:squeeze tophat
./build.sh debian:squeeze tpp
./build.sh debian:squeeze ucsc

python build.py --quiet tbl2asn
