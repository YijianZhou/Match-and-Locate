"""
all sac files: ./events/org_time/[net].[sta].[chn]
have the same kztime
relocated catalog reloc.dat will be output
"""
import os, glob, shutil
import numpy as np
from obspy.core import *
#import matplotlib.pyplot as plt

def calc_tt(lat_range, lon_range, grid_width, sta_dic, vp, vs, dep):
    time_table = {}
    lat0 = lat_range[0]
    lon0 = lon_range[0]
    y_range = range(int((lat_range[1] - lat_range[0]) /grid_width))
    x_range = range(int((lon_range[1] - lon_range[0]) /grid_width))
    # calc time table, x to lon and y to lat
    for sta, sta_xy in sta_dic.items():
      sta_x = int((sta_xy[0] - lon0)/grid_width)
      sta_y = int((sta_xy[1] - lat0)/grid_width)
      tt_p = []
      tt_s = []
      for x in x_range:
        tti_p = []
        tti_s = []
        for y in y_range:
            dist = 111*grid_width *np.sqrt((x-sta_x)**2 + (y-sta_y)**2)
            tt_ij_p = np.sqrt(dep**2 + dist**2) /vp
            tt_ij_s = np.sqrt(dep**2 + dist**2) /vs
            tti_p.append(tt_ij_p)
            tti_s.append(tt_ij_s)
        tt_p.append(tti_p)
        tt_s.append(tti_s)
      time_table[sta] = [tt_p, tt_s]
    return time_table

def preprocess(stream):
    st = stream.detrend('constant')
    return st.filter('bandpass', freqmin=2., freqmax=40.)

def picker(stream, pwin, swin):
    time_shift = stream[0].stats.sac.b
    datax = stream[0].data
    datay = stream[1].data
    dataz = stream[2].data
    # maximum amp in E and N are initially picked S
    tsx0 = np.argmax(abs(datax))
    tsy0 = np.argmax(abs(datay))
    ts0 = (tsx0 + tsy0) /200
    if abs(tsx0-tsy0)>500 or tsx0<=swin+100 or tsy0<=swin+100:
       return 0.1, -1., ts0, -1
    # search 1s before ts0
    tsx, snrx = CF(datax, range(tsx0-100, tsx0), swin)
    tsx += tsx0-100
    tsy, snry = CF(datay, range(tsy0-100, tsy0), swin)
    tsy += tsy0-100
    ts = time_shift + (tsx + tsy)/200
    ssnr = (snrx + snry) /2
    if int(ts*100)-100 <= pwin:
       return 0.2, -1, ts, -1
    # maximum SNR in time before ts are picked P
    tp, psnr = CF(dataz, range(pwin, int((tsx + tsy)/2) - 100), pwin)
    tp = time_shift + (tp + pwin)/100
    return tp, ts, psnr, ssnr

def CF(data, idx_range, win_len):
    snr = np.array([])
    amp = data**2
    for i in idx_range:
        snri = sum(amp[i:i+win_len]) / sum(amp[i-win_len:i])
        snr = np.append(snr, snri)
    return np.argmax(snr), np.amax(snr)

def calc_ot(tp, ts, vp, vs):
    r = (ts-tp) /(1/vs - 1/vp)
    Tp = r/vp
    return tp-Tp


# picking params
pwin, swin = 100, 150
# reloc params
ot_dev = 2.5 # sec
vp = 5.8
vs = 3.2
dep = 5 # km
grid_width = 0.05 # degree
lon_range = [102.5, 104] # x
lat_range = [24.5, 26.5] # y

# input file (station list)
sta_info = 'station_ZSY'
 tmp = open(sta_info); sta_lines = tmp.readlines(); tmp.close()
sta_dic = {}
for sta_line in sta_lines:
    sta, lon, lat, ele = sta_line.split('\t')
    sta_dic[sta] = [float(lon), float(lat)]
# calc time table (sta: [[tp], [ts]])
time_table = calc_tt(lat_range, lon_range, grid_width, sta_dic, vp, vs, dep)

# output file
out_file = 'reloc.dat'
if os.path.exists(out_file):
   os.unlink(out_file)
output = open(out_file, 'a')


# for each evnet
#path0 = os.path.join(os.getcwd(), 'events_test/20160928111127.97') # for test
path0 = os.path.join(os.getcwd(), 'events/*')
stream_paths = sorted(glob.glob(path0))
for stream_path in stream_paths:
    os.chdir(stream_path)
    ot0 = os.path.split(stream_path)[-1]
    print('relocating event {}'.format(ot0))
    zchns = glob.glob('*.*Z')
    # make list of arrival time: [(org_time, tp, ts)]
    pha_times = []
    for zchn in zchns:
        net, sta, chn = zchn.split('.')
        three_chns = sorted(glob.glob('*%s*'%sta))
        # remove missed traces
        if len(three_chns)<3:
           print('    missing trace!')
           continue
        # repick traces
        st  = read(three_chns[0])
        st += read(three_chns[1])
        st += read(three_chns[2])
        st = preprocess(st)
        # seconds relative to header b 
        tp, ts, psnr, ssnr = picker(st, pwin, swin)
        # skip false detections
        if ts-tp>30 or ts-tp<1\
           or psnr<5 or ssnr<2.5:
           continue
        # calc org_time
        ot = calc_ot(tp, ts, vp, vs)
        # add weight (quality)
        if   psnr>20: wt=1.
        elif psnr>10: wt=0.75
        else:         wt=0.25
        pha_times.append((sta, ot, tp, ts, wt))
    # to numpy array
    pha_times = np.array(pha_times, 
                         dtype = [('sta', np.unicode_, 5), 
                                  ('org_time',float), 
                                  ('tp',float), 
                                  ('ts',float),
                                  ('weight',float)])
    # sort by org_time
    pha_times = np.sort(pha_times, order='org_time')
    # if false detected ((by picking result))
    if len(pha_times)<3:
       print('    false detection! (by picking result)')
       continue
    
    # find clustered org_times
    assoc_num = []
    ots = pha_times['org_time']
    for oti in ots:
        is_nbr = abs(ots-oti) < ot_dev
        assoc_num.append( sum(is_nbr.astype(float)) )
    max_num = np.amax(assoc_num)
    max_idx = np.argmax(assoc_num)
    # if less than four stations
    if max_num < 3:
       print('    false detection! (by orginal times)')
       continue
    else: t0 = ots[max_idx]
    reloc_ot = UTCDateTime(ot0) + t0
    
    # clustered org_times for relocation
    pha_times = pha_times[abs(ots-t0) < ot_dev]
    print(pha_times)
    # relocate
    res = 0
    for pha_time in pha_times:
        sta, _, tp, ts, wt = pha_time
        tt = time_table[sta]
        tt_p = np.array(tt[0])
        tt_s = np.array(tt[1])
        res_p = t0 + tt_p - tp
        res_s = t0 + tt_s - ts
        res += abs(res_p)*wt + abs(res_s)*wt
#    plt.imshow(res)
#    plt.show()
    min_res = np.amin(res)
    reloc_x, reloc_y = np.unravel_index(np.argmin(res), res.shape)
    reloc_lon = lon_range[0] + grid_width*reloc_x
    reloc_lat = lat_range[0] + grid_width*reloc_y
    print('event {} reloacted, lon {} lat {}, res = {}'.format(ot0, reloc_lon, reloc_lat, min_res))
    
    # write into relocated catalog
    output.write("{},{},{},1.0\n".format(reloc_ot, reloc_lat, reloc_lon))

