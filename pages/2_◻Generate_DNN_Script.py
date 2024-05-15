import pandas as pd
import numpy as np
import openpyxl as xl
import datetime
import json
import streamlit as st
import re

st.set_page_config(layout='wide')
st.header("DNN Script")
col_dnn_pnf =["Index","NF Instance ID","Data Network Name","PNFNS Index","PDU Session Type","Priority Switch","Priority","Capacity Switch","Capacity"]

f_tb_dnn_index = "../NW_src_pkg/tb_ns_index/tb_dnn_index.txt"
dict_upf ={"UPFTL2H":"3d5a0697-2a3c-43bc-7d7e-0425592b5489","UPFSLA1H":"a5d0c813-f5a7-4510-b97a-9ee506b3a794","UPFPTY1H":"9383a6b0-add1-4211-8b17-3ecbbefb6fdf"}
df_ns = pd.read_csv('../NW_src_pkg/tb_ns_index/tb_ns.csv',index_col=0)
df_dnn_idex = pd.read_csv(f_tb_dnn_index)
# df_dnn_idex['Index'] = df_dnn_idex['Index'].astype(str)


col1,col2 = st.columns(2)
with col1:
    st.text_input("Enter DNN name",key="dnn")
    dnn = st.session_state.dnn

with col2:
    st.text_input("Enter UE IP",key="ue_ip")
    ue_ip = st.session_state.ue_ip

col1,col2 = st.columns(2)
with col1:
    list_vpn = ["VPN_N6_IPCBB","VPN_N6_IPCBB_5GMEC"]
    st.selectbox("Choose common VPN",list_vpn,index=None,key="comm_vpn")
    comm_vpn = st.session_state.comm_vpn


with col2:
    if st.session_state.comm_vpn:
        dedicated_vpn = st.text_input("Enter New VPN name",key="dedicated_vpn",disabled=True)
        dedi_vpn = st.session_state.dedicated_vpn
    else:
        dedicated_vpn = st.text_input("Enter New VPN name", key="dedicated_vpn", disabled=False)
        dedi_vpn = st.session_state.dedicated_vpn



col1,col2,col3,col4 = st.columns(4)
with col1:
    st.radio("Select active UPF",dict_upf, key="upf_act",index=0)
    upf_act = st.session_state.upf_act

with col2:
    st.radio("Select standby UPF",dict_upf, key="upf_std",index=0)
    upf_std = st.session_state.upf_std
with col3:
    charging = st.radio("Select charging mode", ("offline", "online"), key="chf_mode")
    gbr_mode = st.checkbox("GBR(N7)", key="gbr_mode")
with col4:
    nssai = st.selectbox('Select slicing ID',options=(df_ns["SNSSAI"].drop_duplicates()),key='nssai',index=5)
    button = st.button("Create script")



upftls_inst_id = "3d5a0697-2a3c-43bc-7d7e-0425592b5489"
upfsla_inst_id = "a5d0c813-f5a7-4510-b97a-9ee506b3a794"
upfpty_inst_id = "9383a6b0-add1-4211-8b17-3ecbbefb6fdf"

dnn_mec = '^mecng.*'
list_split_dnn_index = []


def normalize_dnn_index(list_dnn_upf_index,df_dnn_idex):
    list_curr_dnn_index = []
    list_chked_dnn_index = []
    assigned_dnn_index = df_dnn_idex['Index']
    for dnn_index in assigned_dnn_index:
        list_curr_dnn_index.append(dnn_index)
    try:
        if list_dnn_upf_index[0] not in list_curr_dnn_index:
            list_chked_dnn_index.append(list_dnn_upf_index[0])

        else:
            rev_index = list_dnn_upf_index[0] + 1
            list_chked_dnn_index.append(rev_index)

        if list_dnn_upf_index[1] not in list_curr_dnn_index:
            list_chked_dnn_index.append(list_dnn_upf_index[1])

        else:
            rev_index = list_dnn_upf_index[1] + 1
            list_chked_dnn_index.append(rev_index)

            # st.write(list_dnn_upf_index)
            if len(list_chked_dnn_index) == 2:
                for id in list_chked_dnn_index:
                    id = str(id)
                    for d in id:
                        list_split_dnn_index.append(d)
                d1 = list_split_dnn_index[1:4]
                d2 = list_split_dnn_index[5:8]
                d1 = ''.join(d1)
                d1 = int(d1)
                d2 = ''.join(d2)
                d2 = int(d2)

                if d1 < d2:
                    diff = d2 - d1
                    list_chked_dnn_index[0] = int(list_chked_dnn_index[0]) + diff

                    return list_chked_dnn_index
                elif d1 > d2:
                    diff = d1 - d2
                    list_chked_dnn_index[1] = int(list_chked_dnn_index[1]) + diff
                    return list_chked_dnn_index
                else:
                    return list_chked_dnn_index
            else:
                return list_chked_dnn_index
    except:
        return list_chked_dnn_index

def q_dnn_index(uut,dnn):
    list_index = []
    for key,inst in df_dnn_idex.iterrows():
        if inst[1] == uut: # uut is active upf instance id
            inst['Index'] = int(inst['Index'])
            if inst[1] == upftls_inst_id:
                if not re.match(dnn_mec, dnn):
                    if inst['Index'] <= 1299:
                        list_index.append(inst['Index'])
                elif 1300 <= inst['Index'] <= 1399:
                    list_index.append(inst['Index'])


            if inst[1] == upfsla_inst_id:
                if not re.match(dnn_mec, dnn):
                    if inst['Index'] <= 2299:
                        list_index.append(inst['Index'])
                elif 2300 <= inst['Index'] <= 2399:
                    list_index.append(inst['Index'])

            if inst[1] == upfpty_inst_id:
                if not re.match(dnn_mec, dnn):
                    if inst['Index'] <= 3199:
                        list_index.append(inst['Index'])
                elif 3300 <= inst['Index'] <= 3399:
                    list_index.append(inst['Index'])


    return list_index

def get_dnn_sl_index(list_inst_act,list_inst_std,dnn_sl_index,dnn):
    # st.write(list_inst_act)
    # st.write(list_inst_std)
    try:
        dict_ns_dnn_act = {}
        dict_ns_dnn_std = {}

        if len(list_inst_act) != 0:
            dict_ns_dnn_act = {"Index": int(dnn_sl_index[0]),
                               "NF Instance ID": list_inst_act[0],
                               "Data Network Name": dnn,
                               "PNFNS Index": list_inst_act[1],
                                "PDU Session Type":"IPV4&IPV6&IPV4V6&UNSTRUCTURED&ETHERNET",
                                "Priority Switch":"SPECIFIC",
                                "Priority":"100",
                                "Capacity Switch":"INHERIT",
                                "Capacity":"0"}

        if len(list_inst_std) != 0:
            dict_ns_dnn_std = {"Index": int(dnn_sl_index[1]),
                               "NF Instance ID": list_inst_std[0],
                               "Data Network Name": dnn,
                               "PNFNS Index": list_inst_std[1],
                                "PDU Session Type":"IPV4&IPV6&IPV4V6&UNSTRUCTURED&ETHERNET",
                                "Priority Switch":"SPECIFIC",
                                "Priority":"200",
                                "Capacity Switch":"INHERIT",
                                "Capacity":"0"}

        return dict_ns_dnn_act,dict_ns_dnn_std

    except:
        st.write('Slice does not exist')

def create_script(dnn_pnf_a,dnn_pnf_s):
    df_dnn_pnf_act = pd.DataFrame(dnn_pnf_a.values())
    df_dnn_pnf_std = pd.DataFrame(dnn_pnf_s.values())
    df_dnn_pnf_act = df_dnn_pnf_act
    df_dnn_pnf_std = df_dnn_pnf_std
    df_dnn_pnf_act = df_dnn_pnf_act.T
    df_dnn_pnf_std = df_dnn_pnf_std.T
    df_dnn = pd.concat([df_dnn_pnf_act, df_dnn_pnf_std], ignore_index=True)
    df_dnn.columns = col_dnn_pnf  # add col in Data frame
    df_dnn_pnf = pd.concat([df_dnn_idex, df_dnn], ignore_index=True)
    df = df_dnn_pnf.sort_values('Index', ascending=True)
    return df

def set_gbr(gbr_mode):
    if gbr_mode:
        mode = 'ENABLE'
    else:
        mode= 'DISABLE'
    return mode

def set_charging(charging):
    if charging == 'online':
        charg_mode = 'ENABLE'
    else:
        charg_mode= 'DISABLE'
    return charg_mode

def wr_dnn_script(ns_index,vpn,index_upf_act,index_upf_std,new_dnn,upf_inst_act,upf_pri_act,pnf_ns_act,
                  upf_inst_std,pnf_ns_std,upf_pri_std,gbr,chf,upf_act,upf_std):
    dnn_script =('''//////////////////SMFTL21H-SLA1H//////////////////////////
ADD NSDNN:NSIDX={ns_index},DNN="{new_dnn}";
ADD APN: APN="{new_dnn}",VIRTUALAPN=DISABLE;
ADD APNUSRPROFG: APN="{new_dnn}", USERPROFGNAME="rbng-internet-corp";
SET APNPCCFUNC: APN="{new_dnn}", HOMEPCCSWITCH={gbr}, ROAMPCCSWITCH={gbr}, VISITPCCSWITCH={gbr},PCCTEMPLATE="pcc-avatar",PCFSELECTMODE=DNN-0&GPSI-0&IMSI-1&NFLOC-0&PLMN-0&SERVINGSCOPE-0&SNSSAIS-0;
SET APNCHARGECTRL: APN="{new_dnn}", CONVERGEDSW={chf}, CCTEMPLATE="offline-avatar";
SET UEDNSBINDAPN: APN="{new_dnn}", MDNSSERVERV4="115.178.58.10",BDNSSERVERV4="115.178.58.26";
SET UEDNSBINDAPN: APN="{new_dnn}", MDNSSERVERV4="115.178.58.26",BDNSSERVERV4="115.178.58.10";
SET APNRDSACCTCTRL: APN="{new_dnn}", SUPPORTACCTRSP=DISABLE, DEACTIVE=CONTINUE;
SET APNACCESSCTRL:APN="{new_dnn}",SELECTMODECHECK=ENABLE,SMFSELMODECHECK=ENABLE,SELECTMODEMS=DISABLE,SELECTMODEMSNET=ENABLE,SELECTMODENET=DISABLE;
SET APNQOSATTR: APN="{new_dnn}", HASQOSPROFILE=ENABLE, QOSPROFILENAME="default-qos";
SET APNUPSELPLY: APN="{new_dnn}", COMBINEPRISTG=COMBINEFIRST, COMBINEDSELSTG=APNPRI;
ADD PNFDNN: INDEX={index_upf_act}, NFINSTANCEID="{upf_inst_act}", DNN="{new_dnn}",PNFNSINDEX={pnf_ns_act}, PRISWITCH=SPECIFIC, PRIORITY={upf_pri_act};
ADD PNFDNN: INDEX={index_upf_std}, NFINSTANCEID="{upf_inst_std}", DNN="{new_dnn}",PNFNSINDEX={pnf_ns_std}, PRISWITCH=SPECIFIC, PRIORITY={upf_pri_std};

////////////////////////{upf_act}-{upf_std}_APN //////////////////////////
ADD APN:APN="{new_dnn}",HASVPN=ENABLE,VPNINSTANCE="{vpn}",HASVPNIPV6=ENABLE,VPNINSTANCEIPV6="{vpn}";
ADD POOL:POOLNAME="pool_{new_dnn}",POOLTYPE=EXTERNAL,IPVERSION=IPV4,HASVPN=ENABLE,VPNINSTANCE="{vpn}";
ADD SECTION:POOLNAME="pool_{new_dnn}",SECTIONNUM=0,IPVERSION=IPV4,V4STARTIP="10.179.6.0",V4ENDIP="10.179.6.127";
ADD POOLGROUP:POOLGRPNAME="poolgroup_{new_dnn}",IPV4ALLOCPRIALG=ENABLE,IPV6ALLOCPRIALG=DISABLE;
ADD POOLBINDGROUP:POOLGROUPNAME="poolgroup_{new_dnn}",POOLNAME="pool_{new_dnn}",PRIORITY=16;
ADD POOLGRPMAP:MAPPINGNAME="mapping_{new_dnn}",APN="{new_dnn}",POOLGROUPNAME="poolgroup_{new_dnn}";
SET APNUEMUTACC: APN="{new_dnn}", INNERAPNS=DISABLE, INTERAPNS=ENABLE;


//////////////////////////4GDNS///////////////////////////////
ADD RESREC: TYPE=NAPTR, ZONE="APN.EPC.MNC003.MCC520.3GPPNETWORK.ORG", DOMAIN="{new_dnn}", ORDER=100, PREF=100, FLAGS=A, SERVICE="x-3gpp-pgw:x-s5-gtp+nc-smf", REPLACEMENT="SMFTL21H.SMF.NODE.5GC.MNC003.MCC520.3GPPNETWORK.ORG.", VIEWNAME="local";
ADD RESREC: TYPE=NAPTR, ZONE="APN.EPC.MNC003.MCC520.3GPPNETWORK.ORG", DOMAIN="{new_dnn}", ORDER=100, PREF=100, FLAGS=A, SERVICE="x-3gpp-pgw:x-s5-gtp+nc-smf", REPLACEMENT="SMFSLA1H.SMF.NODE.5GC.MNC003.MCC520.3GPPNETWORK.ORG.", VIEWNAME="local";
ADD RESREC: TYPE=NAPTR, ZONE="APN.EPC.MNC003.MCC520.3GPPNETWORK.ORG", DOMAIN="{new_dnn}", ORDER=100, PREF=100, FLAGS=A, SERVICE="x-3gpp-pgw:x-s5-gtp+nc-nr", REPLACEMENT="SMFTL21H.SMF.NODE.5GC.MNC003.MCC520.3GPPNETWORK.ORG.", VIEWNAME="local";
ADD RESREC: TYPE=NAPTR, ZONE="APN.EPC.MNC003.MCC520.3GPPNETWORK.ORG", DOMAIN="{new_dnn}", ORDER=100, PREF=100, FLAGS=A, SERVICE="x-3gpp-pgw:x-s5-gtp+nc-nr", REPLACEMENT="SMFSLA1H.SMF.NODE.5GC.MNC003.MCC520.3GPPNETWORK.ORG.", VIEWNAME="local";
ADD RESREC: TYPE=NAPTR, ZONE="APN.EPC.MNC003.MCC520.3GPPNETWORK.ORG", DOMAIN="{new_dnn}", ORDER=100, PREF=100, FLAGS=A, SERVICE="x-3gpp-pgw:x-s5-gtp:x-s8-gtp:x-gn:x-gp", REPLACEMENT="SMFTL21H.SMF.NODE.5GC.MNC003.MCC520.3GPPNETWORK.ORG.", VIEWNAME="local";
ADD RESREC: TYPE=NAPTR, ZONE="APN.EPC.MNC003.MCC520.3GPPNETWORK.ORG", DOMAIN="{new_dnn}", ORDER=100, PREF=100, FLAGS=A, SERVICE="x-3gpp-pgw:x-s5-gtp:x-s8-gtp:x-gn:x-gp", REPLACEMENT="SMFSLA1H.SMF.NODE.5GC.MNC003.MCC520.3GPPNETWORK.ORG.", VIEWNAME="local";
    
    
    
    
    
    '''.format(ns_index=ns_index,vpn=vpn,index_upf_act=index_upf_act,index_upf_std=index_upf_std,new_dnn=new_dnn,upf_inst_act=upf_inst_act,upf_inst_std=upf_inst_std,
               pnf_ns_act=pnf_ns_act,pnf_ns_std=pnf_ns_std,upf_pri_act=upf_pri_act,upf_pri_std=upf_pri_std,gbr=gbr,chf=chf,upf_act=upf_act,upf_std=upf_std))

    return dnn_script

if __name__ == '__main__':
    # st.write(df_ns)
    new_dnn = dnn
    ns_idex = []  # list of NS_INDEX
    dict_instance_id = {}
    for index,row in df_ns.iterrows():
        if row[0] == nssai:
            ns_idex.append(index)
            dict_instance_id[row[2]] = row[1]  # add dict between instance index and instance id

    list_existing_slice_act = []
    list_existing_slice_std = []
    list_dnn_index = []
    list_dnn_index_nor = []
    list_inst_act = []
    list_pnf_act = []
    list_dnn_pnf_act = []
    list_inst_std = []
    list_pnf_std = []
    list_dnn_pnf_std = []
    list_new_dnn_upf_index_std = []
    list_dnn_upf_index_act = []
    list_dnn_upf_index_std= []

    if upf_act != upf_std:
        st.write("NS INDEX:", str(ns_idex[0]))
        for key, inst in dict_upf.items():
            if key == upf_act:
                for i,uut in dict_instance_id.items(): # i is sl_index of upf
                    if uut == inst:
                        list_existing_slice_act.append(i)

                        list_inst_act.append(uut)
                        list_pnf_act.append(i)
                        dnn_index_act = q_dnn_index(uut,new_dnn)
                        list_dnn_pnf_act = list_inst_act + list_pnf_act
                        list_dnn_upf_index_act.append(dnn_index_act[-1]) # select last value of slice id dnn   lastest dnn index
                        list_dnn_upf_index_act = list_dnn_upf_index_act[-1] + 1

                if len(list_existing_slice_act) == 0:
                    st.warning(f"Slice-id does not exist in active site: {key}")

            if key == upf_std:

                for i,uut in dict_instance_id.items():  #i is nsid of upf
                    if uut == inst:
                        list_existing_slice_std.append(i)
                        list_inst_std.append(uut)
                        list_pnf_std.append(i)
                        dnn_index_std = q_dnn_index(uut,new_dnn)
                        list_dnn_pnf_std = list_inst_std + list_pnf_std
                        list_dnn_upf_index_std.append(dnn_index_std[-1]) # select last value of slice id dnn
                        list_new_dnn_upf_index_std = list_dnn_upf_index_std[-1] + 1


                if len(list_existing_slice_std) == 0:
                    st.warning(f"Slice-id does not exist in standby site: {key}")

        list_dnn_upf_index = [list_dnn_upf_index_act] + list_dnn_upf_index_std
        dnn_index_normaliztion = normalize_dnn_index(list_dnn_upf_index,df_dnn_idex)
        dnn_pnf = get_dnn_sl_index(list_dnn_pnf_act,list_dnn_pnf_std,dnn_index_normaliztion,dnn)

        ns_index = ns_idex[0]
        new_dnn = dnn_pnf[0]['Data Network Name']
        index_upf_act = dnn_pnf[0]['Index']
        upf_inst_act = dnn_pnf[0]['NF Instance ID']
        pnf_ns_act = dnn_pnf[0]['PNFNS Index']
        upf_pri_act = dnn_pnf[0]['Priority']
        index_upf_std = dnn_pnf[1]['Index']
        upf_inst_std = dnn_pnf[1]['NF Instance ID']
        pnf_ns_std = dnn_pnf[1]['PNFNS Index']
        upf_pri_std = dnn_pnf[1]['Priority']


        col1,col2 = st.columns(2)
        with col1:
            st.write(f"PNF DNN: {upf_act}",dnn_pnf[0])

        with col2:
            st.write(f"PNF DNN: {upf_std}", dnn_pnf[1])

        gbr = set_gbr(gbr_mode)
        chf = set_charging(charging)
        # if button:
        if st.session_state.get('button') != True:
            st.session_state['button'] = button
        if st.session_state['button'] == True:
            if st.session_state.dnn:
                current_dnn = df_dnn_idex['Data Network Name']
                list_dnn = []
                vpn = ''
                for chk_dnn in current_dnn:
                   list_dnn.append(chk_dnn)
                if dnn not in list_dnn:
                    if st.session_state.comm_vpn and not st.session_state.dedicated_vpn:
                        s = create_script(dnn_pnf[0], dnn_pnf[1])
                        d = s.to_csv(f_tb_dnn_index, index=False)
                        vpn = comm_vpn
                        dnn_script = wr_dnn_script(ns_index, vpn, index_upf_act, index_upf_std, new_dnn, upf_inst_act,
                                                   upf_pri_act, pnf_ns_act, upf_inst_std, pnf_ns_std, upf_pri_std,gbr,chf,upf_act,upf_std)
                        st.write(dnn_script)
                    elif st.session_state.dedicated_vpn and not st.session_state.comm_vpn:
                        s = create_script(dnn_pnf[0], dnn_pnf[1])
                        d = s.to_csv(f_tb_dnn_index, index=False)
                        vpn = dedi_vpn
                        dnn_script = wr_dnn_script(ns_index, vpn, index_upf_act, index_upf_std, new_dnn, upf_inst_act,
                                                   upf_pri_act, pnf_ns_act, upf_inst_std, pnf_ns_std, upf_pri_std,gbr,chf,upf_act,upf_std)
                        st.write(dnn_script)
                    elif st.session_state.dedicated_vpn and st.session_state.comm_vpn:
                        st.error('Please choose one VPN name only')
                    else:
                        st.warning("Please enter VPN name")
                else:

                    st.error('The DNN already exist. Please remove it before re-creating the script ')
                    rmv = st.button('Remove')
                    if rmv:
                        st.session_state['button'] = False
                        for k, r in df_dnn_idex.iterrows():
                            if new_dnn == r['Data Network Name']:
                                df_dnn_idex = df_dnn_idex.drop(k)
                                df = df_dnn_idex.to_csv(f_tb_dnn_index, index=False)
                                st.write('Removed successfully')



            else:
                st.error('Please enter DNN')
    else:
        st.warning("Active and standby UPF should not be the same")





