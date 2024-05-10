import reverse_geocoder as rg
import pandas as pd
import matplotlib.pyplot as plt
import bar_chart_race as bcr
import plotly
import h3
import os
import datetime
import math
if __name__ == '__main__':
    def oranla(sorunsuz,sorunlu):
        return max(0,(sorunsuz-1)/max(1,sorunsuz+sorunlu))
    test=True   
    dosyalar=sorted(os.listdir("./data/map"))
    veriler=[]
    veri_gunler = []
    miktar=min(len(dosyalar),50) if test else len(dosyalar)
    for i in range(miktar):
        veri_gunler.append(datetime.datetime.strptime(dosyalar[i].split(".csv")[0],"%Y-%m-%d"))
        ayristirilan=[]
        koordinatlar=[]
        df=pd.read_csv("./data/map/"+dosyalar[i])
        df_miktar=min(len(df),10000) if test else len(df)
        for j in range(df_miktar):
            if j%1000==0:print(i,miktar,i/miktar,j,df_miktar,j/df_miktar)
            guncel=df.loc[j]
            koordinatlar.append(h3.h3_to_geo(guncel.hex))
            ayristirilan.append([int(guncel.count_good_aircraft),int(guncel.count_bad_aircraft)])
        ulkeler=rg.search(koordinatlar,verbose=False)
        veriler.append([[ulkeler[i]["cc"],ulkeler[i]["admin1"],ayristirilan[i][0],ayristirilan[i][1]] for i in range(df_miktar)])
        ulke_basina={}
    gunluk_ulke_sayac=[{} for i in range(miktar)]
    for i in range(miktar):
        guncel_veri=veriler[i]
        for j in guncel_veri:
            if not j[0] in ulke_basina:ulke_basina[j[0]]={}
            if not j[1] in ulke_basina[j[0]]: ulke_basina[j[0]][j[1]]=[0,0]
            ulke_basina[j[0]][j[1]]=[ulke_basina[j[0]][j[1]][0]+j[2],ulke_basina[j[0]][j[1]][1]+j[3]]
            if not j[0] in gunluk_ulke_sayac[i]:gunluk_ulke_sayac[i][j[0]]=[0,0]
            gunluk_ulke_sayac[i][j[0]]=[gunluk_ulke_sayac[i][j[0]][0]+j[2],gunluk_ulke_sayac[i][j[0]][1]+j[3]]
    ulke_sayac={}
    ulke_toplam={}
    ulke_toplam_arr=[]
    for i in ulke_basina:
        ulke_sayac[i]=[]
        if not i in ulke_toplam:
            ulke_toplam[i]=[i,0,0]
        for j in ulke_basina[i]:
            ulke_sayac[i].append([j,ulke_basina[i][j][0],ulke_basina[i][j][1],oranla(ulke_basina[i][j][1],ulke_basina[i][j][0])])
            ulke_toplam[i]=[i,ulke_toplam[i][1]+ulke_basina[i][j][0],ulke_toplam[i][2]+ulke_basina[i][j][1]]
        ulke_sayac[i].sort(key=lambda a:a[2],reverse=True)
    for i in ulke_toplam:
        ulke_toplam[i].append(oranla(ulke_toplam[i][2],ulke_toplam[i][1]))
        ulke_toplam_arr.append(ulke_toplam[i])
    ulke_toplam_arr.sort(key=lambda a:a[3],reverse=True)
    print(ulke_toplam_arr)
    baskentler=pd.read_csv("./data/countries.csv")
    baskent_dict={}
    for _,i in baskentler.iterrows():
        baskent_dict[i["country"]]=i["capital"]
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

    baskentte_var=[any([i in cc and cc[i] in baskent_dict and ulke_sayac[i][j][0]==baskent_dict[cc[i]] for j in range(min(len(ulke_sayac[i]),5))]) for i in ulke_sayac]
    
    jammer_var=[any([j[2]>0 for j in ulke_sayac[i]]) for i in ulke_sayac].count(True)
    ulke_adet=[[i,max(0,sum(j[2] for j in ulke_sayac[i]))/max(1,(sum(j[2] for j in ulke_sayac[i])+sum(j[1] for j in ulke_sayac[i])))] for i in ulke_sayac]
    ulke_adet.sort(key=lambda a:a[1],reverse=True)
    ulke_adet_dict={}
    for i in ulke_adet:ulke_adet_dict[i[0]]=i[1]
    gelismislik_ve_yozlasmislik=[[i,hdi[i],i in corruption_dict and corruption_dict[i],i in corruption_dict and corruption_dict[i]*hdi[i]] for i in hdi]
    gvy=[]
    gvy_dict={}
    for i in gelismislik_ve_yozlasmislik: 
        if i[2] and i[0] in country2cc and country2cc[i[0]] in ulke_adet_dict:
            gvy.append([i[0],i[1],i[2]])
            gvy_dict[i[0]]=[i[1],i[2]]
    gvy.sort(key=lambda a:ulke_adet_dict[country2cc[a[0]]],reverse=True)
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    gecerli_ulke_adet=list(filter(lambda a:a[0] in cc and cc[a[0]] in gvy_dict,map(lambda a: [a[0],math.floor(a[1]*1000)/1000],ulke_adet)))

    print(len(gecerli_ulke_adet),len(gvy))
    xs=[i[1] for i in gecerli_ulke_adet]
    ys=[i[2] for i in gvy]
    zs=[i[1] for i in gvy]
    print(xs,ys,zs)
    ax.scatter(xs, ys, zs)
    ax.set_yticks(ys,[i[0] for i in gecerli_ulke_adet])
    #plt.show()
    hafta_sayilar={}
    ulke_gecerli_gun_miktar={}
    guncel_hafta=veri_gunler[0].strftime("%Y-%m-%d")
    hafta_sayilar[guncel_hafta]={}
    hafta_oranlar={"date":[]}
    son_tarih=veri_gunler[0].timestamp()
    bir_hafta=7*24*60*60
    for i in range(miktar):
        tarih=veri_gunler[i]
        guncel_timestamp=tarih.timestamp()
        print(guncel_timestamp-son_tarih)
        while guncel_timestamp-son_tarih>bir_hafta:
            son_tarih+=bir_hafta
            yeni_hafta=datetime.datetime.fromtimestamp(son_tarih).strftime("%Y-%m-%d")
            print(yeni_hafta,guncel_hafta)
            guncel_hafta=yeni_hafta
            hafta_sayilar[guncel_hafta]={}
        veri=gunluk_ulke_sayac[i]
        for j in veri:
            if not j in hafta_sayilar[guncel_hafta]:
                hafta_sayilar[guncel_hafta][j]=[0,0]
            if not j in ulke_gecerli_gun_miktar:ulke_gecerli_gun_miktar[j]=0
            ulke_gecerli_gun_miktar[j]+=1
            hafta_sayilar[guncel_hafta][j]=[hafta_sayilar[guncel_hafta][j][0]+veri[j][0],hafta_sayilar[guncel_hafta][j][1]+veri[j][1]]

    print("hafta sayılar",hafta_sayilar)
    to_delete=[]
    for i in hafta_sayilar:
        for j in hafta_sayilar[i]:
            if ulke_gecerli_gun_miktar[j]!=miktar: to_delete.append([i,j])
    for i in to_delete:del hafta_sayilar[i[0]][i[1]]
    for i in hafta_sayilar:
        hafta_oranlar["date"].append(i)
        for j in hafta_sayilar[i]:
            deger=math.floor(1000*oranla(hafta_sayilar[i][j][1],hafta_sayilar[i][j][0]))/10
            if not j in hafta_oranlar: hafta_oranlar[j]=[]
            hafta_oranlar[j].append(deger)

    hafta_df=pd.DataFrame.from_dict(hafta_oranlar)
    hafta_df.set_index("date",inplace=True)

    print(hafta_df)
    bcr.bar_chart_race(
        df=hafta_df,
        filename="test.mp4",
        orientation='h', 
        sort='desc', 
        n_bars=10, 
        bar_texttemplate='{x:,.2f}',
        period_length=2000,
        steps_per_period=50,
        end_period_pause=500,
        title="Haftalık GPS Jammer Sıralaması"
    ) 