import matplotlib.pyplot as plt
import reverse_geocoder as rg
import bar_chart_race as bcr # pip install git+https://github.com/programiz/bar_chart_race.git@master
from functools import reduce
import pandas as pd
import datetime
import plotly
import json 
import math
import csv
import os
import h3
if __name__ == '__main__':
    def oranla(sorunlu,sorunsuz):
        return max(0,(sorunlu-1)/max(1,sorunsuz+sorunlu))
    def list_oranla(curr):
        return oranla(curr[1],curr[0])
    yapilacaklar={"olustur":False,"test":False,"video":False,"baskent":True}
    olustur=True
    test=False
    if yapilacaklar["olustur"]:
        dosyalar=sorted(os.listdir("./data/map"))
        veriler=[]
        veri_gunler = []
        miktar=min(len(dosyalar),10) if test else len(dosyalar)
        for i in range(miktar):
            veri_gunler.append(datetime.datetime.strptime(dosyalar[i].split(".csv")[0],"%Y-%m-%d"))
            ayristirilan=[]
            koordinatlar=[]
            df=pd.read_csv("./data/map/"+dosyalar[i])
            df_miktar=min(len(df),10000) if test else len(df)
            for j in range(df_miktar):
                if j%1000==0:print(i,miktar,i/miktar+j/df_miktar/miktar,j,df_miktar,j/df_miktar)
                guncel=df.loc[j]
                koordinatlar.append(h3.h3_to_geo(guncel.hex))
                ayristirilan.append([int(guncel.count_good_aircraft),int(guncel.count_bad_aircraft)])
            ulkeler=rg.search(koordinatlar,verbose=False)
            veriler.append([[ulkeler[i]["cc"],ulkeler[i]["admin1"],ayristirilan[i][0],ayristirilan[i][1]] for i in range(df_miktar)])
            del df,koordinatlar,ayristirilan
            ulke_basina={}
        gunluk_ulke_sayac=[{} for i in range(miktar)]
        gunluk_sehir_sayac=[{} for i in range(miktar)]
        for i in range(miktar):
            guncel_veri=veriler[i]
            for j in guncel_veri:
                if not j[0] in ulke_basina:ulke_basina[j[0]]={}
                if not j[1] in ulke_basina[j[0]]: ulke_basina[j[0]][j[1]]=[0,0]
                ulke_basina[j[0]][j[1]]=[ulke_basina[j[0]][j[1]][0]+j[2],ulke_basina[j[0]][j[1]][1]+j[3]]
                if not j[0] in gunluk_ulke_sayac[i]:
                    gunluk_ulke_sayac[i][j[0]]=[0,0]
                    gunluk_sehir_sayac[i][j[0]]={}
                if not j[1] in gunluk_sehir_sayac[i][j[0]]: gunluk_sehir_sayac[i][j[0]][j[1]]=[0,0]
                gunluk_ulke_sayac[i][j[0]]=[gunluk_ulke_sayac[i][j[0]][0]+j[2],gunluk_ulke_sayac[i][j[0]][1]+j[3]]
                gunluk_sehir_sayac[i][j[0]][j[1]]=[gunluk_sehir_sayac[i][j[0]][j[1]][0]+j[2],gunluk_sehir_sayac[i][j[0]][j[1]][1]+j[3]]
        cc2country=pd.read_csv("./data/cc_to_country.csv")
        corruption_arr=pd.read_csv("./data/corruption_data.csv")
        corruption_dict = {}
        for _,row in corruption_arr.iterrows():corruption_dict[row["region_name"].strip()]=row["2021"]
        hdi_arr=pd.read_csv("./data/hdi.csv")
        hdi={}
        for i,row in hdi_arr.iterrows():hdi[row["country"]]=row["Hdi2022"]
        cc={}
        country2cc={}
        for _,i in cc2country.iterrows():
            cc[i["alpha-2"]]=i["name"]
            country2cc[i["name"]]=i["alpha-2"]
    
        hafta_sayilar={}
        hafta_array={}
        hafta_sehir_array={}
        ulke_gecerli_gun_miktar={}
        guncel_hafta=veri_gunler[0].strftime("%Y-%m-%d")
        hafta_sayilar[guncel_hafta]={}
        hafta_array[guncel_hafta]={}
        hafta_sehir_array[guncel_hafta]={}
        son_tarih=veri_gunler[0].timestamp()
        bir_gun=24*60*60
        bir_hafta=7*bir_gun
        hafta_tarihler=[guncel_hafta]
        for i in range(miktar):
            tarih=veri_gunler[i]
            guncel_timestamp=tarih.timestamp()
            fark=guncel_timestamp-son_tarih
            while fark>=bir_hafta:
                son_tarih+=bir_hafta
                fark=guncel_timestamp-son_tarih
                guncel_hafta=datetime.datetime.fromtimestamp(son_tarih).strftime("%Y-%m-%d")
                hafta_tarihler.append(guncel_hafta)
                hafta_sayilar[guncel_hafta]={}
                hafta_array[guncel_hafta]={}
                hafta_sehir_array[guncel_hafta]={}
            guncel_gun=math.floor(fark/bir_gun)
            veri=gunluk_ulke_sayac[i]
            for j in veri:
                if not j in hafta_sayilar[guncel_hafta]:
                    hafta_sayilar[guncel_hafta][j]=[0,0]
                    hafta_array[guncel_hafta][j]=[]
                    hafta_sehir_array[guncel_hafta][j]={}
                if not j in ulke_gecerli_gun_miktar:ulke_gecerli_gun_miktar[j]=0
                ulke_gecerli_gun_miktar[j]+=1
                hafta_sayilar[guncel_hafta][j]=[hafta_sayilar[guncel_hafta][j][0]+veri[j][0],hafta_sayilar[guncel_hafta][j][1]+veri[j][1]]
                hafta_array[guncel_hafta][j].append([guncel_gun,veri[j][0],veri[j][1]])
            sehir=gunluk_sehir_sayac[i]
            for j in sehir:
                for q in sehir[j]:
                    if not q in hafta_sehir_array[guncel_hafta][j]:
                        hafta_sehir_array[guncel_hafta][j][q]=[]
                    hafta_sehir_array[guncel_hafta][j][q].append([guncel_gun,sehir[j][q][0],sehir[j][q][1]])
    
        to_delete=[]
        header=["date","cc","data","hdi","corruption","is_near_war"]
        for i in hafta_sayilar:
            for j in hafta_sayilar[i]:
                if ulke_gecerli_gun_miktar[j]!=miktar: to_delete.append([i,j])
        for i in to_delete:
            del hafta_sayilar[i[0]][i[1]]
            del hafta_array[i[0]][i[1]]
        with open("./data/country_data.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            sayac=0
            for i in hafta_sayilar:
                for j in hafta_sayilar[i]:
                    if not j in cc: continue
                    deger=math.floor(1000*oranla(hafta_sayilar[i][j][1],hafta_sayilar[i][j][0]))/10
                    data_arr=[[0,0]]*7
                    for idx in range(len(hafta_array[i][j])): 
                        e=hafta_array[i][j][idx]
                        data_arr[e[0]]=[e[1],e[2]]
                    writer.writerow([
                        hafta_tarihler[sayac], 
                        j,
                        json.dumps(data_arr,separators=(',', ':')),
                        hdi[cc[j]] if cc[j] in hdi else 0,
                        corruption_dict[cc[j]] if cc[j] in corruption_dict else 50, 
                        False
                    ])
                sayac+=1
        header=["date","cc","city","data"]
        with open("./data/city_data.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            sayac=0
            for i in hafta_sehir_array :
                for j in hafta_sehir_array[i]:
                    for q in hafta_sehir_array[i][j]:
                        data_arr=[[0,0]]*7
                        for idx in range(len(hafta_sehir_array[i][j][q])): 
                            e=hafta_sehir_array[i][j][q][idx]
                            data_arr[e[0]]=[e[1],e[2]]
                            writer.writerow([
                                hafta_tarihler[sayac], 
                                j,
                                q,
                                json.dumps(data_arr,separators=(',', ':')),
                            ])
                sayac+=1
    country_df=pd.read_csv("./data/country_data.csv")
    country_df["data"]=country_df["data"].apply(json.loads)
    city_df=pd.read_csv("./data/city_data.csv")
    city_df["data"]=city_df["data"].apply(json.loads)
    if yapilacaklar["baskent"]:
        baskentler=pd.read_csv("./data/countries.csv")
        baskent_dict={}
        for _,i in baskentler.iterrows():
            baskent_dict[i["country"]]=i["capital"]
        ulke_basine_jammer_sehir={}
        for _,row in city_df.iterrows():
            data=row["data"]
            country=row["cc"]
            city=row["city"]
            if  city!=city: continue
            jammer_var=False
            for i in range(7):
                if data[i][1]:
                    jammer_var=True
                    break
            if jammer_var:
                if not country in ulke_basine_jammer_sehir:
                    ulke_basine_jammer_sehir[country]={}
                if not city in ulke_basine_jammer_sehir[country]:
                    ulke_basine_jammer_sehir[country][city]=[0,0]
                for i in range(7):
                    ulke_basine_jammer_sehir[country][city]=[ulke_basine_jammer_sehir[country][city][0]+data[i][0],
                    ulke_basine_jammer_sehir[country][city][1]+data[i][1]]
        sehir_siralanmis={i:sorted(list(ulke_basine_jammer_sehir[i].items()),
        key=lambda a:list_oranla(ulke_basine_jammer_sehir[i][a[0]])) for i in ulke_basine_jammer_sehir}
        #ülke başına en çok jammer içeren şehirler sıralandı ama başkentte var mı hipotezi kontrol edilecek

    if yapilacaklar["video"]:
        genis_dict={"date":[]}
        son_tarih=None
        for _,row in country_df.iterrows():
            guncel_tarih=row["date"]
            if son_tarih!=guncel_tarih:
                genis_dict["date"].append(guncel_tarih)
                son_tarih=guncel_tarih
            cc=row["cc"]
            if not cc in genis_dict: genis_dict[cc]=[]
            data=row["data"]
            sorunlu_toplam=reduce(lambda acc,x:acc+x[1],data,0)
            sorunsuz_toplam=reduce(lambda acc,x:acc+x[0],data,0)
            oran=math.floor(1000*oranla(sorunlu_toplam,sorunsuz_toplam))/10
            genis_dict[cc].append(oran)
        hafta_df=pd.DataFrame.from_dict(genis_dict)
        hafta_df.set_index("date",inplace=True)
        bcr.bar_chart_race(
            df=hafta_df,
            filename="test.mp4",
            orientation='h', 
            sort='desc', 
            n_bars=20, 
            bar_texttemplate='{x:,.2f}',
            period_length=1000,
            steps_per_period=50,
            end_period_pause=500,
            title="Haftalık GPS Jammer Sıralaması"
        ) 