#!/bin/bash
perl marktaup.pl
ls -d /data1/zhouyj/XJ_ML/Template/201* > dirs
for dir in $(cat dirs)
do
    perl SACfilter.pl $dir
done
rm dirs
