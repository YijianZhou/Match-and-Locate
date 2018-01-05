import os, glob

out_file = 'ML_cc0.5'
if os.path.exists(out_file):
  os.remove(out_file)
out = open(out_file,'a')

fnames = os.path.join(os.getcwd(), 'DetectedFinal*')
file_list = sorted(glob.glob(fnames))
for fname in file_list:
  tmp = open(fname); lines = tmp.readlines(); tmp.close()
  for i, line in enumerate(lines):
    if i>0:
      line = [x for x in line.split(' ') if x!='']
      date, time = line[1], line[2],
      lat, lon, dep = line[3], line[4], line[5]
      mag = line[6]
      date = '-'.join(date.split('/'))
      date_time = 'T'.join([date, time])
      out.write("{},{},{},{}\n".format(date_time, lat, lon, mag))
out.close()
