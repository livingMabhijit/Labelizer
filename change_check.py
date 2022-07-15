import pandas as pd
import sys


# import my_app_v3
db = sys.argv[1]

def change_df_check(x,idx):
    my_df = pd.read_csv('csv/'+db+'.csv',sep = ',')#main_file_error_v6_windx_77k_edit_col.csv
    my_df['check'][idx] = x
    my_df.to_csv('csv/'+db+'.csv',sep = ',',index=False)#main_file_error_v6_windx_77k_edit_col.csv
    # idx =  my_app_v3.first_page(idx = idx+1)
