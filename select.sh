#!/bin/bash

rm Allevents* DetectedFinal*
ls -d 201* > dirs
for dir in $(cat dirs)
do
    perl MergeEvents.pl /data1/zhouyj/XJ_ML/exML/$dir Allevents$dir
done

rm days
for i in $(seq 31)
do
    printf "%02d\n" $i >> days
done

for day in $(cat days)
do
    perl SelectFinal.pl 2016 09 $day Allevents201609$day
    mv DetectedFinal.dat DetectedFinal$day
done
python merge.py
rm dirs days
