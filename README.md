# Match-and-Locate
Input files maker for M&L.
Package Match-and-Locate (Zhang, 2014) is an immplementation of MFT in detecting micro-seismic events.
This set of scripts is for preparing the input files for easier usage of M&L

./Trace

  continuous waveforms, in the format of Trace/yyyymmdd/net.sta.chn
  Call your database (which in our workstation is /data3) and copy into related folders, and run 'doall' to change the head file and filter the traces.
  
  in cmd: 
  
      python mkTrace.py
      cd [/data1/zhouyj/ML]/Trace     
      ./doall



./Template

  templates for MFT, in the format of Template/yyyymmddhhmmss.ss/net.sta.chn 
  Run STA/LTA to get SNR info for selection (such as PSIRpicker, Li 2016), and run 'doall' to mark theoretical arrival time and filter the templates.
  
  in cmd: 
       
      python mkTemp.py
      cd [/data1/zhouyj/ML]/Template     
      ./doall



./exML

  Having prepared the input files, run M&L in this folder.
  This will output the matching result in days (yyyymmdd)
  Run 'select.sh' to further select the result and merge them into a single catalog (csv file)
 
