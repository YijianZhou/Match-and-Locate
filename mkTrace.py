"""
make Trace from continuous waveform for M&L
archived data in /data3
"""
import os, glob, shutil
from obspy.core import UTCDateTime

path0 = '/data1/zhouyj/XJ_ML/Trace'
stream_paths = sorted(glob.glob('/data3/XJ_SAC/ZSY/*/*/*/*')) # sta/yyyy/mm/dd

print('copy streams into Trace')
for stream_path in stream_paths:
    print('entering path {}'.format(stream_path))
    os.chdir(stream_path)
    streams = glob.glob('*')
    for stream in streams:
        net, sta, yr, jday, chn, _ = stream.split('.')
        date_time = UTCDateTime(yr+jday)
        rela_path = ''.join(str(date_time.date).split('-'))
        out_path = os.path.join(path0, rela_path)
        if not os.path.exists(out_path):
           os.mkdir(out_path)
        fname = '.'.join([net, sta, chn])
        tar_path = os.path.join(out_path, fname)
        shutil.copy(stream, tar_path)
