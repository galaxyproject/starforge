./build debian:squeeze atlas
./build debian:squeeze bcftools
./build debian:squeeze bowtie2
./build debian:squeeze emboos
./build debian:squeeze jellyfish
./build debian:squeeze kraken
./build debian:squeeze ngninx
./build debian:squeeze openms
./build debian:squeeze perlgd
./build debian:squeeze pkiss
./build debian:squeeze rnashapes
./build debian:squeeze samtools
./build debian:squeeze tophat
./build debian:squeeze tpp
./build debian:squeeze ucsc

python build.py --quiet tbl2asn
