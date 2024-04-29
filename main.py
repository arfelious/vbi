import reverse_geocoder as rg
import pandas as pd
import matplotlib.pyplot as plt
import h3
import os
import math
if __name__ == '__main__':
    test=True
    dosyalar=os.listdir("./data/map")
    veriler=[]
    miktar=min(len(dosyalar),3) if test else len(dosyalar)
    for i in range(miktar):
        ayristirilan=[]
        koordinatlar=[]
        df=pd.read_csv("./data/map/"+dosyalar[i])
        df_miktar=min(len(df),10000) if test else len(df)
        for j in range(df_miktar):
            if j%1000==0:print(j,df_miktar,j/df_miktar)
            guncel=df.loc[j]
            koordinatlar.append(h3.h3_to_geo(guncel.hex))
            ayristirilan.append([int(guncel.count_good_aircraft),int(guncel.count_bad_aircraft)])
        ulkeler=rg.search(koordinatlar,verbose=False)
        veriler.append([[ulkeler[i]["cc"],ulkeler[i]["admin1"],ayristirilan[i][0],ayristirilan[i][1]] for i in range(df_miktar)])
        ulke_basina={}
    for i in veriler:
        for j in i:
            if not j[0] in ulke_basina:ulke_basina[j[0]]={}
            if not j[1] in ulke_basina[j[0]]: ulke_basina[j[0]][j[1]]=[0,0]
            ulke_basina[j[0]][j[1]]=[ulke_basina[j[0]][j[1]][0]+j[2],ulke_basina[j[0]][j[1]][1]+j[3]]
    ulke_sayac={}
    #print(ulke_basina)
    for i in ulke_basina:
        ulke_sayac[i]=[]
        for j in ulke_basina[i]:
            ulke_sayac[i].append([j,ulke_basina[i][j][0],ulke_basina[i][j][1],max(0,ulke_basina[i][j][1]-1)/(ulke_basina[i][j][0]+ulke_basina[i][j][1])])
        ulke_sayac[i].sort(key=lambda a:a[2],reverse=True)
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

plt.show()