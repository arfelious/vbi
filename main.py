import reverse_geocoder as rg
import pandas as pd
import matplotlib.pyplot as plt
import h3
import os
if __name__ == '__main__':
    test=True
    dosyalar=os.listdir("./data")
    veriler=[]
    miktar=min(len(dosyalar),3) if test else len(dosyalar)
    for i in range(miktar):
        ayristirilan=[]
        koordinatlar=[]
        df=pd.read_csv("./data/"+dosyalar[i])
        df_miktar=min(len(df),10000) if test else len(df)
        for j in range(df_miktar):
            if j%1000==0:print(j,df_miktar,j/df_miktar)
            guncel=df.loc[j]
            koordinatlar.append(h3.h3_to_geo(guncel.hex))
            ayristirilan.append([int(guncel.count_good_aircraft),int(guncel.count_bad_aircraft)])
        ulkeler=rg.search(koordinatlar,verbose=False)
        print (ulkeler[i])
        veriler.append([[ulkeler[i]["cc"],ayristirilan[i][0],ayristirilan[i][1]] for i in range(df_miktar)])
        ulke_basina={}
    for i in veriler:
        for j in i:
            if not j[0] in ulke_basina:ulke_basina[j[0]]=[0,0]
            ulke_basina[j[0]]=[ulke_basina[j[0]][0]+j[1],ulke_basina[j[0]][1]+j[2]]
    ulke_sayac=[]
    for i in ulke_basina:ulke_sayac.append([i,ulke_basina[i],(max(0,ulke_basina[i][1]-1))/(ulke_basina[i][0]+ulke_basina[i][1])])
    ulke_sayac.sort(key=lambda a:a[2],reverse=True)
    print(ulke_sayac)
    ulkeler=[]
    degerler=[]
    for i in ulke_sayac:
        if i[2]>0.0003:
            ulkeler.append(i[0])
            degerler.append(i[2]*100)
    #plt.bar(ulkeler, degerler, color ='maroon', 
    #    width = 0.4)
    #plt.show()