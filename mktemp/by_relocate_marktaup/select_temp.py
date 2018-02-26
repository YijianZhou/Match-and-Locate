import os, glob, shutil
import numpy as np
from obspy.core import *

def calc_snr(st, win_len, search_rng):
    tp = st[0].stats.sac.t0
    ts = st[0].stats.sac.t1
    dt = st[0].stats.sac.b
    idx_p = int((tp-dt)*100)
    idx_s = int((ts-dt)*100)
    time_range_p = range(idx_p - search_rng[0], idx_p + search_rng[1])
    time_range_s = range(idx_s - search_rng[0], idx_s + search_rng[1])
    # calc SNR and AMP
    snre_p, ampe_p = CF(st[0].data, time_range_p, win_len)
    snre_s, ampe_s = CF(st[0].data, time_range_s, win_len)
    snrn_p, ampn_p = CF(st[1].data, time_range_p, win_len)
    snrn_s, ampn_s = CF(st[1].data, time_range_s, win_len)
    snrz, ampz = CF(st[2].data, time_range_p, win_len)
    # format output
    snre = np.round([snre_p, snre_s], 2)
    ampe = np.round([ampe_p, ampe_s], 2)
    snrn = np.round([snrn_p, snrn_s], 2)
    ampn = np.round([ampn_p, ampn_s], 2)
    snrz = round(snrz, 2)
    ampz = round(ampz, 2)
    tp = round(tp, 2)
    ts = round(ts, 2)
    return tp, ts, snre, snrn, snrz, ampe, ampn, ampz

def CF(data0, time_range, win_len):
    snr = np.array([])
    amp = np.array([])
    data = data0**2
    for i in time_range:
        if sum(data[i-win_len:i])==0: return -1, -1
        snri = sum(data[i:i+win_len]) / sum(data[i-win_len:i])
        snr = np.append(snr, snri)
        ampi = sum(abs(data0[i:i+1]))
        amp = np.append(amp, ampi)
    return np.amax(snr), np.amax(amp)

# output file 'catalog.dat'
out_file = 'catalog.dat'
if os.path.exists(out_file):
   os.unlink(out_file)
output = open(out_file, 'a')

# original catalog
catalog0 = 'reloc.dat'
tmp = open(catalog0); ctlg_lines = tmp.readlines(); tmp.close()

# pick params
win_len = 100
search_rng = [200, 200]

# remove noisy traces
path0 = os.getcwd()
#paths = glob.glob(os.path.join(path0, 'Template/20*'))
paths = glob.glob(os.path.join(path0, 'test/*'))
for path in paths:
  print('entering path {}'.format(path))
  os.chdir(path)
  zchns = sorted(glob.glob('*.*Z'))
  for zchn in zchns:
      net, sta, chn = zchn.split('.')
      three_chns = sorted(glob.glob('*%s*' %sta))
      st  = read(three_chns[0])
      st += read(three_chns[1])
      st += read(three_chns[2])
      st = st.normalize()
      tp, ts, snre, snrn, snrz, ampe, ampn, ampz = calc_snr(st, win_len, search_rng)
      print('    ', sta, 'tp:', tp, 'ts:', ts)
      print('        ', 'snr(e,n,z) = ', snre, snrn, snrz)
      print('        ', 'amp(e,n,z) = ', ampe, ampn, ampz)
      if snrz<10 or snre[0]<5 or snrn[0]<5\
         or ((snre[1]<3 or snrn[1]<3 or snre[1]+snrn[1]<10)\
             and (ampe[1]<0.9 or ampn[1]<0.9))\
         or st[0].stats.sac.t1>25:
         print('False!')
  # check if too few temps left
  if len(glob.glob('*')) < 9: shutil.rmtree(path)

# write catalog.dat
paths = glob.glob(os.path.join(path0, 'Template/20*'))
for path in paths:
  ot_key = os.path.split(path)[-1]
  for ctlg_line in ctlg_lines:
      date_time, lat, lon, mag = ctlg_line.split(',')
      date, time = date_time.split('T')
      key = ''.join(date.split('-')) +\
            ''.join(time.split(':'))[0:9]
      if key==ot_key:
         date = '/'.join(date.split('-'))
         time = time[0:11]
         output.write('{} {} {} {}  5 M {}\n'.format(date, time, lat, lon, mag[0:3]))
         break
