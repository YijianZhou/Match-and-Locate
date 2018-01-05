#/usr/bin/env perl 
use warnings;
@ARGV == 2 || die "perl $0 dir file\n";
$dir=$ARGV[0];
$file=$ARGV[1];
chomp($dir); chomp($file);

open(FL,">$file");
chdir "$dir";
@events = glob "*";
foreach $_(@events){
    chomp($_);
    open(JK,"<$_");
    @pars = <JK>;
    close(JK);
    $num = @pars-1;
    shift(@pars);
    for($i=0;$i<$num;$i++){
        chomp($pars[$i]);
        ($jk,$time,$lat,$lon,$dep,$mag,$coef,$r1,$r2) = split(" ",$pars[$i]);
        print FL "$time $lat $lon $dep $mag $coef $r1 $r2 $_\n";
    }
}
close(FL);
