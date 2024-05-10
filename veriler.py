import os
import requests
from datetime import timedelta,date,datetime
gun=timedelta(days=1)
guncel=datetime.now()-gun*2
sayac=len(os.listdir("./data/map"))
sorun_sayac=0
while sayac<600:
    tarih=guncel.strftime("%Y-%m-%d")
    link="https://gpsjam.org/data/"+tarih+"-h3_4.csv"
    r=requests.get(link)
    guncel-=gun
    if r.status_code!=200:
        sorun_sayac+=1
        if sorun_sayac==7:break
        continue
    sorun_sayac=0
    print(sayac,guncel.strftime("%Y-%m-%d"))
    f = open("./data/map/"+tarih+".csv", "w")
    f.write(r.text)
    f.close()
    sayac+=1
