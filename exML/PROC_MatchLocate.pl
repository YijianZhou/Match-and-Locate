#!/usr/bin/env perl
use warnings;
#######################################
#       A perl script for detecting and locating low-magnitude events
#       Miao Zhang  11/22/2013  USTC        inital version
#       Miao Zhang  02/07/2015  USTC        add description
# Reference: Zhang and Wen, GJI, 2015
# Email: zhmiao@mail.ustc.edu.cn
#######################################
#Make sure the begin and end time of all the continuous seismograms are equal.
@ARGV >= 2 || die "perl $0 dir1(reference event) dir2(continuous data) [evla/evlo/evdp/mag] INPUT F\n";
$dir1 = $ARGV[0];
$dir2 = $ARGV[1];
$inputfile = $ARGV[3];

#Location and magnitude of the reference event
#Lat/Lon/Depth/Mag
$L = $ARGV[2];

#Search center
#Refevla/refevlo/refevdp
#Usually, centered at the template location.
$F = $ARGV[4];
chomp($F);

$TB = time();

#Search area
#MaxLat/MaxLon/MaxDepth
#"0/0/0" corresponds to the matched filter case.
#If you don't want to search the depth, please fix depth to be zero.
#There would be strong trade-off between origin time and depth if the station coverage is not very well.
$R = "0.16/0.16/0";

#Search inveral
#Dlat/Dlon/Ddepth (must not be zero for any one!)
$I = "0.02/0.02/1";

#output stacked cross-correlograms
#0 ----> don't output
#1 ----> just output the stacked CCs of the determined location of a new detertend event.[default]
#2 ----> just output the stacked continuous CCs of the searched grid.
$O = "0";

#Time interval
#Keep one event within a certain time window (e.g., 6 sec).
#It depends on your search area and station distance.
$D = "6.0";
                                                                                     1,1           Top
##SNR defination
##Gap/NoiseLength
##...    |   |      |
##...    t   t+GAP   t+GAP+NoiseLength
$N = "1.0/2.0";

##WindowLength/before/after
##The cross-correlation window based on the marked t1 in your templates.
#Here 5 sec is used, 1 sec before and 3 sec after the marked t1.
$T = "5.0/1.5/3.5";

#Define thresholds
#coef/ratio
#ratio = coef./backgroud CC
#If ratio is zero, that means there is no SNR constrain.
$H = "0.2/6";

#station parameter
#1.Channel number
#2.Template_dir Trace_dir dt_dD(horizontal slowness)/dt_dh(vertical slowness)
#3. ...
$INPUT = "INPUT.in";
$markornot = 1;

if($markornot == 1){
open(ST,"<$inputfile");
@sta = <ST>;
close(ST);
if(-e $INPUT){`rm $INPUT`;}
open(AA,">$INPUT");
for($i=0;$i<@sta;$i++){
    ($station,$t1,$DT) = split(" ",$sta[$i]);
    $station = sprintf("%-s",$station);
    #Make sure there are common stations in both directions.
    if(-e "$dir1/$station" && -e "$dir2/$station" ){
        print AA "$dir1/$station $dir2/$station $DT\n";
    }
}
close(AA);

open(AA,"<$INPUT");
@par = <AA>;
close(AA);
$num = @par;

open(NEW,">$INPUT");
print NEW "$num\n";
for($i=0; $i<@par;$i++){
chomp($par[$i]);
print NEW "$par[$i]\n";
}
close(NEW);
}

($maxlat,$maxlon,$maxh) = split('/',$R);
($dlat,$dlon,$dh) = split('/',$I);
$np = int(2*$maxlat/$dlat + 1)*(int(2*$maxlon/$dlon + 1))*int((2*$maxh/$dh + 1));
print STDERR "There are $np potential locations\n";
system("/home/yanc/software/ML/bin/MatchLocate -L$L -F$F -R$R -I$I -T$T -H$H -D$D -N$N -O$O $INPUT");
printf STDERR "../bin/MatchLocate -L$L -F$F -R$R -I$I -T$T -H$H -D$D -N$N -O$O $INPUT\n";

if($O == 1 ){
$stackcc1 = "SELECT_STACKCC";
if(-e $stackcc1){`rm $stackcc1/*`;}
else{`mkdir $stackcc1`}
`mv *.stack $stackcc1/`;
}

$TE = time();
$time = $TE - $TB;
printf STDERR "Time consuming is %6.2f mins\n",$time/60.0;
