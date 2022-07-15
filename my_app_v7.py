from ast import Continue
import pandas as pd
import numpy as np
import streamlit as st
import pickle
from sklearn import preprocessing
# import matplotlib.pyplot as plt
import streamlit as st
from bokeh.plotting import figure
from bokeh.layouts import gridplot
import streamlit.components.v1 as components
import change
import change_check
import time
import sys
from enum import IntEnum
db = sys.argv[1]

class used_chnls(IntEnum):
    VA    =    0
    VB    =    1
    VC    =    2
    IA    =    3
    IB    =    4
    IC    =    5
    IN    =    6
    VA_PD =    7
    VB_PD =    8
    VC_PD =    9
    IA_PD =    10
    IB_PD =    11
    IC_PD =    12
    IN_PD =    13
    IA_EVENS = 14
    IB_EVENS = 15
    IC_EVENS = 16
    IN_EVENS = 17
    PA =       18
    PB =       19
    PC =       20
    QA =       21
    QB =       22
    QC =       23
    IA_NONS = 24
    IB_NONS = 25
    IC_NONS = 26
    IN_NONS = 27
    VAB = 28
    VBC = 29
    VCA = 30

with open('current_index.txt') as f:
        lines = f.readlines()
        line = lines[-1]
        # print(lines)
        f.close()

#------------------------ Home Page setup -------------------------------
st.set_page_config(
     page_title="DFA Labelizer",
     layout="wide"   
 )
st.sidebar.header('Page Navigation')
navigation_tab = st.sidebar.selectbox('Choose Page', ('Labelizer','Label verify','Search', 'RMS Not-edited','False +ve/-ve'))

#------------------ Page set up ends ----------------------------------
if navigation_tab == 'Labelizer':
    # path='/Users/apple/Documents/work_DFA/Labelizer/'
    
    t0 = time.time()
    st.subheader(""" DFA Labelizer """)
    ## Data
    x  = np.load("npy/"+db+"_scl.npy",allow_pickle=True) #error_rms_77k_ce.npy
    x_raw = np.load("npy/"+db+"_raw.npy",allow_pickle=True)#error_rms_raw_77k_ce.npy
     # curated dataframe for only actual , pred class as file name
    main_file = pd.read_csv("csv/"+db+'.csv',sep = ',')#main_file_error_v6_windx_77k_edit_col.csv
    #key value holder
    vals={10110:'Capacitor on',10120: 'Capacitor off',12110: 'Motor start',13170: 'Inrush',15110: 'OC normal',66666:'Other Downstream',77777:'Not downstream',88888:'Unknown',99999:'Nothing'} 

    # For new start
    if 'count' not in st.session_state:
        st.session_state.count = 0
        print('start count '+str(st.session_state.count))

    def first_page(idx):
  
            classes = ["10110: Capacitor on",
                        "10120: Capacitor off",
                        "12110: Motor start",
                        "13170: Inrush",
                        "15110: OC normal",
                        "66666: Other Downstream",
                        "77777: Not downstream",
                        "88888: Unknown",
                        "99999: Nothing"]
            for i in classes:
                if i[0:5]==str(main_file['classification_codes'][idx]): #comparing first 5 char e.g '15110'  with the string value of class list
                    cl_index = i # this will later used for what will be the default value for radio button 
            # actual classes fetched from DB
            col_1, col_2, = st.columns(2)
            with col_1:
                st.write('Ground Truth')
                if main_file.status[idx]=='Edited':
                    st.success(vals[main_file['classification_codes'][idx]] )
                else:
                    st.subheader(vals[main_file['classification_codes'][idx]] )

            with col_2:
                st.write('Predicted class')
                st.subheader( vals[main_file['predictions'][idx]] )



            #### Plot starts
            f_name = str(main_file['file_names'][idx].split('/')[4])
            # st.write(str(idx)+' - PQD Filename '+f_name)
            if f_name[0]== 'S' or f_name[0]== 'L':
                link = str(idx)+' - PQD Filename: '+str(f_name)+' '+' [File link](https://ce5.dfa.plus/grid/?plot_files='+ str(f_name)+')'
                st.write(link)
            else:
                link = str(idx)+' - PQD Filename: '+str(f_name)+' '+' [File link](https://dfa.plus/grid/?company=plot_only&plot_files='+ str(f_name)+')'
                st.write(link)
            # st.markdown(link, unsafe_allow_html=True)
            # st.write(main_file['status'][idx])
            ## Add new fields 
            md1,md2,md3,md4,md5  = st.columns(5)
            with md1:
                st.subheader(' Duration: '+str(main_file['duration_seconds'][idx])+ ' seconds')
            with md2:
                st.subheader(' Frequency: '+str(main_file['powerline_frequencies'][idx])+ ' Hz')
            with md3:
                flags = {
                    1:'TWACS',
                    0:'NONE',
                    2:'DC',
                    3:'TWACS,DC'
                }
                st.subheader(' Flags: '+str(flags[main_file['ind_flags'][idx]]))
            with md4:
                three_wires = {1:'True',0:'False'}
                st.subheader(' Three Wire: '+str(three_wires[main_file['three_wire'][idx]]))
            with md5:
                dpts = {1:'True',0:'False'}
                st.subheader(' Delta PTs: '+str(dpts[main_file['delta_pts'][idx]]))
            
            # print(str(main_file['check'][idx]))
            if main_file['check'][idx]==True or main_file['check'][idx]=='True':
                checked = st.checkbox('Main event occurs later than 1 < t < 3 seconds.',key = 'my_chk'+str(st.session_state.count),on_change=uncheck_box,value = True)
            else:
                unchecked = st.checkbox('Main event occurs later than 1 < t < 3 seconds.',key = 'my_chk'+str(st.session_state.count),on_change=check_box,value = False)
            
            col_orig, col_scaled, = st.columns(2)
            with col_orig:
                RAW_RMS = st.button('Original RMS',key='my_btn'+str(st.session_state.count))
            with col_scaled:
                SCALED_RMS = st.button('Scaled RMS',key='my_scld_btn'+str(st.session_state.count))
            

            ##plot Normalized
            print('here is the idx'+ str(idx))
            x1 = [i for i in range(0,len(x_raw[idx][0]))]
            
            p1 = figure(plot_width=600,plot_height=200,)
            p2 = figure(plot_width=600,plot_height=200)
            p3 = figure(plot_width=600,plot_height=200)
            p4 = figure(plot_width=600,plot_height=200)
            p5 = figure(plot_width=600,plot_height=200)
            p6 = figure(plot_width=600,plot_height=200)
            
            main_indx = main_file.indx[idx]
            print('indxzt = '+ str(main_indx))

            indxz = main_file.index[idx]
            print('indxz = '+ str(indxz))
            y0 = x_raw[indxz][used_chnls.VA]
            y1 = x_raw[indxz][used_chnls.VB]
            y2 = x_raw[indxz][used_chnls.VC]  
            if SCALED_RMS is True :
                y0 = x[indxz][used_chnls.VA]
                y1 = x[indxz][used_chnls.VB]
                y2 = x[indxz][used_chnls.VC] 
            p1.line(x1,y0,color = 'red')
            p1.line(x1,y1,color = 'blue')
            p1.line(x1,y2,color = 'green')

            #IA_IB_IC
            y3 = x_raw[indxz][used_chnls.IA]
            y4 = x_raw[indxz][used_chnls.IB]
            y5 = x_raw[indxz][used_chnls.IC]
            y6 = x_raw[indxz][used_chnls.IN]
            if SCALED_RMS is True:
                y3 = x[indxz][used_chnls.IA]
                y4 = x[indxz][used_chnls.IB]
                y5 = x[indxz][used_chnls.IC]
                y6 = x[indxz][used_chnls.IN]
            p2.line(x1,y3,color = 'red')
            p2.line(x1,y4,color = 'blue')
            p2.line(x1,y5,color = 'green')
            p2.line(x1,y6,color = 'brown')

            #IEVEN
            y14 = x_raw[indxz][used_chnls.IA_EVENS]
            y15 = x_raw[indxz][used_chnls.IB_EVENS]
            y16 = x_raw[indxz][used_chnls.IC_EVENS]
            y17 = x_raw[indxz][used_chnls.IN_EVENS]
            if SCALED_RMS is True:
                y14 = x_raw[indxz][used_chnls.IA_EVENS]
                y15 = x_raw[indxz][used_chnls.IB_EVENS]
                y16 = x_raw[indxz][used_chnls.IC_EVENS]
                y17 = x_raw[indxz][used_chnls.IN_EVENS]
            
            p3.line(x1,y14,color = 'red')
            p3.line(x1,y15,color = 'blue')
            p3.line(x1,y16,color = 'green')
            p3.line(x1,y17,color = 'brown')
            
            #INONs
            y24 = x_raw[indxz][used_chnls.IA_NONS]
            y25 = x_raw[indxz][used_chnls.IB_NONS]
            y26 = x_raw[indxz][used_chnls.IC_NONS]
            y27 = x_raw[indxz][used_chnls.IN_NONS]
            if SCALED_RMS is True:
                y24 = x_raw[indxz][used_chnls.IA_NONS]
                y25 = x_raw[indxz][used_chnls.IB_NONS]
                y26 = x_raw[indxz][used_chnls.IC_NONS]
                y27 = x_raw[indxz][used_chnls.IN_NONS]
            
            p4.line(x1,y24,color = 'red')
            p4.line(x1,y25,color = 'blue')
            p4.line(x1,y26,color = 'green')
            p4.line(x1,y27,color = 'brown')

            #PA_PB_PC
            max_a = max(abs(x_raw[indxz][used_chnls.PA]))
            max_b = max(abs(x_raw[indxz][used_chnls.PB]))
            max_c = max(abs(x_raw[indxz][used_chnls.PC]))
            max_all = max(max_a,max_b,max_c)
            print('Max all val '+str(max_all))

            if max_all >=1000000:
                metric  = 'Mwatts'
                y18 = x_raw[indxz][used_chnls.PA]/1000000
                y19 = x_raw[indxz][used_chnls.PB]/1000000
                y20 = x_raw[indxz][used_chnls.PC]/1000000
            else:
                metric  = 'Kwatts'
                y18 = x_raw[indxz][used_chnls.PA]/1000
                y19 = x_raw[indxz][used_chnls.PB]/1000
                y20 = x_raw[indxz][used_chnls.PC]/1000
            if SCALED_RMS is True:
                y18 = x[indxz][used_chnls.PA]
                y19 = x[indxz][used_chnls.PB]
                y20 = x[indxz][used_chnls.PC]
            p5.line(x1,y18,color = 'red')
            p5.line(x1,y19,color = 'blue')
            p5.line(x1,y20,color = 'green')
            
            #QA_QB_QC
            max_aa = max(abs(x_raw[indxz][used_chnls.QA]))
            max_bb = max(abs(x_raw[indxz][used_chnls.QB]))
            max_cc = max(abs(x_raw[indxz][used_chnls.QC]))
            max_all_abc = max(max_aa,max_bb,max_cc)
            print('Max all val '+str(max_all_abc))

            if max_all_abc >=1000000:
                metric_q  = 'Mvars'
                y21 = x_raw[indxz][used_chnls.QA]/1000000
                y22 = x_raw[indxz][used_chnls.QB]/1000000
                y23 = x_raw[indxz][used_chnls.QC]/1000000
            else:
                metric_q = 'Kvars'
                y21 = x_raw[indxz][used_chnls.QA]/1000
                y22 = x_raw[indxz][used_chnls.QB]/1000
                y23 = x_raw[indxz][used_chnls.QC]/1000

            # y29 = x_raw[indx,:,21]
            # y30 = x_raw[indx,:,22]
            # y31 = x_raw[indx,:,23]
            if SCALED_RMS is True:
                y21 = x[indxz][used_chnls.QA]
                y22 = x[indxz][used_chnls.QB]
                y23 = x[indxz][used_chnls.QC]
            p6.line(x1,y21,color = 'red')
            p6.line(x1,y22,color = 'blue')
            p6.line(x1,y23,color = 'green')

            col1, col2,col3  = st.columns(3)
            col4,col5,col6 = st.columns(3)

            with col1:
                st.write('Voltage')
                st.bokeh_chart(p1, use_container_width=False,)
        
            with col2:
                if SCALED_RMS is not True:
                    st.write('Real Power in '+ str(metric))
                    st.bokeh_chart(p5, use_container_width=False)
                else:
                    st.write('Real Power')
                    st.bokeh_chart(p5, use_container_width=False)
            
            with col3:
                st.write('Current Even')
                st.bokeh_chart(p3, use_container_width=False)
            
            with col4:
                st.write('Current')
                st.bokeh_chart(p2, use_container_width=False)
            
            with col5:
                if SCALED_RMS is not True:
                    st.write('Reactive Power in '+ str(metric_q))
                    st.bokeh_chart(p6, use_container_width=False)
                else:
                    st.write('Reactive Power')
                    st.bokeh_chart(p6, use_container_width=False)
            
                
            with col6:
                st.write('Current NONs')
                st.bokeh_chart(p4, use_container_width=False)

            return idx

    
    # Keyboard part
    def capon():
        st.write('Previously: cap on was clicked')
        print('cap on was clicked')
        pred_classification_code = 10110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1        
        
    def capoff():
        st.write('Previously: cap off was clicked')
        print('cap off was clicked')
        pred_classification_code = 10120
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1        
        
    def motstart():
        st.write('Previously: motor start was clicked')
        print('motor start was clicked')
        pred_classification_code = 12110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1        
        

    def inrush():
        st.write('Previously: inrush was clicked')
        print('inrush was clicked')
        pred_classification_code = 13170
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1        
        
    def oc():
        st.write('Previously: oc was clicked')
        print('oc was clicked')
        pred_classification_code = 15110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1        
        
    def ods():
        st.write('Previously: other downstream was clicked')
        print('ods was clicked')
        pred_classification_code = 66666
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1
    def nds():
        st.write('Previously: Not downstream was clicked')
        print('nds was clicked')
        pred_classification_code = 77777
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1
    def unk():
        st.write('Previously: Unknown was clicked')
        print('unk was clicked')
        pred_classification_code = 88888
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1
    def noth():
        st.write('Previously: Nothing was clicked')
        print('noth was clicked')
        pred_classification_code = 99999
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.count )
        st.session_state.count = st.session_state.count+1
    
    def check_box():
        st.write('Check required later')
        print('check clicked')
        req_check = 'True'
        change_check.change_df_check(x = req_check,idx = st.session_state.count )
    
    def uncheck_box():
        st.write('Check required later')
        print('check clicked')
        req_check = ' '
        change_check.change_df_check(x = req_check,idx = st.session_state.count )

    # Button Init
    left_col, right_col= st.columns(2)
    with right_col:
        if st.session_state.count != len(x):
            next_btn = st.button('Next RMS')
        else:
            next_btn = st.button('Next RMS',disabled=True)
    with left_col:
        if st.session_state.count == 0:
            prev_button = st.button('Previous RMS', disabled=True)
        else:
            prev_button = st.button('Previous RMS')
    
   
    one,two,three,four,five,six,seven,eight,nine= st.columns(9)
    with one:
        c1 = st.button('1. 10110: Capacitor on')
    with two:
        c2 = st.button('2. 10120: Capacitor off')
    with three:
        c3 = st.button('3. 12110: Motor start')
    with four:
        c4 = st.button('4. 13170: Inrush')
    with five:
        c5 = st.button('5. 15110: OC normal')

    with six:
        c6 = st.button('6. 66666: Other Downstream')
    with seven:
        c7 = st.button('7. 77777: Not downstream')
    with eight:
        c8 = st.button('8. 88888: Unknown')
    with nine:
        c9 = st.button('9. 99999: Nothing')


    if c1:
        capon()
    elif c2:
        capoff()
    elif c3:
        motstart()
    elif c4:
        inrush()
    elif c5:
        oc() 

    elif c6:
        ods()
    elif c7:
        nds()
    elif c8:
        unk()
    elif c9:
        noth()

    
    if next_btn is False and prev_button is False and st.session_state.count == 0:
        st.session_state.count = int(line)
        idx =  first_page(idx = int(line))
    elif next_btn is False and prev_button is False and st.session_state.count != 0:
        # indxy = radio_change1()
        print('indixy')
        idx = first_page(idx = st.session_state.count)

    elif prev_button is True and next_btn is False:
        st.session_state.count -= 1
        idx = first_page(idx = st.session_state.count)

    elif next_btn is True and prev_button is False:
        st.session_state.count += 1
        idx =  first_page(idx = st.session_state.count)

    

    # print('current indx '+str(indx))
    print(st.session_state)
    
    # Write last index
    with open('current_index.txt', 'w') as f:
        f.write(str(st.session_state.count))
        f.close()
        t1 = time.time()
        print(f'{round(t1-t0,3) } seconds \n')
        print('ends here')
    components.html(
        """
    <script>
    const doc = window.parent.document;
    buttons = Array.from(doc.querySelectorAll('button[kind=primary]'));
    const next_button = buttons.find(el => el.innerText === 'Next RMS');
    const prev_button = buttons.find(el => el.innerText === 'Previous RMS');

    const c1_button = buttons.find(el => el.innerText === '1. 10110: Capacitor on');
    const c2_button = buttons.find(el => el.innerText === '2. 10120: Capacitor off');
    const c3_button = buttons.find(el => el.innerText === '3. 12110: Motor start');
    const c4_button = buttons.find(el => el.innerText === '4. 13170: Inrush');
    const c5_button = buttons.find(el => el.innerText === '5. 15110: OC normal');

    const c6_button = buttons.find(el => el.innerText === '6. 66666: Other Downstream');
    const c7_button = buttons.find(el => el.innerText === '7. 77777: Not downstream');
    const c8_button = buttons.find(el => el.innerText === '8. 88888: Unknown');
    const c9_button = buttons.find(el => el.innerText === '9. 99999: Nothing');
    
    checks = Array.from(doc.querySelectorAll('label[data-baseweb=checkbox]'));
    const check = checks.find(el => el.innerText === 'Main event occurs later than 1 < t < 3 seconds.');

    doc.addEventListener('keydown', function(e) {
        switch (e.keyCode) {
            case 13: // (13 = enter)
                next_button.click();
                break;
            case 8: // (8 = back space)
                prev_button.click();
                break;
            case 37: // (37 = Left Arrow)
                prev_button.click();
                break;
            case 39: // (39 = Right arrow)
                next_button.click();
                break;


            case 49: // (49 = num 1)
                c1_button.click();
                break;
            case 50: // (50 = num 2)
                c2_button.click();
                break;
            case 51: // (51 = num 3)
                c3_button.click();
                break;
            case 52: // (52 = num 4)
                c4_button.click();
                break;
            case 53: // (53 = num 5)
                c5_button.click();
                break;

            case 54: //(54 = num6)
                c6_button.click();
                break;
            case 55: //(55 = num7)
                c7_button.click();
                break;
            case 56: //(56 = num8)
                c8_button.click();
                break;
            case 57: //(57 = num9)
                c9_button.click();
                break;
            
            case 83: //(83 = char s)
                
                check.click();
                //alert()
                break;
            
        }
    });
    </script>
    """,
        height=0,
        width=0,
    )

elif navigation_tab == 'Label verify':
    st.header('Label verify page')
    
    main_file_verify = pd.read_csv("csv/"+db+'.csv',sep = ',')#main_file_error_v6_windx_77k_edit_col.csv
    x_arr  = np.load("npy/"+db+"_raw.npy",allow_pickle=True)
    
    
    vals={'Capacitor on':10110,'Capacitor off':10120,'Motor start':12110,'Inrush':13170,'OC normal':15110,'Other Downstream':66666,'Not downstream':77777,'Unknown':88888,'Nothing':99999}
    option = st.selectbox(
     'Select the classification code',
     ('Capacitor on',
      'Capacitor off',
       'Motor start',
       'Inrush',
       'OC normal',
       'Other Downstream',
       'Not downstream',
       'Unknown',
       'Nothing'
       ))
    selection = vals[option]

    print('sel '+ str(selection))
    
    selected_df = main_file_verify[main_file_verify.classification_codes ==selection]
    print(len(selected_df))
    total_size = len(selected_df)
    col_size = int((total_size/2)-1)
    
    col_1, col_2,col_3,col_4  = st.columns(4)
    
    # with col_1:
        # src1 = 
        # for idx in selected_df.index[0:51] :
    for idx in selected_df.index[:total_size]:
        
        # print(idx)
        # print(selected_df[selected_df.indx==indx1]['file_name'])
        x1 = [i for i in range(0,len(x_arr[idx][0]))]
        p1 = figure(plot_width=450,plot_height=100)
        p2 = figure(plot_width=450,plot_height=100)
        p5 = figure(plot_width=450,plot_height=100)
        p6 = figure(plot_width=450,plot_height=100)

        #VA_VB_VC
        y1 = x_arr[idx][used_chnls.VA]
        y2 = x_arr[idx][used_chnls.VB]
        y3 = x_arr[idx][used_chnls.VC]  
        
        p1.line(x1,y1,color = 'red')
        p1.line(x1,y2,color = 'blue')
        p1.line(x1,y3,color = 'green')

        #IA_IB_IC
        y5 = x_arr[idx][used_chnls.IA]
        y6 = x_arr[idx][used_chnls.IB]
        y7 = x_arr[idx][used_chnls.IC]
        y8 = x_arr[idx][used_chnls.IN]
        p2.line(x1,y5,color = 'red')
        p2.line(x1,y6,color = 'blue')
        p2.line(x1,y7,color = 'green')
        p2.line(x1,y8,color = 'brown')

        #PA_PB_PC
        
        # y25 = x_arr[idx,:,18]
        # y26 = x_arr[idx,:,19]
        # y27 = x_arr[idx,:,20]

        # p5.line(x1,y25,color = 'red')
        # p5.line(x1,y26,color = 'blue')
        # p5.line(x1,y27,color = 'green')
        

        max_a = max(abs(x_arr[idx][used_chnls.PA]))
        max_b = max(abs(x_arr[idx][used_chnls.PB]))
        max_c = max(abs(x_arr[idx][used_chnls.PC]))
        max_all = max(max_a,max_b,max_c)
        print('Max all val '+str(max_all))

        if max_all >=1000000:
            metric  = 'Mwatts'
            y25 = x_arr[idx][used_chnls.PA]/1000000
            y26 = x_arr[idx][used_chnls.PB]/1000000
            y27 = x_arr[idx][used_chnls.PC]/1000000
        else:
            metric  = 'Kwatts'
            y25 = x_arr[idx][used_chnls.PA]/1000
            y26 = x_arr[idx][used_chnls.PC]/1000
            y27 = x_arr[idx][used_chnls.PA]/1000
        
        p5.line(x1,y25,color = 'red')
        p5.line(x1,y26,color = 'blue')
        p5.line(x1,y27,color = 'green')
        #QA_QB_QC
        
        # y29 = x_arr[idx,:,21]
        # y30 = x_arr[idx,:,22]
        # y31 = x_arr[idx,:,23]

        max_aa = max(abs(x_arr[idx][used_chnls.QA]))
        max_bb = max(abs(x_arr[idx][used_chnls.QB]))
        max_cc = max(abs(x_arr[idx][used_chnls.QC]))
        max_all_abc = max(max_aa,max_bb,max_cc)
        print('Max all val '+str(max_all_abc))

        if max_all_abc >=1000000:
            metric_q  = 'Mvars'
            y29 = x_arr[idx][used_chnls.QA]/1000000
            y30 = x_arr[idx][used_chnls.QB]/1000000
            y31 = x_arr[idx][used_chnls.QC]/1000000
        else:
            metric_q = 'Kvars'
            y29 = x_arr[idx][used_chnls.QA]/1000
            y30 = x_arr[idx][used_chnls.QB]/1000
            y31 = x_arr[idx][used_chnls.QC]/1000

        p6.line(x1,y29,color = 'red')
        p6.line(x1,y30,color = 'blue')
        p6.line(x1,y31,color = 'green')


        
            ## st.bokeh_chart(gr1, use_container_width=False)
        
        with col_1:
            st.write(str(idx)+' - '+str(selected_df[selected_df.index==idx]['file_names'].iloc[0].split('/')[4]))
            st.write('Voltage')
            st.bokeh_chart(p1, use_container_width=False)
        with col_2:
            # st.text('|')
            # st.write(str(idx)+' - '+str(selected_df[selected_df.index==idx]['file_name'].iloc[0]))
            f_name = str(selected_df['file_names'][idx].split('/')[4])
            if f_name[0]== 'S' or f_name[0]== 'L':
                link = '[File link](https://ce5.dfa.plus/grid/?plot_files='+ str(f_name)+')'
                st.write(link)
            else:
                link = '[File link](https://dfa.plus/grid/?company=plot_only&plot_files='+ str(f_name)+')'
                st.write(link)
            st.write('Current')
            st.bokeh_chart(p2, use_container_width=False)
        with col_3:
            # st.text('|')
            st.write(str(idx)+' - '+str(selected_df[selected_df.index==idx]['file_names'].iloc[0].split('/')[4]))
            st.write('Real Power in '+str(metric))
            st.bokeh_chart(p5, use_container_width=False)
        with col_4:
            # st.text('|')
            st.write(str(idx)+' - '+str(selected_df[selected_df.index==idx]['file_names'].iloc[0].split('/')[4]))
            st.write('Reactive Power in '+str(metric_q) )
            st.bokeh_chart(p6, use_container_width=False)

    

elif navigation_tab == 'Search':
    st.header('SEARCH')
    main_file = pd.read_csv("csv/"+db+'.csv',sep = ',')#main_file_error_v6_windx_77k_edit_col.csv
    title = st.number_input('File index',0)
    title_indx = main_file.index[title]
    print(title_indx)
    srch = st.button('search')
    x  = np.load("npy/"+db+"_scl.npy",allow_pickle=True)
    x_raw = np.load("npy/"+db+"_raw.npy",allow_pickle=True)
    # curated dataframe for only actual , pred class as file name
    # main_file = pd.read_csv('main_file_error_v6_windx_77k_edit_col.csv',sep = ',')
    #key value holder
    vals={10110:'Capacitor on',10120: 'Capacitor off',12110: 'Motor start',13170: 'Inrush',15110: 'OC normal',66666:'Other Downstream',77777:'Not downstream',88888:'Unknown',99999:'Nothing'} 

    if 'count' not in st.session_state:
        st.session_state.count = title_indx

    def first_page(idx = title_indx):
        
  
        classes = ["10110: Capacitor on",
                    "10120: Capacitor off",
                    "12110: Motor start",
                    "13170: Inrush",
                    "15110: OC normal",
                    "66666: Other Downstream",
                    "77777: Not downstream",
                    "88888: Unknown",
                    "99999: Nothing"]
        for i in classes:
            if i[0:5]==str(main_file['classification_codes'][idx]): #comparing first 5 char e.g '15110'  with the string value of class list
                cl_index = i # this will later used for what will be the default value for radio button 
        # actual classes fetched from DB
        col_1, col_2, = st.columns(2)
        with col_1:
            st.write('Ground Truth')
            st.header( vals[main_file['classification_codes'][idx]] )
        with col_2:
            st.write('Predicted class')
            st.header( vals[main_file['predictions'][idx]] )



        #### Plot starts
        f_name=str(main_file['file_names'][idx].split('/')[4])
        # st.write(str(idx)+' - PQD Filename '+f_name)
        if f_name[0]== 'S' or f_name[0]== 'L':
            link = str(idx)+' - PQD Filename '+str(f_name)+' [File link](https://ce5.dfa.plus/grid/?plot_files='+ str(f_name)+')'
        else:
            link = str(idx)+' - PQD Filename '+str(f_name)+' [File link](https://dfa.plus/grid/?company=plot_only&plot_files='+ str(f_name)+')'
        st.markdown(link, unsafe_allow_html=True)
        # st.write(main_file['status'][idx])

        ## Add new fields 
        md1,md2,md3,md4,md5  = st.columns(5)
        with md1:
            st.subheader(' Duration: '+str(main_file['duration_seconds'][idx])+ ' seconds')
        with md2:
            st.subheader(' Frequency: '+str(main_file['powerline_frequencies'][idx])+ ' Hz')
        with md3:
            flags = {
                1:'TWACS',
                0:'NONE',
                2:'DC',
                3:'TWACS,DC'
            }
            st.subheader(' Flags: '+str(flags[main_file['ind_flags'][idx]]))
        with md4:
            three_wires = {1:'True',0:'False'}
            st.subheader(' Three Wire: '+str(three_wires[main_file['three_wire'][idx]]))
        with md5:
            dpts = {1:'True',0:'False'}
            st.subheader(' Delta PTs: '+str(dpts[main_file['delta_pts'][idx]]))
        
        col_orig, col_scaled, = st.columns(2)
        with col_orig:
            RAW_RMS = st.button('Original RMS',key='raw'+str(st.session_state.count))
        with col_scaled:
            SCALED_RMS = st.button('Scaled RMS',key='scaled'+str(st.session_state.count),disabled=True)
        

        ##plot Normalized
        print('here is the idx'+ str(idx))
        x1 = [i for i in range(0,len(x_raw[idx][0]))]
        
        p1 = figure(plot_width=600,plot_height=200,)
        p2 = figure(plot_width=600,plot_height=200)
        p3 = figure(plot_width=600,plot_height=200)
        p4 = figure(plot_width=600,plot_height=200)
        p5 = figure(plot_width=600,plot_height=200)
        p6 = figure(plot_width=600,plot_height=200)
        
        main_indx = main_file.indx[idx]
        print('indxzt = '+ str(main_indx))

        indxz = main_file.index[idx]
        print('indxz = '+ str(indxz))
        y0 = x_raw[indxz][used_chnls.VA]
        y1 = x_raw[indxz][used_chnls.VB]
        y2 = x_raw[indxz][used_chnls.VC]  
        if SCALED_RMS is True :
            y0 = x[indxz][used_chnls.VA]
            y1 = x[indxz][used_chnls.VB]
            y2 = x[indxz][used_chnls.VC] 
        p1.line(x1,y0,color = 'red')
        p1.line(x1,y1,color = 'blue')
        p1.line(x1,y2,color = 'green')

        #IA_IB_IC
        y3 = x_raw[indxz][used_chnls.IA]
        y4 = x_raw[indxz][used_chnls.IB]
        y5 = x_raw[indxz][used_chnls.IC]
        y6 = x_raw[indxz][used_chnls.IN]
        if SCALED_RMS is True:
            y3 = x[indxz][used_chnls.IA]
            y4 = x[indxz][used_chnls.IB]
            y5 = x[indxz][used_chnls.IC]
            y6 = x[indxz][used_chnls.IN]
        p2.line(x1,y3,color = 'red')
        p2.line(x1,y4,color = 'blue')
        p2.line(x1,y5,color = 'green')
        p2.line(x1,y6,color = 'brown')

        #IEVEN
        y14 = x_raw[indxz][used_chnls.IA_EVENS]
        y15 = x_raw[indxz][used_chnls.IB_EVENS]
        y16 = x_raw[indxz][used_chnls.IC_EVENS]
        y17 = x_raw[indxz][used_chnls.IN_EVENS]
        if SCALED_RMS is True:
            y14 = x_raw[indxz][used_chnls.IA_EVENS]
            y15 = x_raw[indxz][used_chnls.IB_EVENS]
            y16 = x_raw[indxz][used_chnls.IC_EVENS]
            y17 = x_raw[indxz][used_chnls.IN_EVENS]
        
        p3.line(x1,y14,color = 'red')
        p3.line(x1,y15,color = 'blue')
        p3.line(x1,y16,color = 'green')
        p3.line(x1,y17,color = 'brown')
        
        #INONs
        y24 = x_raw[indxz][used_chnls.IA_NONS]
        y25 = x_raw[indxz][used_chnls.IB_NONS]
        y26 = x_raw[indxz][used_chnls.IC_NONS]
        y27 = x_raw[indxz][used_chnls.IN_NONS]
        if SCALED_RMS is True:
            y24 = x_raw[indxz][used_chnls.IA_NONS]
            y25 = x_raw[indxz][used_chnls.IB_NONS]
            y26 = x_raw[indxz][used_chnls.IC_NONS]
            y27 = x_raw[indxz][used_chnls.IN_NONS]
        
        p4.line(x1,y24,color = 'red')
        p4.line(x1,y25,color = 'blue')
        p4.line(x1,y26,color = 'green')
        p4.line(x1,y27,color = 'brown')

        #PA_PB_PC
        max_a = max(abs(x_raw[indxz][used_chnls.PA]))
        max_b = max(abs(x_raw[indxz][used_chnls.PB]))
        max_c = max(abs(x_raw[indxz][used_chnls.PC]))
        max_all = max(max_a,max_b,max_c)
        print('Max all val '+str(max_all))

        if max_all >=1000000:
            metric  = 'Mwatts'
            y18 = x_raw[indxz][used_chnls.PA]/1000000
            y19 = x_raw[indxz][used_chnls.PB]/1000000
            y20 = x_raw[indxz][used_chnls.PC]/1000000
        else:
            metric  = 'Kwatts'
            y18 = x_raw[indxz][used_chnls.PA]/1000
            y19 = x_raw[indxz][used_chnls.PB]/1000
            y20 = x_raw[indxz][used_chnls.PC]/1000
        if SCALED_RMS is True:
            y18 = x[indxz][used_chnls.PA]
            y19 = x[indxz][used_chnls.PB]
            y20 = x[indxz][used_chnls.PC]
        p5.line(x1,y18,color = 'red')
        p5.line(x1,y19,color = 'blue')
        p5.line(x1,y20,color = 'green')
        
        #QA_QB_QC
        max_aa = max(abs(x_raw[indxz][used_chnls.QA]))
        max_bb = max(abs(x_raw[indxz][used_chnls.QB]))
        max_cc = max(abs(x_raw[indxz][used_chnls.QC]))
        max_all_abc = max(max_aa,max_bb,max_cc)
        print('Max all val '+str(max_all_abc))

        if max_all_abc >=1000000:
            metric_q  = 'Mvars'
            y21 = x_raw[indxz][used_chnls.QA]/1000000
            y22 = x_raw[indxz][used_chnls.QB]/1000000
            y23 = x_raw[indxz][used_chnls.QC]/1000000
        else:
            metric_q = 'Kvars'
            y21 = x_raw[indxz][used_chnls.QA]/1000
            y22 = x_raw[indxz][used_chnls.QB]/1000
            y23 = x_raw[indxz][used_chnls.QC]/1000

        # y29 = x_raw[indx,:,21]
        # y30 = x_raw[indx,:,22]
        # y31 = x_raw[indx,:,23]
        if SCALED_RMS is True:
            y21 = x[indxz][used_chnls.QA]
            y22 = x[indxz][used_chnls.QB]
            y23 = x[indxz][used_chnls.QC]
        p6.line(x1,y21,color = 'red')
        p6.line(x1,y22,color = 'blue')
        p6.line(x1,y23,color = 'green')

        col1, col2,col3  = st.columns(3)
        col4,col5,col6 = st.columns(3)

        with col1:
            st.write('Voltage')
            st.bokeh_chart(p1, use_container_width=False,)
    
        with col2:
            if SCALED_RMS is not True:
                st.write('Real Power in '+ str(metric))
                st.bokeh_chart(p5, use_container_width=False)
            else:
                st.write('Real Power')
                st.bokeh_chart(p5, use_container_width=False)
        
        with col3:
            st.write('Current Even')
            st.bokeh_chart(p3, use_container_width=False)
        
        with col4:
            st.write('Current')
            st.bokeh_chart(p2, use_container_width=False)
        
        with col5:
            if SCALED_RMS is not True:
                st.write('Reactive Power in '+ str(metric_q))
                st.bokeh_chart(p6, use_container_width=False)
            else:
                st.write('Reactive Power')
                st.bokeh_chart(p6, use_container_width=False)
        
            
        with col6:
            st.write('Current NONs')
            st.bokeh_chart(p4, use_container_width=False)

        return idx

    
    # Keyboard part
    def capon():
        st.write('Previously: cap on was clicked')
        print('cap on was clicked')
        pred_classification_code = 10110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1        
        
    def capoff():
        st.write('Previously: cap off was clicked')
        print('cap off was clicked')
        pred_classification_code = 10120
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1        
        
    def motstart():
        st.write('Previously: motor start was clicked')
        print('motor start was clicked')
        pred_classification_code = 12110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1        
        

    def inrush():
        st.write('Previously: inrush was clicked')
        print('inrush was clicked')
        pred_classification_code = 13170
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1        
        
    def oc():
        st.write('Previously: oc was clicked')
        print('oc was clicked')
        pred_classification_code = 15110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1        
        
    def ods():
        st.write('Previously: other downstream was clicked')
        print('ods was clicked')
        pred_classification_code = 66666
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1
    def nds():
        st.write('Previously: Not downstream was clicked')
        print('nds was clicked')
        pred_classification_code = 77777
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1
    def unk():
        st.write('Previously: Unknown was clicked')
        print('unk was clicked')
        pred_classification_code = 88888
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1
    def noth():
        st.write('Previously: Nothing was clicked')
        print('noth was clicked')
        pred_classification_code = 99999
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = idx )
        # st.session_state.count = st.session_state.count+1
    
   
    one,two,three,four,five,six,seven,eight,nine= st.columns(9)
    with one:
        c1 = st.button('1. 10110: Capacitor on')
    with two:
        c2 = st.button('2. 10120: Capacitor off')
    with three:
        c3 = st.button('3. 12110: Motor start')
    with four:
        c4 = st.button('4. 13170: Inrush')
    with five:
        c5 = st.button('5. 15110: OC normal')

    with six:
        c6 = st.button('6. 66666: Other Downstream')
    with seven:
        c7 = st.button('7. 77777: Not downstream')
    with eight:
        c8 = st.button('8. 88888: Unknown')
    with nine:
        c9 = st.button('9. 99999: Nothing')


    if c1:
        capon()
    elif c2:
        capoff()
    elif c3:
        motstart()
    elif c4:
        inrush()
    elif c5:
        oc() 

    elif c6:
        ods()
    elif c7:
        nds()
    elif c8:
        unk()
    elif c9:
        noth()

    if srch is True:
        idx =  first_page()
    
    components.html(
        """
    <script>
    const doc = window.parent.document;
    buttons = Array.from(doc.querySelectorAll('button[kind=primary]'));

    const srch = buttons.find(el => el.innerText === 'search');

    const c1_button = buttons.find(el => el.innerText === '1. 10110: Capacitor on');
    const c2_button = buttons.find(el => el.innerText === '2. 10120: Capacitor off');
    const c3_button = buttons.find(el => el.innerText === '3. 12110: Motor start');
    const c4_button = buttons.find(el => el.innerText === '4. 13170: Inrush');
    const c5_button = buttons.find(el => el.innerText === '5. 15110: OC normal');

    const c6_button = buttons.find(el => el.innerText === '6. 66666: Other Downstream');
    const c7_button = buttons.find(el => el.innerText === '7. 77777: Not downstream');
    const c8_button = buttons.find(el => el.innerText === '8. 88888: Unknown');
    const c9_button = buttons.find(el => el.innerText === '9. 99999: Nothing');
    

    doc.addEventListener('keydown', function(e) {
        switch (e.keyCode) {

            case 13: // (13 = enter)
                srch.click();
                break;
            
            
        }
    });
    </script>
    """,
        height=0,
        width=0,
    )


elif navigation_tab == 'RMS Not-edited':
    with open('current_index_not_edited.txt') as fne:
        lines_ne = fne.readlines()
    
    line_ne = lines_ne[-1]
    print(lines_ne)
    fne.close()



    st.header('RMS NOT EDITED')
    x  = np.load("npy/"+db+"_scl.npy",allow_pickle=True)
    xx_raw = np.load("npy/"+db+"_raw.npy",allow_pickle=True)
     # curated dataframe for only actual , pred class as file name
    main_file1 = pd.read_csv("csv/"+db+'.csv',sep = ',')#main_file_error_v6_windx_77k_edit_col.csv
    main_file = main_file1[main_file1.status!='Edited']
    # print(main_file.index)
    x_raw = []
    for i in main_file.index:
        x_raw.append(xx_raw[i])
    np.save("temp_raw.npy", x_raw)
    x_raw = np.load("temp_raw.npy",allow_pickle=True)
    main_file = main_file.reset_index(drop=True)
    
    #key value holder
    vals={10110:'Capacitor on',10120: 'Capacitor off',12110: 'Motor start',13170: 'Inrush',15110: 'OC normal',66666:'Other Downstream',77777:'Not downstream',88888:'Unknown',99999:'Nothing'} 

    # For new start
    if 'cnt' not in st.session_state:
        st.session_state.cnt = 0
        print('start count '+str(st.session_state.cnt))
        # main_file.index[idx]

    def first_page(idx):
  
            classes = ["10110: Capacitor on",
                        "10120: Capacitor off",
                        "12110: Motor start",
                        "13170: Inrush",
                        "15110: OC normal",
                        "66666: Other Downstream",
                        "77777: Not downstream",
                        "88888: Unknown",
                        "99999: Nothing"]
            for i in classes:
                if i[0:5]==str(main_file['classification_codes'][idx]): #comparing first 5 char e.g '15110'  with the string value of class list
                    cl_index = i # this will later used for what will be the default value for radio button 
            # actual classes fetched from DB
            col_1, col_2, = st.columns(2)
            with col_1:
                st.write('Ground Truth')
                st.header(vals[main_file['classification_codes'][idx]] )

            with col_2:
                st.write('Predicted class')
                st.header( vals[main_file['predictions'][idx]] )



            #### Plot starts
            f_name = str(main_file['file_names'][idx].split('/')[4])
            # st.write(str(idx)+' - PQD Filename '+f_name)
            if f_name[0]== 'S' or f_name[0]== 'L':
                link = str(idx)+' - PQD Filename '+str(f_name)+' [File link](https://ce5.dfa.plus/grid/?plot_files='+ str(f_name)+')'
                st.write(link)
            else:
                link = str(idx)+' - PQD Filename '+str(f_name)+' [File link](https://dfa.plus/grid/?company=plot_only&plot_files='+ str(f_name)+')'
                st.write(link)
            # st.markdown(link, unsafe_allow_html=True)
            # st.write(main_file['status'][idx])
            ## Add new fields 
            md1,md2,md3,md4,md5  = st.columns(5)
            with md1:
                st.subheader(' Duration: '+str(main_file['duration_seconds'][idx])+ ' seconds')
            with md2:
                st.subheader(' Frequency: '+str(main_file['powerline_frequencies'][idx])+ ' Hz')
            with md3:
                flags = {
                    1:'TWACS',
                    0:'NONE',
                    2:'DC',
                    3:'TWACS,DC'
                }
                st.subheader(' Flags: '+str(flags[main_file['ind_flags'][idx]]))
            with md4:
                three_wires = {1:'True',0:'False'}
                st.subheader(' Three Wire: '+str(three_wires[main_file['three_wire'][idx]]))
            with md5:
                dpts = {1:'True',0:'False'}
                st.subheader(' Delta PTs: '+str(dpts[main_file['delta_pts'][idx]]))

            if main_file['check'][idx]=='True' or main_file['check'][idx]==True:
                checked = st.checkbox('Main event occurs later than 1 < t < 3 seconds.',key = 'my_chk'+str(st.session_state.cnt),on_change=uncheck_box,value = True)
            else:
                unchecked = st.checkbox('Main event occurs later than 1 < t < 3 seconds.',key = 'my_chk'+str(st.session_state.cnt),on_change=check_box,value = False)
            
            col_orig, col_scaled, = st.columns(2)
            with col_orig:
                RAW_RMS = st.button('Original RMS',key='my_btn'+str(st.session_state.cnt))
            with col_scaled:
                SCALED_RMS = st.button('Scaled RMS',key='my_scld_btn'+str(st.session_state.cnt))
            

            ##plot Normalized
            print('here is the idx'+ str(idx))
            x1 = [i for i in range(0,len(x_raw[idx][0]))]
            
            p1 = figure(plot_width=600,plot_height=200,)
            p2 = figure(plot_width=600,plot_height=200)
            p3 = figure(plot_width=600,plot_height=200)
            p4 = figure(plot_width=600,plot_height=200)
            p5 = figure(plot_width=600,plot_height=200)
            p6 = figure(plot_width=600,plot_height=200)
            
            main_indx = main_file.indx[idx]
            print('indxzt = '+ str(main_indx))

            indxz = main_file.index[idx]
            print('indxz = '+ str(indxz))
            y0 = x_raw[indxz][used_chnls.VA]
            y1 = x_raw[indxz][used_chnls.VB]
            y2 = x_raw[indxz][used_chnls.VC]  
            if SCALED_RMS is True :
                y0 = x[indxz][used_chnls.VA]
                y1 = x[indxz][used_chnls.VB]
                y2 = x[indxz][used_chnls.VC] 
            p1.line(x1,y0,color = 'red')
            p1.line(x1,y1,color = 'blue')
            p1.line(x1,y2,color = 'green')

            #IA_IB_IC
            y3 = x_raw[indxz][used_chnls.IA]
            y4 = x_raw[indxz][used_chnls.IB]
            y5 = x_raw[indxz][used_chnls.IC]
            y6 = x_raw[indxz][used_chnls.IN]
            if SCALED_RMS is True:
                y3 = x[indxz][used_chnls.IA]
                y4 = x[indxz][used_chnls.IB]
                y5 = x[indxz][used_chnls.IC]
                y6 = x[indxz][used_chnls.IN]
            p2.line(x1,y3,color = 'red')
            p2.line(x1,y4,color = 'blue')
            p2.line(x1,y5,color = 'green')
            p2.line(x1,y6,color = 'brown')

            #IEVEN
            y14 = x_raw[indxz][used_chnls.IA_EVENS]
            y15 = x_raw[indxz][used_chnls.IB_EVENS]
            y16 = x_raw[indxz][used_chnls.IC_EVENS]
            y17 = x_raw[indxz][used_chnls.IN_EVENS]
            if SCALED_RMS is True:
                y14 = x_raw[indxz][used_chnls.IA_EVENS]
                y15 = x_raw[indxz][used_chnls.IB_EVENS]
                y16 = x_raw[indxz][used_chnls.IC_EVENS]
                y17 = x_raw[indxz][used_chnls.IN_EVENS]
            
            p3.line(x1,y14,color = 'red')
            p3.line(x1,y15,color = 'blue')
            p3.line(x1,y16,color = 'green')
            p3.line(x1,y17,color = 'brown')
            
            #INONs
            y24 = x_raw[indxz][used_chnls.IA_NONS]
            y25 = x_raw[indxz][used_chnls.IB_NONS]
            y26 = x_raw[indxz][used_chnls.IC_NONS]
            y27 = x_raw[indxz][used_chnls.IN_NONS]
            if SCALED_RMS is True:
                y24 = x_raw[indxz][used_chnls.IA_NONS]
                y25 = x_raw[indxz][used_chnls.IB_NONS]
                y26 = x_raw[indxz][used_chnls.IC_NONS]
                y27 = x_raw[indxz][used_chnls.IN_NONS]
            
            p4.line(x1,y24,color = 'red')
            p4.line(x1,y25,color = 'blue')
            p4.line(x1,y26,color = 'green')
            p4.line(x1,y27,color = 'brown')

            #PA_PB_PC
            max_a = max(abs(x_raw[indxz][used_chnls.PA]))
            max_b = max(abs(x_raw[indxz][used_chnls.PB]))
            max_c = max(abs(x_raw[indxz][used_chnls.PC]))
            max_all = max(max_a,max_b,max_c)
            print('Max all val '+str(max_all))

            if max_all >=1000000:
                metric  = 'Mwatts'
                y18 = x_raw[indxz][used_chnls.PA]/1000000
                y19 = x_raw[indxz][used_chnls.PB]/1000000
                y20 = x_raw[indxz][used_chnls.PC]/1000000
            else:
                metric  = 'Kwatts'
                y18 = x_raw[indxz][used_chnls.PA]/1000
                y19 = x_raw[indxz][used_chnls.PB]/1000
                y20 = x_raw[indxz][used_chnls.PC]/1000
            if SCALED_RMS is True:
                y18 = x[indxz][used_chnls.PA]
                y19 = x[indxz][used_chnls.PB]
                y20 = x[indxz][used_chnls.PC]
            p5.line(x1,y18,color = 'red')
            p5.line(x1,y19,color = 'blue')
            p5.line(x1,y20,color = 'green')
            
            #QA_QB_QC
            max_aa = max(abs(x_raw[indxz][used_chnls.QA]))
            max_bb = max(abs(x_raw[indxz][used_chnls.QB]))
            max_cc = max(abs(x_raw[indxz][used_chnls.QC]))
            max_all_abc = max(max_aa,max_bb,max_cc)
            print('Max all val '+str(max_all_abc))

            if max_all_abc >=1000000:
                metric_q  = 'Mvars'
                y21 = x_raw[indxz][used_chnls.QA]/1000000
                y22 = x_raw[indxz][used_chnls.QB]/1000000
                y23 = x_raw[indxz][used_chnls.QC]/1000000
            else:
                metric_q = 'Kvars'
                y21 = x_raw[indxz][used_chnls.QA]/1000
                y22 = x_raw[indxz][used_chnls.QB]/1000
                y23 = x_raw[indxz][used_chnls.QC]/1000

            # y29 = x_raw[indx,:,21]
            # y30 = x_raw[indx,:,22]
            # y31 = x_raw[indx,:,23]
            if SCALED_RMS is True:
                y21 = x[indxz][used_chnls.QA]
                y22 = x[indxz][used_chnls.QB]
                y23 = x[indxz][used_chnls.QC]
            p6.line(x1,y21,color = 'red')
            p6.line(x1,y22,color = 'blue')
            p6.line(x1,y23,color = 'green')

            col1, col2,col3  = st.columns(3)
            col4,col5,col6 = st.columns(3)

            with col1:
                st.write('Voltage')
                st.bokeh_chart(p1, use_container_width=False,)
        
            with col2:
                if SCALED_RMS is not True:
                    st.write('Real Power in '+ str(metric))
                    st.bokeh_chart(p5, use_container_width=False)
                else:
                    st.write('Real Power')
                    st.bokeh_chart(p5, use_container_width=False)
            
            with col3:
                st.write('Current Even')
                st.bokeh_chart(p3, use_container_width=False)
            
            with col4:
                st.write('Current')
                st.bokeh_chart(p2, use_container_width=False)
            
            with col5:
                if SCALED_RMS is not True:
                    st.write('Reactive Power in '+ str(metric_q))
                    st.bokeh_chart(p6, use_container_width=False)
                else:
                    st.write('Reactive Power')
                    st.bokeh_chart(p6, use_container_width=False)
            
                
            with col6:
                st.write('Current NONs')
                st.bokeh_chart(p4, use_container_width=False)

            return idx

    
    # Keyboard part
    def capon():
        st.write('Previously: cap on was clicked')
        print('cap on was clicked')
        pred_classification_code = 10110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1        
        
    def capoff():
        st.write('Previously: cap off was clicked')
        print('cap off was clicked')
        pred_classification_code = 10120
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1        
        
    def motstart():
        st.write('Previously: motor start was clicked')
        print('motor start was clicked')
        pred_classification_code = 12110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1        
        

    def inrush():
        st.write('Previously: inrush was clicked')
        print('inrush was clicked')
        pred_classification_code = 13170
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1        
        
    def oc():
        st.write('Previously: oc was clicked')
        print('oc was clicked')
        pred_classification_code = 15110
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1        
        
    def ods():
        st.write('Previously: other downstream was clicked')
        print('ods was clicked')
        pred_classification_code = 66666
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1
    def nds():
        st.write('Previously: Not downstream was clicked')
        print('nds was clicked')
        pred_classification_code = 77777
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1
    def unk():
        st.write('Previously: Unknown was clicked')
        print('unk was clicked')
        pred_classification_code = 88888
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1
    def noth():
        st.write('Previously: Nothing was clicked')
        print('noth was clicked')
        pred_classification_code = 99999
        print('new_pred = '+str(pred_classification_code))
        change.change_df(x = pred_classification_code,idx = st.session_state.cnt )
        st.session_state.cnt = st.session_state.cnt+1
    def check_box():
        st.write('Check required later')
        print('check clicked')
        req_check = 'True'
        change_check.change_df_check(x = req_check,idx = st.session_state.cnt )
    def uncheck_box():
        st.write('Check required later')
        print('check clicked')
        req_check = ' '
        change_check.change_df_check(x = req_check,idx = st.session_state.count )

    # Button Init
    left_col, right_col= st.columns(2)
    with right_col:
        if st.session_state.cnt != len(x):
            next_btn = st.button('Next RMS ->')
        else:
            next_btn = st.button('Next RMS ->',disabled=True)
    with left_col:
        if st.session_state.cnt == 0:
            prev_button = st.button('<- Previous RMS', disabled=True)
        else:
            prev_button = st.button('<- Previous RMS')
    
   
    one,two,three,four,five,six,seven,eight,nine= st.columns(9)
    with one:
        c1 = st.button('1. 10110: Capacitor on')
    with two:
        c2 = st.button('2. 10120: Capacitor off')
    with three:
        c3 = st.button('3. 12110: Motor start')
    with four:
        c4 = st.button('4. 13170: Inrush')
    with five:
        c5 = st.button('5. 15110: OC normal')

    with six:
        c6 = st.button('6. 66666: Other Downstream')
    with seven:
        c7 = st.button('7. 77777: Not downstream')
    with eight:
        c8 = st.button('8. 88888: Unknown')
    with nine:
        c9 = st.button('9. 99999: Nothing')


    if c1:
        capon()
    elif c2:
        capoff()
    elif c3:
        motstart()
    elif c4:
        inrush()
    elif c5:
        oc() 

    elif c6:
        ods()
    elif c7:
        nds()
    elif c8:
        unk()
    elif c9:
        noth()

    if next_btn is False and prev_button is False and st.session_state.cnt == 0:
        # st.session_state.count = int(line)
        # idx =  first_page(idx = main_file.index[0])

        st.session_state.cnt = int(line_ne)
        idx =  first_page(idx = int(line_ne))
    elif next_btn is False and prev_button is False and st.session_state.cnt != 0:
        # indxy = radio_change1()
        print('indixy')
        idx = first_page(idx = st.session_state.cnt)

    elif prev_button is True and next_btn is False:
        try:
            st.session_state.cnt -= 1
            idx =  first_page(idx = st.session_state.cnt)
        except:
            Continue
        

    elif next_btn is True and prev_button is False:
        try:
            st.session_state.cnt += 1
            idx =  first_page(idx = st.session_state.cnt)
        except:
            Continue

    with open('current_index_not_edited.txt', 'w') as f:
        f.write(str(st.session_state.cnt))
        f.close()

    st.text("* NOTE - Index are reset, Don't refer indices from this page!!")
    components.html(
        """
    <script>
    const doc = window.parent.document;
    buttons = Array.from(doc.querySelectorAll('button[kind=primary]'));
    const next_button = buttons.find(el => el.innerText === 'Next RMS ->');
    const prev_button = buttons.find(el => el.innerText === '<- Previous RMS');

    const c1_button = buttons.find(el => el.innerText === '1. 10110: Capacitor on');
    const c2_button = buttons.find(el => el.innerText === '2. 10120: Capacitor off');
    const c3_button = buttons.find(el => el.innerText === '3. 12110: Motor start');
    const c4_button = buttons.find(el => el.innerText === '4. 13170: Inrush');
    const c5_button = buttons.find(el => el.innerText === '5. 15110: OC normal');

    const c6_button = buttons.find(el => el.innerText === '6. 66666: Other Downstream');
    const c7_button = buttons.find(el => el.innerText === '7. 77777: Not downstream');
    const c8_button = buttons.find(el => el.innerText === '8. 88888: Unknown');
    const c9_button = buttons.find(el => el.innerText === '9. 99999: Nothing');
    
    checks = Array.from(doc.querySelectorAll('label[data-baseweb=checkbox]'));
    const check = checks.find(el => el.innerText === 'Require check');

    doc.addEventListener('keydown', function(e) {
        switch (e.keyCode) {
            case 13: // (13 = enter)
                next_button.click();
                break;
            case 8: // (8 = back space)
                prev_button.click();
                break;
            case 37: // (37 = Left Arrow)
                
                prev_button.click();
                break;
            case 39: // (39 = Right arrow)
                next_button.click();
                break;


            case 49: // (49 = num 1)
                c1_button.click();
                break;
            case 50: // (50 = num 2)
                c2_button.click();
                break;
            case 51: // (51 = num 3)
                c3_button.click();
                break;
            case 52: // (52 = num 4)
                c4_button.click();
                break;
            case 53: // (53 = num 5)
                c5_button.click();
                break;

            case 54: //(54 = num6)
                c6_button.click();
                break;
            case 55: //(55 = num7)
                c7_button.click();
                break;
            case 56: //(56 = num8)
                c8_button.click();
                break;
            case 57: //(57 = num9)
                c9_button.click();
                break;
            case 83: //(83 = char s)
                
                check.click();
                alert()
                break;
        }
    });
    </script>
    """,
        height=0,
        width=0,
    )
elif navigation_tab == 'False +ve/-ve':
    st.header('False Positives and Negatives')
    
    main_file_verify = pd.read_csv("csv/"+db+'.csv',sep = ',')#main_file_error_v6_windx_77k_edit_col.csv
    x_arr  = np.load("npy/"+db+"_raw.npy",allow_pickle=True)
    
    
    vals={'Capacitor on':10110,'Capacitor off':10120,'Motor start':12110,'Inrush':13170,'OC normal':15110,'Other Downstream':66666,'Not downstream':77777,'Unknown':88888,'Nothing':99999}
    
    val_list = ['Capacitor on',
      'Capacitor off',
       'Motor start',
       'Inrush',
       'OC normal',
       'Other Downstream',
       'Not downstream',
       'Unknown',
       'Nothing'
       ]
    left_col, right_col= st.columns(2)
    with left_col:
        option1 = st.selectbox('Select the True classification code',val_list,key='a')
    option2_list = []  
    for i in val_list:
        if i != option1:
            option2_list.append(i)
    with right_col:
        option2 = st.selectbox('Select the predicted classification code',option2_list,key='b')
    
    selection1 = vals[option1]
    print(selection1)
    selection2 = vals[option2]
    print(selection2)

    print('sel-1 '+ str(selection1)+'-------'+'sel-2 '+ str(selection2))
    
    selected_df = main_file_verify[(main_file_verify.classification_codes ==selection1) & (main_file_verify.predictions ==selection2)]
    # print(selected_df)
    print(len(selected_df))
    total_size = len(selected_df)
    st.text(" Total number of entries "+str(total_size))

    
    col_1, col_2,col_3,col_4  = st.columns(4)
    
    # with col_1:
        # src1 = 
        # for idx in selected_df.index[0:51] :
    for idx in selected_df.index[:total_size]:
        
        # print(idx)
        # print(selected_df[selected_df.indx==indx1]['file_name'])
        x1 = [i for i in range(0,len(x_arr[idx][0]))]
        p1 = figure(plot_width=450,plot_height=100)
        p2 = figure(plot_width=450,plot_height=100)
        p5 = figure(plot_width=450,plot_height=100)
        p6 = figure(plot_width=450,plot_height=100)

        #VA_VB_VC
        y1 = x_arr[idx][used_chnls.VA]
        y2 = x_arr[idx][used_chnls.VB]
        y3 = x_arr[idx][used_chnls.VC]  
        
        p1.line(x1,y1,color = 'red')
        p1.line(x1,y2,color = 'blue')
        p1.line(x1,y3,color = 'green')

        #IA_IB_IC
        y5 = x_arr[idx][used_chnls.IA]
        y6 = x_arr[idx][used_chnls.IB]
        y7 = x_arr[idx][used_chnls.IC]
        y8 = x_arr[idx][used_chnls.IN]
        p2.line(x1,y5,color = 'red')
        p2.line(x1,y6,color = 'blue')
        p2.line(x1,y7,color = 'green')
        p2.line(x1,y8,color = 'brown')

        #PA_PB_PC
        
        # y25 = x_arr[idx,:,18]
        # y26 = x_arr[idx,:,19]
        # y27 = x_arr[idx,:,20]

        # p5.line(x1,y25,color = 'red')
        # p5.line(x1,y26,color = 'blue')
        # p5.line(x1,y27,color = 'green')
        

        max_a = max(abs(x_arr[idx][used_chnls.PA]))
        max_b = max(abs(x_arr[idx][used_chnls.PB]))
        max_c = max(abs(x_arr[idx][used_chnls.PC]))
        max_all = max(max_a,max_b,max_c)
        print('Max all val '+str(max_all))

        if max_all >=1000000:
            metric  = 'Mwatts'
            y25 = x_arr[idx][used_chnls.PA]/1000000
            y26 = x_arr[idx][used_chnls.PB]/1000000
            y27 = x_arr[idx][used_chnls.PC]/1000000
        else:
            metric  = 'Kwatts'
            y25 = x_arr[idx][used_chnls.PA]/1000
            y26 = x_arr[idx][used_chnls.PB]/1000
            y27 = x_arr[idx][used_chnls.PC]/1000
        
        p5.line(x1,y25,color = 'red')
        p5.line(x1,y26,color = 'blue')
        p5.line(x1,y27,color = 'green')
        #QA_QB_QC
        
        # y29 = x_arr[idx,:,21]
        # y30 = x_arr[idx,:,22]
        # y31 = x_arr[idx,:,23]

        max_aa = max(abs(x_arr[idx][used_chnls.QA]))
        max_bb = max(abs(x_arr[idx][used_chnls.QB]))
        max_cc = max(abs(x_arr[idx][used_chnls.QC]))
        max_all_abc = max(max_aa,max_bb,max_cc)
        print('Max all val '+str(max_all_abc))

        if max_all_abc >=1000000:
            metric_q  = 'Mvars'
            y29 = x_arr[idx][used_chnls.QA]/1000000
            y30 = x_arr[idx][used_chnls.QB]/1000000
            y31 = x_arr[idx][used_chnls.QC]/1000000
        else:
            metric_q = 'Kvars'
            y29 = x_arr[idx][used_chnls.QA]/1000
            y30 = x_arr[idx][used_chnls.QB]/1000
            y31 = x_arr[idx][used_chnls.QC]/1000

        p6.line(x1,y29,color = 'red')
        p6.line(x1,y30,color = 'blue')
        p6.line(x1,y31,color = 'green')


        
            ## st.bokeh_chart(gr1, use_container_width=False)
        
        with col_1:
            st.write(str(idx)+'-'+str(selected_df[selected_df.index==idx]['file_names'].iloc[0].split('/')[4]))
            st.write('Voltage')
            st.bokeh_chart(p1, use_container_width=False)
        with col_2:
            f_name = str(selected_df['file_names'][idx].split('/')[4])
            if f_name[0]== 'S' or f_name[0]== 'L':
                link = '[File link](https://ce5.dfa.plus/grid/?plot_files='+ str(f_name)+')'
                st.write(link)
            else:
                link = '[File link](https://dfa.plus/grid/?company=plot_only&plot_files='+ str(f_name)+')'
                st.write(link)
            # st.write(link)
            # st.text('')
            st.write('Current')
            st.bokeh_chart(p2, use_container_width=False)
        with col_3:
            st.write(str(idx)+'-'+str(selected_df[selected_df.index==idx]['file_names'].iloc[0].split('/')[4]))
            st.write('Real Power in '+str(metric))
            st.bokeh_chart(p5, use_container_width=False)
        with col_4:
            st.write(str(idx)+'-'+str(selected_df[selected_df.index==idx]['file_names'].iloc[0].split('/')[4]))
            st.write('Reactive Power in '+str(metric_q))
            st.bokeh_chart(p6, use_container_width=False)