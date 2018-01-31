import os, glob, shutil
import numpy as np
from obspy.core import *

def calc_snr(st, ts, win_len, search_rng):
    idx = int(ts*100)
    time_range = range(idx - search_rng[0], idx + search_rng[1])
    snre = CF(st[0].data, time_range, win_len)
    snrn = CF(st[1].data, time_range, win_len)
    snrz = CF(st[2].data, time_range, win_len)
    return round(snre,2), round(snrn,2), round(snrz,2)

def CF(data, time_range, win_len):
    snr = np.array([])
    amp = data**2
    for i in time_range:
        if sum(amp[i-win_len:i])==0: return -1
        snri = sum(amp[i:i+win_len]) / sum(amp[i-win_len:i])
        snr = np.append(snr, snri)
    return np.amax(snr)

# output file 'catalog.dat'
out_file = 'catalog.dat'
if os.path.exists(out_file):
   os.unlink(out_file)
output = open(out_file, 'a')

# original catalog
catalog0 = 'reloc.dat'
tmp = open(catalog0); ctlg_lines = tmp.readlines(); tmp.close()

# pick params
win_len = 150
search_rng = [200, 100]

# remove noisy traces
path0 = os.getcwd()
paths = glob.glob(os.path.join(path0, 'Template/20*'))
#paths = glob.glob(os.path.join(path0, 'test/20160922104622.12'))
for path in paths:
  print('entering path {}'.format(path))
  os.chdir(path)
  zchns = sorted(glob.glob('*.*Z'))
  for zchn in zchns:
      net, sta, chn = zchn.split('.')
      three_chns = sorted(glob.glob('*%s*' %sta))
      st = read(three_chns[0])
      st += read(three_chns[1])
      st += read(three_chns[2])
      ts = st[0].stats.sac.t1 - st[0].stats.sac.b
      snre, snrn, snrz = calc_snr(st, ts, win_len, search_rng)
      print('    ', sta, round(ts-10, 2), snre, snrn, snrz)
      if snre + snrn < 10 or snrz < 2.5\
         or snre < 3 or snrn < 3\
         or st[0].stats.sac.t1>25:
         for fname in three_chns: os.unlink(fname)
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

