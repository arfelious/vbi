import os
import requests
from datetime import timedelta,date,datetime
gun=timedelta(days=1)
guncel=datetime.now()-gun*2
arr=os.listdir("./data/map")
map_set=set(arr)
sayac=0
sorun_sayac=0
while sayac<600:
    tarih=guncel.strftime("%Y-%m-%d")
    print(sayac,guncel.strftime("%Y-%m-%d"))
    dosya_adi=tarih+".csv"
    sayac+=1
    guncel-=gun
    if dosya_adi in map_set:
        print("exists")
        continue
    link="https://gpsjam.org/data/"+tarih+"-h3_4.csv"
    r=requests.get(link)
    if r.status_code!=200:
        sorun_sayac+=1
        if sorun_sayac==7:break
        continue
    sorun_sayac=0
    f = open("./data/map/"+dosya_adi, "w")
    f.write(r.text)
    f.close()
