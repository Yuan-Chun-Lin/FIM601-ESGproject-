

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
#from datetime import datetime as dt


Port=pd.read_csv("C:/NCSU/Spring2022/ESG/PythonData/tmp/port/port.csv")
FF3=pd.read_csv("C:/NCSU/Spring2022/ESG/PythonData/Data/F-F_Research_Data_Factors_daily_new.CSV")

FF3 = FF3.dropna()
#P100 = P100.where(P100.iloc[:,:]!=-99.99)
Port['DATES']=pd.to_datetime(Port['DATES'])
Port['DATES'] = pd.to_datetime(Port['DATES'], format='%Y%m%d')#, errors='ignore')
Port=Port.rename(columns={'DATES':'date'})
FF3['date'] = pd.to_datetime(FF3['date'], format='%Y%m%d', errors='ignore')
FF3 = FF3.rename(columns={"Mkt-RF": "Mkt_RF"})

Rg = pd.merge(Port,FF3,how='left', on='date')
# minus RF
for i in range(1,3):
    Rg.iloc[:,i] = Rg.iloc[:,i] - Rg.iloc[:,7]


# a = CAPM.params, a[0] = intercept, a[1] = beta1, ...
alpha=[]
beta1=[]
beta2=[]
beta3=[]
col_list=Rg.columns.drop(['date','Mkt_RF','SMB','HML','RF'])
# Step1: Run time-series to get the market factor params.
for i in col_list:
    mod = smf.ols(formula= i+' ~ Mkt_RF + SMB + HML', data=Rg)
    FF = mod.fit()
    Params = FF.params
    alpha.append(Params[0])
    beta1.append(Params[1])
    beta2.append(Params[2])
    
    beta3.append(Params[3])
    print(FF.summary())
    #FF.to_csv("C:/NCSU/Spring2022/ESG/PythonData/tmp/port/summary.csv",index=False)
beta = pd.DataFrame(np.matrix([alpha,beta1,beta2,beta3]),index=['alpha','beta1','beta2','beta3'],columns=col_list)


print(beta)
