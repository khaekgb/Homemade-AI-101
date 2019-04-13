
# coding: utf-8

# In[3]:


## ดึงรายชื่อหุ้น
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
import urllib
    
tickers =   ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

for ticker in tickers:
    print(ticker)
    page = 0 #reset page
                   
    url_string = "https://www.set.or.th/set/commonslookup.do?language=th&country=TH&prefix={0}".format(ticker)
       
    page = urllib.request.urlopen(url_string).read()   
        
    soup = BeautifulSoup(page, 'lxml') 
    table = soup.find_all("table", {"class":"table table-profile table-hover table-set-border-yellow"})
    df = pd.read_html(str(table))
    a = np.array(df[0])
        
    if ticker == 'A' : 
            
            b=a[1:,0]                   #[1:] เลือก row 1 ไปจนหมด , 0 เลือก column แรก
        
    else : 
            b = np.append(b,a[1:,0])    
            
np.savetxt("ticker.csv", b , fmt='%.11s' , newline = "','" )    #%.11s = 11 string

# print(b)


# In[4]:


#ดึงข้อมูลตาราง จากไฟล์ html หุ้นแต่ละตัว มารวมเปน csv ไฟล์เดียว เพื่อกรองหุ้นที่รูปแบบตารางไม่เหมือนกันออกไป 
import os
import urllib.request  
from datetime import datetime
import codecs
from bs4 import BeautifulSoup
import pandas as pd

tickers = ['A','AAV','ABICO','ABM','ABPIF','ACAP','ACC','ADAM','ADB','ADVANC','AEC','AEONTS','AF','AFC','AGE','AH','AHC','AI','AIE','AIMIRT','AIRA',
               'AIT','AJ','AJA','AKP','AKR','ALLA','ALT','ALUCON','AMA','AMANAH','AMARIN','AMATA','AMATAR','AMATAV','AMC','ANAN','AOT','AP','APCO',
               'APCS','APEX','APURE','AQ','AQUA','ARIP','ARROW','AS','ASAP','ASEFA','ASIA','ASIAN','ASIMAR','ASK','ASN','ASP','ATP30','AU','AUCT','AYUD',
               'BA','BAFS','BANPU','BAT-3K','BAY','BBL','BCH','BCP','BCPG','BDMS','BEAUTY','BEC','BEM','BFIT','BGRIM','BGT','BH','BIG','BIZ','BJC',
               'BJCHI','BKD','BKI','BKKCP','BLA','BLAND','BLISS','BM','BOL','BPP','BR','BROCK','BROOK','BRR','BRRGIF','BSBM','BSM','BTNC',
               'BTS','BTSGIF','BTW','BUI','BWG','CBG','CCET','CCP','CEN','CENTEL','CFRESH','CGD','CGH','CHARAN','CHEWA','CHG','CHO','CHOTI','CHOW',
               'CHUO','CI','CIG','CIMBT','CITY','CK','CKP','CM','CMO','CMR','CNS','CNT','COL','COLOR','COMAN','CPALL','CPF','CPH','CPI','CPL','CPN',
               'CPNCG','CPNREIT','CPR','CPT','CPTGF','CRANE','CRD','CRYSTAL','CSC','CSL','CSP','CSR','CSS','CTARAF','CTW','CWT','D','DCC','DCON','DCORP',
               'DDD','DELTA','DEMCO','DIF','DIGI','DIMET','DNA','DREIT','DRT','DTAC','DTC','DTCI','EA','EARTH','EASON','EASTW','ECF','ECL','EE','EFORL',
               'EGATIF','EGCO','EIC','EKH','EMC','EPCO','EPG','ERW','ERWPF','ESSO','ESTAR','ETE','EVER','FANCY','FC','FE','FER','FLOYD','FMT','FN',
               'FNS','FOCUS','FORTH','FPI','FSMART','FSS','FTE','FUTUREPF','FVC','GAHREIT','GBX','GC','GCAP','GEL','GENCO','GFPT','GGC','GIFT','GJS','GL',
               'GLAND','GLANDRT','GLOBAL','GLOW','GOLD','GOLDPF','GPI','GPSC','GRAMMY','GRAND','GREEN','GSTEL','GTB','GULF','GUNKUL','GVREIT',
               'GYT','HANA','HARN','HFT','HMPRO','HOTPOT','HPF','HPT','HREIT','HTC','HTECH','HUMAN','HYDRO','ICC','ICHI','ICN','IEC','IFEC','IFS','IHL'
               ,'III','ILINK','IMPACT','INET','INGRS','INOX','INSURE','INTUCH','IRC','IRCP','IRPC','IT','ITD','ITEL','IVL','J','JAS','JASIF','JCP','JCT','JKN',
               'JMART','JMT','JSP','JTS','JUBILE','JUTHA','JWD','K','KAMART','KASET','KBANK','KBS','KC','KCAR','KCE','KCM','KDH','KGI','KIAT','KKC','KKP',
               'KOOL','KPNPF','KSL','KTB','KTC','KTECH','KTIS','KWC','KWG','KYE','LALIN','LANNA','LDC','LEE','LH','LHBANK','LHHOTEL','LHK','LHPF',
               'LHSC','LIT','LOXLEY','LPH','LPN','LRH','LST','LTX','LUXF','LVT','M','M-CHAI','M-II','M-PAT','M-STOR','MACO','MAJOR','MAKRO','MALEE',
               'MANRIN','MATCH','MATI','MAX','MBAX','MBK','MBKET','MC','MCOT','MCS','MDX','MEGA','METCO','MFC','MFEC','MGT','MIDA','MILL','MINT',
               'MIPF','MIT','MJD','MJLF','MK','ML','MM','MNIT','MNIT2','MNRF','MODERN','MONO','MONTRI','MOONG','MPG','MPIC','MSC','MTI','MTLS',
               'NBC','NC','NCH','NCL','NDR','NEP','NETBAY','NEW','NEWS','NFC','NINE','NKI','NMG','NNCL','NOBLE','NOK','NPK','NPP','NSI','NTV','NUSA',
               'NVD','NWR','NYT','OCC','OCEAN','OGC','OHTL','OISHI','ORI','OTO','PACE','PAE','PAF','PAP','PATO','PB','PCSGH','PDG','PDI','PDJ','PE','PERM',
               'PF','PG','PHOL','PICO','PIMO','PJW','PK','PL','PLANB','PLANET','PLAT','PLE','PM','PMTA','POLAR','POMPUI','POPF','PORT','POST','PPF','PPM',
               'PPP','PPS','PRAKIT','PREB','PRECHA','PRG','PRIN','PRINC','PRM','PRO','PSH','PSL','PSTC','PT','PTG','PTL','PTT','PTTEP','PTTGC','PYLON',
               'Q-CON','QH','QHHR','QHOP','QHPF','QLT','QTC','RAM','RATCH','RCI','RCL','RICH','RICHY','RJH','RML','ROBINS','ROCK','ROH','ROJNA',
               'RP','RPC','RPH','RS','RSP','RWI','S','S11','SABINA','SAFARI','SALEE','SAM','SAMART','SAMCO','SAMTEL','SANKO','SAPPE','SAT',
               'SAUCE','SAWAD','SAWANG','SBPF','SC','SCB','SCC','SCCC','SCG','SCI','SCN','SCP','SDC','SE','SE-ED','SEAFCO','SEAOIL','SELIC','SENA',
               'SF','SFP','SGF','SGP','SHANG','SHREIT','SIAM','SIMAT','SINGER','SIRI','SIRIP','SIS','SITHAI','SKE','SKN','SKR','SKY','SLP','SMART','SMIT',
               'SMK','SMM','SMPC','SMT','SNC','SNP','SOLAR','SORKON','SPA','SPACK','SPALI','SPC','SPCG','SPF','SPG','SPI','SPORT','SPPT','SPRC','SPVI',
               'SQ','SR','SRICHA','SRIPANWA','SSC','SSF','SSI','SSP','SSPF','SSSC','SST','SSTPF','SSTRT','STA','STANLY','STAR','STEC','STHAI','STPI','SUC',
               'SUN','SUPER','SUSCO','SUTHA','SVH','SVI','SVOA','SWC','SYMC','SYNEX','SYNTEC','T','TACC','TAE','TAKUNI','TAPAC','TASCO','TBSP','TC',
               'TCAP','TCB','TCC','TCCC','TCJ','TCMC','TCOAT','TEAM','TFD','TFG','TFI','TFMAMA','TGCI','TGPRO','TH','THAI','THANA','THANI','THCOM',
               'THE','THG','THIP','THL','THMUI','THRE','THREL','TIC','TICON','TIF1','TIP','TIPCO','TISCO','TITLE','TIW','TK','TKN','TKS','TKT','TLGF',
               'TLHPF','TLUXE','TM','TMB','TMC','TMD','TMI','TMILL','TMT','TMW','TNDT','TNH','TNITY','TNL','TNP','TNPC','TNPF','TNR','TOA','TOG',
               'TOP','TOPP','TPA','TPAC','TPBI','TPCH','TPCORP','TPIPL','TPIPP','TPOLY','TPP','TPRIME','TR','TRC','TREIT','TRITN','TRT','TRU','TRUBB',
               'TRUE','TSC','TSE','TSF','TSI','TSR','TSTE','TSTH','TTA','TTCL','TTI','TTL','TTLPF','TTTM','TTW','TU','TU-PF','TUCC','TVD','TVI','TVO','TVT',
               'TWP','TWPC','TWZ','TYCN','U','UAC','UBIS','UEC','UKEM','UMI','UMS','UNIQ','UOBKH','UP','UPA','UPF','UPOIC','URBNPF','UREKA','UT',
               'UTP','UV','UVAN','UWC','VARO','VCOM','VGI','VI','VIBHA','VIH','VNG','VNT','VPO','VTE','WACOAL','WAVE','WG','WHA','WHABT','WHART',
               'WHAUP','WICE','WIIK','WIN','WINNER','WORK','WORLD','WP','WPH','WR','XO','YCI','YNP','YUASA','ZIGA','ZMICO' ] 
    #'B-WORK',BOFFICE','S & J',

df=  pd.DataFrame(data=[])

for ticker in tickers:
    page = 0 #reset page
    y=0
    file_name = 'set_html_Monthly/{}/20180316.html'.format(ticker)    
    page=codecs.open(file_name, encoding="utf8") 
    soup = BeautifulSoup(page, 'lxml') 
    table = soup.find_all("table", {"class":"table-factsheet-padding0"})
    data = pd.read_html(str(table))
    print(ticker)
    for t in range(0,len(table)) :
        x = data[t].iloc[0:1,0] 
        z = data[t].iloc[:,0:1]
        
        if x.item() == 'Statement of Financial Position (MB.)' : 

            tk = [ticker]
            y = pd.DataFrame(data=tk)
            y = y.append(data[t].iloc[:,0:1] , ignore_index=True) 
            
        elif x.item() == 'Statement of Comprehensive Income (MB.)' :
            y = y.append(data[t].iloc[:,0:1] , ignore_index=True) 
            
        elif x.item() == 'Statement of Cash Flow (MB.)'  :
            y = y.append(data[t].iloc[:,0:1] , ignore_index=True)
            
    ex = y.transpose()
    df = df.append(ex, ignore_index=True)
    
# df.to_csv('44444.csv')


# In[ ]:


#เปลี่ยนรายชื่อหุ้นจากไฟล์ csv เป็น ใส่ '  ', ให้หุ้นแต่ละตัว
import csv
import numpy as np
with open('normal ticker.csv', newline='') as f:
    reader = csv.reader(f)
    r=[]
    for row in reader:
        r = np.append(r, row)
# print(r)
np.savetxt("normal ticker11.csv", r  , fmt='%.11s' , newline = "','" ) 

