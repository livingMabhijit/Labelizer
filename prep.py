import pandas as pd
import numpy as np
scl = []
raw = []
file = pd.read_csv('9.csv',sep=',')

scl_npy_file = np.load('/Users/apple/Documents/work_DFA/All channel data/karthick_dropbox/RMS_data_with_IN_all.npy',allow_pickle = True)
raw_npy_file = np.load('/Users/apple/Documents/work_DFA/All channel data/karthick_dropbox/RMS_data_with_IN_all_raw.npy',allow_pickle=True)
for i in range (0,len(file)):
    scl.append(scl_npy_file[file.indx[i]])
    raw.append(raw_npy_file[file.indx[i]])
np.save("9_scl.npy", scl)
np.save("9_raw.npy", raw)
