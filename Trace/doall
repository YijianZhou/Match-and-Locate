#!/bin/bash
ls -d /data1/zhouyj/XJ_ML/Trace/201* > dirs
for dir in $(cat dirs)
do
    perl SACfilter.pl $dir
    perl SACH_O.pl $dir
done
rm dirs
