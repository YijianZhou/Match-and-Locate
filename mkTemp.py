"""
make Template from selected catalog for M&L
select by SNR (remove noisy traces)
cp -r events Template
python mkTemp.py
result:
/Template
catalog.dat
"""
import os, glob, shutil
pick_file = 'pick.dat'
out_file = 'catalog.dat'
ctlg0 = 'ML_result.csv'
if os.path.exists(out_file):
  os.unlink(out_file)
output = open(out_file, 'a')

tmp = open(ctlg0); ctlg_lines = tmp.readlines(); tmp.close()
tmp = open(pick_file); picks = tmp.readlines(); tmp.close()
event_path = '/home/zhouyj/Xiaojiang/MFT/mktemp/Template/'

psnr_lim = 10
ssnr_lim = 5
sta_lim = 3
# filter all traces
for i, pick in enumerate(picks):
    print('checking {}th pick'.format(i))
    pickinfo = [x for x in pick.split(' ') if x!='']
    sta = pickinfo[0]
    ot = pickinfo[1]
    os.chdir(os.path.join(event_path, ot))
    traces = glob.glob("*")
    # find related trace
    for trace in traces:
        net, stai, time, chn, _ = trace.split('.')
        # rm low SNR traces
        ptime, psnr = pickinfo[2], pickinfo[3]
        stime, ssnr = pickinfo[4], pickinfo[5]
        if sta==stai and\
           (float(psnr) < psnr_lim or\
            float(ssnr) < ssnr_lim):
           os.unlink(trace)

# rename and rm noisy traces (> 4 stations)
paths = glob.glob(event_path + '*')
for path in paths:
    os.chdir(path)
    traces = glob.glob('*')
    if len(traces) < 3*sta_lim:
       shutil.rmtree(path)
       continue
    for trace in traces:
        net, stai, time, chn, _ = trace.split('.')
        os.rename(trace, '.'.join(['ZSY', stai, chn]))

# make catalog.dat
print('make catalog.dat')
paths = glob.glob(event_path + '*')
for path in paths:
  for ctlg_line in ctlg_lines:
      date_time, lat, lon, mag = ctlg_line.split(',')
      date, time = date_time.split('T')
      key = ''.join(date.split('-')) +\
            ''.join(time.split(':'))[0:6]
      if key == os.path.split(path)[-1]:
         os.rename(path, '.'.join([path, time.split('.')[1][0:2]]))
         date = '/'.join(date.split('-'))
         time = time[0:11]
         output.write('{} {} {} {}  5 M {}\n'.format(date, time, lat, lon, mag[0:3]))
