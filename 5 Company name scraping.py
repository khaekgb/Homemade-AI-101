
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

