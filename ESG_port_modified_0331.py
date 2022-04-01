# -*- coding: utf-8 -*-
"""

ESG score Exclude incomplete data changing term
March 31st 2022

"""

import pandas as pd
import numpy as np

e_path="C:/NCSU/Spring2022/ESG/PythonData/Data/ESG_score.csv"
s_path="C:/NCSU/Spring2022/ESG/PythonData/Data/Stock_CSV_n.csv"
m_path="C:/NCSU/Spring2022/ESG/PythonData/Data/cur_mkt_cap_esg.csv"
out_path="C:/NCSU/Spring2022/ESG/PythonData/tmp/"

#ESG data
esg=pd.read_csv(e_path)
esg=esg.dropna()
esg['period']=esg['period'].str[:4]
esg=esg.sort_values('period')
period=esg['period'].drop_duplicates()


#Stock data
stock=pd.read_csv(s_path)
col=stock.columns
col=col.to_list()
del col[0]

stock=stock.dropna(how='all',subset=col)
stock['period']=stock['DATES'].str[:4]
stock['DATES']=pd.to_datetime(stock['DATES'])
nofna=stock.isnull().sum(axis=1)
naratio=nofna/len(stock.columns)
stock['na']=naratio
stock=stock[stock['na']<=0.9]

stock=stock.dropna(how='any',axis=1)


#marlet cap
mkp_t=pd.read_csv(m_path)
mcol=mkp_t.columns
mcol=mcol.tolist()
del mcol[0]

mkp=stock['DATES']
mkp_t['DATES']=pd.to_datetime(mkp_t['DATES'])
mkp=pd.merge(mkp,mkp_t,on='DATES')

i=0
ratio=0.1
for i in range(len(period)-1):

    tmp=esg[esg['period']==period.iat[i]]
    tmp=pd.concat([tmp,tmp['esg_disc'].rank(pct=True,method='min')],axis=1)
    tmp.columns=['name','esg_disc','period','percent']
   
    sd=pd.to_datetime(period.iat[i]+'-07-31')
    ed=pd.to_datetime(period.iat[i+1]+'-07-31')
    stock_tmp=stock[stock['DATES']>=sd]
    stock_tmp=stock_tmp[stock_tmp['DATES']<=ed].reset_index(drop=True)
    stock_tmp=stock_tmp.dropna(how='any',subset=[1],axis=1).reset_index(drop=True)
    sn=set(stock_tmp.columns)
    tn=set(tmp['name'])
    common=sn&tn
    
    tmp=tmp[tmp['name'].isin(common)]
    
    tmp_t=tmp.loc[tmp['percent']>=0.9]
    
  
    ycol=tmp_t['name']
    ycol=ycol.to_list()
      
   #selecting stocks
    stock_tmp=stock[ycol]
    stock_tmp=stock_tmp.interpolate('ffill')
    stock_tmp.insert(loc=0,column='DATES',value=stock['DATES'])
    stock_p=stock_tmp #use it later
    stock_tmp=stock[stock['DATES']>=sd]
    stock_tmp=stock_tmp[stock_tmp['DATES']<=ed].reset_index(drop=True)
    stock_tmp=stock_tmp.reset_index(drop=True)
   
   
    
    #market cap top
    mkp_tmp=mkp[ycol]
    mkp_tmp=mkp_tmp.interpolate('ffill')
    mkp_tmp.insert(loc=0,column='DATES',value=mkp['DATES'])
    mkp_tmp=mkp[mkp['DATES']>=sd]
    mkp_tmp=mkp_tmp[mkp_tmp['DATES']<=ed].reset_index(drop=True)
    mkp_tmp[:]=mkp_tmp.loc[0]
    
    mkp_tmp.to_csv(out_path+'test/mkp_base_'+period.iat[i]+'.csv',index=False)

    
    #calc weight
    rsum=mkp_tmp.sum(axis=1)
    mkp_tmp[ycol]=mkp_tmp[ycol]/(rsum.values.reshape(-1,1))
    mkp_tmp=mkp_tmp.reset_index(drop=True)
    mkp_tmp.to_csv(out_path+'test/mkp_'+period.iat[i]+'.csv',index=False)
    
   # creating portfolio file
    stock_tmp_p=stock_tmp[ycol].pct_change()
    stock_tmp.to_csv(out_path+'test/test_st1_'+period.iat[i]+'.csv',index=False)
    stock_tmp_p.insert(loc=0,column='DATES',value=stock_tmp['DATES'])
    stock_tmp_p.to_csv(out_path+'test/test_st1_'+period.iat[i]+'.csv',index=False)
    
    stock_tmp_p=stock_tmp_p.reset_index(drop=True)
    stock_tmp_p[ycol]=stock_tmp_p[ycol]*mkp_tmp[ycol]
    stock_tmp_p=stock_tmp_p[1:]
    stock_tmp_p.to_csv(out_path+'port_top_'+period.iat[i]+'.csv',index=False)
    
    
   #making port bottom
  
    tmp_b=tmp[tmp['percent']<=0.1]
      
    #tmp_b=tmp.tail(m)
    ycol_b=tmp_b['name']
    ycol_b=ycol_b.to_list()
    stock_tmp_b=stock[ycol_b]
    
    stock_tmp_b=stock_tmp_b.interpolate('ffill')
    stock_tmp_b.insert(loc=0,column='DATES',value=stock['DATES'])
    stock_b=stock_tmp_b #use later
    stock_tmp_b=stock_tmp_b[stock_tmp_b['DATES']>=sd]
    stock_tmp_b=stock_tmp_b[stock_tmp_b['DATES']<=ed].reset_index(drop=True)
    
    stock_tmp_b=stock_tmp_b.reset_index(drop=True)
    
     #market cap bottom
    mkp_tmp_b=mkp[ycol_b]
    mkp_tmp_b=mkp_tmp_b.interpolate('ffill')
    mkp_tmp_b.insert(loc=0,column='DATES',value=mkp['DATES'])
    mkp_tmp_b=mkp_tmp_b[mkp_tmp_b['DATES']>=sd]
    mkp_tmp_b=mkp_tmp_b[mkp_tmp_b['DATES']<=ed]

    
    mkp_tmp_b=mkp_tmp_b.reset_index(drop=True)
    mkp_tmp_b[:]=mkp_tmp_b.loc[0]
    
    #calc weight
    rsum_b=mkp_tmp_b.sum(axis=1)
    mkp_tmp_b[ycol_b]=mkp_tmp_b[ycol_b]/(rsum_b.values.reshape(-1,1))
  
   # creating portfolio file
    stock_tmp_b_p=stock_tmp_b[ycol_b].pct_change()
    stock_tmp_b_p.insert(loc=0,column='DATES',value=stock_tmp_b['DATES'])
    stock_tmp_b=stock_tmp_b.reset_index(drop=True)
    stock_tmp_b_p.to_csv(out_path+'test/test_st2_'+period.iat[i]+'.csv',index=False)
    stock_tmp_b_p[ycol_b]=stock_tmp_b_p[ycol_b]*mkp_tmp_b[ycol_b]
    stock_tmp_b_p=stock_tmp_b_p[1:]
    stock_tmp_b_p.to_csv(out_path+'port_btm_'+period.iat[i]+'.csv',index=False)
    
     #making port buy top, sell bottom
    ycol_c=ycol+ycol_b
    stock_tmp_c=pd.merge(stock_p,stock_b,on='DATES')
    stock_tmp_c=stock_tmp_c.interpolate('ffill')
    stock_tmp_c=stock_tmp_c[stock_tmp_c['DATES']>=sd]
    stock_tmp_c=stock_tmp_c[stock_tmp_c['DATES']<=ed].reset_index(drop=True)
    
   
    
     #market cap buy top sell bottom
    mkp_tmp_c=mkp[ycol_c]
    mkp_tmp_c=mkp_tmp_c.interpolate('ffill')
    mkp_tmp_c.insert(loc=0,column='DATES',value=mkp['DATES'])
    mkp_tmp_c=mkp_tmp_c[mkp_tmp_c['DATES']>=sd]
    mkp_tmp_c=mkp_tmp_c[mkp_tmp_c['DATES']<=ed]
   
    mkp_tmp_c=mkp_tmp_c.reset_index(drop=True)
    mkp_tmp_c[:]=mkp_tmp_c.loc[0]
    
    #calc weight
    rsum_c=mkp_tmp_c.sum(axis=1)
    mkp_tmp_c[ycol_c]=mkp_tmp_c[ycol_c]/(rsum_c.values.reshape(-1,1))
    mkp_tmp_c.to_csv(out_path+'test/mkp_bs_'+period.iat[i]+'.csv',index=False)
    
   # creating portfolio file
    stock_tmp_c_p=stock_tmp_c[ycol_c].pct_change()
    
    stock_tmp_c_p[ycol_b]=stock_tmp_c_p[ycol_b]*(-1)
    
    stock_tmp_c_p.insert(loc=0,column='DATES',value=stock_tmp_c['DATES'])
    stock_tmp_c_p.to_csv(out_path+'test/test_st3_'+period.iat[i]+'.csv',index=False)
    print(i)
    stock_tmp_c_p=stock_tmp_c_p.reset_index(drop=True)
    stock_tmp_c_p[ycol_c]=stock_tmp_c_p[ycol_c]*mkp_tmp_c[ycol_c]
    stock_tmp_c_p=stock_tmp_c_p[1:]
    stock_tmp_c_p.to_csv(out_path+'port_bs_'+period.iat[i]+'.csv',index=False)
 


j=0
port1=pd.DataFrame()
port2=pd.DataFrame()
port3=pd.DataFrame()
for j in range(len(period)-1):
    
    pj=pd.read_csv(out_path+'port_top_'+period.iat[j]+'.csv')
    pj['Top']=pj.sum(axis=1,numeric_only=True)
    df=pj[['DATES','Top']]
    if j==0:
        port1=df
    else:
        port1=pd.concat([port1,df])
        
    pj2=pd.read_csv(out_path+'port_btm_'+period.iat[j]+'.csv')
    pj2['Btm']=pj2.sum(axis=1,numeric_only=True)
    df2=pj2[['DATES','Btm']]
    if j==0:
        port2=df2
    else:
        port2=pd.concat([port2,df2])
        
    pj3=pd.read_csv(out_path+'port_bs_'+period.iat[j]+'.csv')
    pj3['BuySell']=pj3.sum(axis=1,numeric_only=True)
    df3=pj3[['DATES','BuySell']]
    if j==0:
        port3=df3
    else:
        port3=pd.concat([port3,df3])
   
port1=port1.dropna()
port2=port2.dropna()
port3=port3.dropna()
 
port1['Btm']=port2['Btm']
print(i)
port1['BuySell']=port3['BuySell']
port1[['Top','Btm','BuySell']]=port1[['Top','Btm','BuySell']]*100

port1.to_csv(out_path+'port/port.csv',index=False)
