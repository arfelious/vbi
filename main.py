from functools import reduce,cache
from matplotlib_venn import venn2
import matplotlib.pyplot as plt
import reverse_geocoder as rg
import bar_chart_race as bcr # pip install git+https://github.com/programiz/bar_chart_race.git@master
from scipy import stats
import seaborn as sb
import polars as pl
import pandas as pd
import numpy as np
import datetime
import random
import json 
import math
import time
import csv
import os
import h3
import gc
if __name__ == '__main__':
    def oranla(sorunlu,sorunsuz):
        return max(0,(sorunlu-1)/max(1,sorunsuz+sorunlu))
    @cache
    def h3_to_geo(x):
        return h3.h3_to_geo(x)
    def ondalik(x,y):
        return math.floor(x*10**y)/10**y
    def search(x):
        return rg.search(x,verbose=False)
    def surec(i,miktar):
        print(str(i)+"/"+str(miktar)+" "*10+"\r",end="")
        if i>=miktar:print(" "*30+"\r",end="")
    def yeni():
        global plot_sayac
        plt.figure()
        plot_sayac=plot_miktar*100+20
    yapilacaklar={"olustur":True,"istatistik":False,"test":False,"video":True,"baskent":True,"savas":True,"koreleasyon":True,"gun":True}
    cizilecek={"koreleasyon","baskent","savas"}
    ulke_basine_jammer_sehir={}
    jammer_oranlar=[]
    yaptirilacaklar={}
    hafta_ici={}
    hafta_sonu={}
    def list_oranla(curr):
        return oranla(curr[1],curr[0])
    def hangi(row,sayac):
        global son_tarih,son_haftasonu
        data=row["data"]
        for i in range(7):
            kullanicilacak_dict=hafta_sonu if i<5 else hafta_ici
            city=row["city"]
            if city!=city:return
            country=row["cc"]
            if not country in kullanicilacak_dict:
                kullanicilacak_dict[country]=set()
            if data[i][1]>1:
                kullanicilacak_dict[country].add(city)

    def baskent(row,sayac):
            data=row["data"]
            country=row["cc"]
            city=row["city"]
            sayac+=1
            if city!=city: return
            jammer_var=False
            for i in range(7):
                if data[i][1]>1:
                    jammer_var=True
                    break
            if jammer_var:
                if not country in ulke_basine_jammer_sehir:
                    ulke_basine_jammer_sehir[country]={}
                if not city in ulke_basine_jammer_sehir[country]:
                    ulke_basine_jammer_sehir[country][city]=[0,0]
                for i in range(7):
                    ulke_basine_jammer_sehir[country][city]=[
                        ulke_basine_jammer_sehir[country][city][0]+data[i][0],
                        ulke_basine_jammer_sehir[country][city][1]+data[i][1]
                    ]
                jammer_oranlar.append(list_oranla(ulke_basine_jammer_sehir[country][city]))
    cc={}
    country2cc={}
    cc2country=pl.read_csv("./data/cc_to_country.csv")
    for i in cc2country.rows(named=True):
        cc[i["alpha-2"]]=i["name"]
        country2cc[i["name"]]=i["alpha-2"]
    yaptirilacaklar["baskent"]=baskent
    yaptirilacaklar["gun"]=hangi
    if yapilacaklar["olustur"]:
        dosyalar=sorted(os.listdir("./data/map"))
        veriler=[]
        veri_gunler = []
        miktar=len(dosyalar)
        gecerli_miktar=0
        test=yapilacaklar["test"]
        aranacak=[]
        total_ayristirilan=[]
        aranacak_miktarlar=[]
        def aranacak_hallet(force):
            global aranacak,total_ayristirilan,aranacak_miktarlar,veriler
            aranacak_miktar=len(aranacak)
            yapilacak_miktar=len(aranacak_miktarlar)
            if yapilacak_miktar>=50 or (force and yapilacak_miktar>0):
                bulunan=search(aranacak)
                son=0
                for i in range(len(aranacak_miktarlar)):
                    e=aranacak_miktarlar[i]
                    guncel=bulunan[son:son+e]
                    guncel_ayristirilan=total_ayristirilan[i]
                    veriler.append([[guncel[j]["cc"],
                    guncel[j]["admin1"],
                    guncel_ayristirilan[j][0],
                    guncel_ayristirilan[j][1]] for j in range(e)])
                    son+=e
                del aranacak,total_ayristirilan,aranacak_miktarlar
                gc.collect()
                aranacak=[]
                total_ayristirilan=[]
                aranacak_miktarlar=[]
        gc.disable()
        for i in range(miktar):
            if test and i%100>0:continue
            gecerli_miktar+=1
            veri_gunler.append(datetime.datetime.strptime(dosyalar[i].split(".csv")[0],"%Y-%m-%d"))
            ayristirilan=[]
            df=pl.read_csv("./data/map/"+dosyalar[i])
            df_miktar=len(df)
            j=0
            for guncel in df.rows(named=True):
                if test and j%100>0:continue
                j+=1
                if j%10000==0:print(i,miktar,math.floor((i/miktar+j/df_miktar/miktar)*1e5)/1e5,j,df_miktar,j/df_miktar)
                aranacak.append(h3_to_geo(guncel["hex"]))
                ayristirilan.append([int(guncel["count_good_aircraft"]),int(guncel["count_bad_aircraft"])])
            aranacak_miktarlar.append(j)
            total_ayristirilan.append(ayristirilan)
            aranacak_hallet(False)
            del df,ayristirilan
        aranacak_hallet(True)
        gunluk_ulke_sayac=[{} for i in range(gecerli_miktar)]
        gunluk_sehir_sayac=[{} for i in range(gecerli_miktar)]
        ulke_basina={}
        for i in range(gecerli_miktar):
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
        corruption_arr=pl.read_csv("./data/corruption_data.csv")
        rol_pd=pl.read_csv("./data/rule_of_law.csv") # openpyxl, xlsx2csv
        rol={}
        baskentler=pl.read_csv("./data/countries.csv")
        for row in rol_pd.rows(named=True):
            if not row["country"] in country2cc:continue
            rol[country2cc[row["country"]]]=row["WorldJusticeProjectOverallScore"]
        savas=pl.read_csv("./data/war_data.csv",has_header=False)
        savas_dict={}
        for i in savas.rows():
            ilk=True
            for j in i:
                if ilk:
                    ilk=False
                    tarih=datetime.datetime(*map(int,j.split("-"))).timestamp()
                if j:
                    savas_dict[j]=tarih
        baskent_dict={}
        for i in baskentler.rows(named=True):
            baskent_dict[i["country"]]=i["capital"]
        corruption_dict = {}
        for row in corruption_arr.rows(named=True):corruption_dict[row["region_name"].strip()]=row["2021"]
        hdi_arr=pl.read_csv("./data/hdi.csv")
        hdi={}
        for row in hdi_arr.rows(named=True):hdi[row["country"]]=row["Hdi2022"]
        basin=pl.read_csv(source="./data/press.csv",separator=";",decimal_comma=True)
        basin_dict={}
        for row in basin.rows(named=True):
            basin_dict[row["Country_EN"]]=row["Score"]
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
        hafta_date=[son_tarih]
        for i in range(gecerli_miktar):
            surec(i,gecerli_miktar)
            tarih=veri_gunler[i]
            guncel_timestamp=tarih.timestamp()
            fark=guncel_timestamp-son_tarih
            while fark>=bir_hafta:
                son_tarih+=bir_hafta
                fark=guncel_timestamp-son_tarih
                hafta_date.append(son_tarih)
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
        surec(i,gecerli_miktar)
        header=["date","cc","data","capital","hdi","corruption","press","is_near_war","rol"]
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
                        baskent_dict[cc[j]]  if cc[j] in baskent_dict else "",
                        hdi[cc[j]] if cc[j] in hdi else 0.63,
                        1-(((corruption_dict[cc[j]] if cc[j] in corruption_dict else 50.3)-10)/88),
                        (basin_dict[cc[j]] if cc[j] in basin_dict else 55.86)/100,
                        cc[j] in savas_dict and hafta_date[sayac]>=savas_dict[cc[j]],
                        rol[j] if j in rol else 0.5
                    ])
                sayac+=1
        header=["date","cc","city","data"]
        with open("./data/city_data.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            sayac=0
            for i in hafta_sehir_array :
                for j in hafta_sehir_array[i]:
                    if len(j)==0:continue
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
        del veriler,gunluk_sehir_sayac,gunluk_ulke_sayac,hafta_sayilar,hafta_array
        print("Birleştirme bitiyor")
        gc.enable()
        gc.collect()
    print("Ülkeler okunuyor")
    country_df=pl.read_csv("./data/country_data.csv")
    country_df = country_df.with_columns(country_df["data"].str.json_decode().alias("data"))
    baskentler={}
    for row in country_df.rows(named=True):
        baskentler[row["cc"]]=row["capital"]
    print("Şehirler okunuyor")
    city_df=pl.read_csv("./data/city_data.csv")
    print("Şehirler ayrıştırılıyor")
    city_df = city_df.with_columns(city_df["data"].str.json_decode().alias("data"))
    yaptirilacaklar_list=[]
    yaptirilacaklar_veri={}
    for i in yaptirilacaklar:
        if yapilacaklar[i]:
            yaptirilacaklar_list.append(yaptirilacaklar[i])
    plot_miktar=list(map(lambda a:yapilacaklar[a],cizilecek)).count(True)
    plot_sayac=plot_miktar*100+20
    def sayi_al():
        global plot_sayac
        plot_sayac+=1
        return plot_sayac
    sayac=0
    
    miktar=city_df.shape[0]
    for row in city_df.iter_rows(named=True,buffer_size=250000):
        sayac+=1
        if sayac%10000==0:surec(sayac,miktar)
        for f in yaptirilacaklar_list:
            f(row,sayac)
    surec(sayac,miktar) # \r içeren satırı temizlemek için
    if yapilacaklar["koreleasyon"]:
        country_df = country_df.with_columns(country_df["data"].map_elements(lambda a:reduce(lambda acc,x:acc+list_oranla(x),a,0)/len(a),pl.Float64).alias("ratio"))
        country_df_pd=country_df.to_pandas()
        country_df_pd["ratio"]=np.log(1e-9+country_df_pd["ratio"])
        rat=country_df_pd["ratio"]
        country_df_pd["ratio"]=(rat-rat.min())/(rat.max()-rat.min())
        plt.subplot(sayi_al())
        del country_df_pd["data"],country_df_pd["is_near_war"]
        sb.heatmap(country_df_pd.corr(method="spearman",numeric_only=True), cmap="turbo", annot=True)
        plt.subplot(sayi_al())
        sb.violinplot(country_df_pd)
    if yapilacaklar["istatistik"]:
        print("Dönüşüm öncesi normal dağılıma uygunluk:")
        hedef=jammer_oranlar
        miktar=min(5000,len(hedef))
        hedef=random.sample(hedef,miktar)
        normal_test = stats.kstest(hedef,"norm")
        print("W:", normal_test.statistic)
        print("p:", normal_test.pvalue)
        mu, std = stats.norm.fit(hedef)
        fitted_data, fitted_lambda = stats.boxcox(hedef)
        print("Box-Cox:",fitted_lambda,"≈0") # -0.05, en yakını 0 https://stats.stackexchange.com/questions/18844
        print("Dönüşüm sonrası normal dağılıma uygunluk:")
        mapper=lambda x:np.log(x)
        hedef=list(map(mapper,jammer_oranlar))
        hedef=random.sample(hedef,min(5000,len(hedef)))
        normal_test = stats.kstest(hedef,"norm")
        print("W:", normal_test.statistic)
        print("p:", normal_test.pvalue)
        mu, std = stats.norm.fit(hedef)
        plt.subplot(sayi_al())
        plt.hist(jammer_oranlar, bins=50, density=True, alpha=0.7, color='g')
        ppf = stats.norm(loc=mu, scale=std).ppf # Inverse CDF
        y=np.sort(hedef)
        x = [ppf( i/(miktar+2) ) for i in range(1,miktar+1)]
        plt.subplot(sayi_al())
        plt.scatter(x, y)
        dmin, dmax = np.min([x,y]), np.max([x,y])
        diag = np.linspace(dmin, dmax, 1000)
        #standart doğru
        plt.plot(diag, diag, color='red', linestyle='--')

        plt.subplot(sayi_al())
        plt.hist(hedef, bins=50, density=True, alpha=0.7, color='g')
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = stats.norm.pdf(x, mu, std)
        plt.plot(x, p, 'k', linewidth=2)
    print("-"*30)
    if yapilacaklar["gun"]:
        # McNemar testi
        yeni()
        print("Haftanın günü hipotezi:")
        print("-"*30+"""
        H0: Ülkenin hafta içi jammer'dan etkilenen şehirleriyle hafta sonu etkilenen şehirleri arasında bir fark yoktur.

        H1: Ülkenin hafta içi jammer'dan etkilenen şehirleriyle hafta sonu etkilenen şehirleri farklıdır.

        """)
        A = B = C = 0
        hafta_ici_kume=set()
        hafta_sonu_kume=set()
        hafta_ici_arr=[]
        hafta_sonu_arr=[]
        ulkeler=list(hafta_ici.keys())
        ulkeler.extend(list(hafta_sonu.keys()))
        ulkeler=set(ulkeler)
        for ulke in ulkeler:
            hafta_ici_sehirler = hafta_ici[ulke]
            if not ulke in hafta_sonu: continue
            hafta_sonu_sehirler = hafta_sonu[ulke]
            hafta_ici_arr.append(len(hafta_ici_sehirler))
            hafta_sonu_arr.append(len(hafta_sonu_sehirler))

            # B ve C test için yetiyor
            A += len(hafta_ici_sehirler.intersection(hafta_sonu_sehirler))
            B += len(hafta_ici_sehirler - hafta_sonu_sehirler)
            C += len(hafta_sonu_sehirler - hafta_ici_sehirler)
            hafta_ici_kume|=hafta_ici_sehirler
            hafta_sonu_kume|=hafta_sonu_sehirler

        chi2 = ((B - C) ** 2) / (B + C)
        p_value = stats.chi2.sf(chi2, df=1)

        print("p:",p_value)
        if p_value < 0.05:
            print("\tHafta içi jammer'dan etkilenen şehirlerle hafta sonu etkilenen şehirler farklıdır.")
        else:
            print("\tHafta içi jammer'dan etkilenen şehirlerle hafta sonu etkilenenler arasında bir fark olduğu söylenemez")
        plt.subplot(sayi_al())
        venn2(subsets=[hafta_ici_kume, hafta_sonu_kume], set_labels=('Hafta içi', 'Hafta sonu'))
        plt.subplot(sayi_al())
        sb.violinplot({"Hafta İçi":hafta_ici_arr,"Hafta Sonu":hafta_sonu_arr})
    if yapilacaklar["savas"]:
        print("Savaş sınır hipotezi:")
        print("-"*30+"""
        H0: Ülkenin savaş halinde bir ülkeyle sınır komşusu olması GPS Jammer oranını etkilemez.

        H1: Savaş halindeki ülkelerle sınır komşusu olan ülkelerde GPS Jammer yoğunluğu diğer ülkelere göre fazladır

        """)
        farklar=[]
        savasta=[]
        total=[]
        for row in country_df.rows(named=True):
            total.append(row["ratio"])
            if row["is_near_war"]:
                savasta.append(row["ratio"])
        total_sample=random.sample(total,len(savasta))
        p_value=stats.wilcoxon(savasta,total_sample,alternative="greater").pvalue
        print("p:",p_value)
        if p_value < 0.05:
            print("\tSavaş halindeki ülkelerle sınır komşusu olan ülkelerde GPS Jammer yoğunluğu diğer ülkelerden fazladır.")
        else:
            print("\tÜlkenin savaş halinde bir ülkeyle sınır komşusu olması GPS Jammer oranını arttırdığı söylenemez.")
        sb.set(style='whitegrid')
        bas_df=pd.DataFrame()
        bas_df['Ortalama']=random.sample(total,len(savasta))
        bas_df['Savaşta']=savasta
        plt.subplot(sayi_al())
        sb.boxplot(data=bas_df)
        bas_df['Ortalama']=np.log(1e-9+bas_df['Ortalama'])
        bas_df['Savaşta']=np.log(1e-9+bas_df['Savaşta'])
        plt.subplot(sayi_al())
        sb.boxplot(data=bas_df)
    if yapilacaklar["baskent"]:
        print("Başkent hipotezi:")
        oranlanacak=[]
        sehir_siralanmis={i:sorted(list(map(list_oranla,ulke_basine_jammer_sehir[i].values()))) for i in ulke_basine_jammer_sehir}
        print("-"*30+"""
        H0: Ülkenin başkentiyle diğer şehirleri arasında GPS Jammer yoğunluğu açısından kayda değer fark yoktur.

        H1: Şehrin başkent olması, ülkedeki diğer şehirlere göre fazla oranda jammer bulunmasında etkilidir.

        """)
        gecerli=0
        total=0
        farklar=[]
        baskent_degerler=[]
        toplam_degerler=[]
        for i in sehir_siralanmis:
            ulke_oran=sehir_siralanmis[i]
            if not i in baskentler:continue
            #if not baskentler[i] in ulke_basine_jammer_sehir[i]: continue
            ulke_medyan=ulke_oran[len(ulke_oran)//2]
            baskent=list_oranla(ulke_basine_jammer_sehir[i][baskentler[i]]) if baskentler[i] in ulke_basine_jammer_sehir[i] else ulke_medyan
            farklar.append(baskent-ulke_medyan)
            baskent_degerler.append(baskent)
            toplam_degerler.append(ulke_medyan)

        farklar=np.array(farklar)
        positive_signs=np.sum(farklar > 0)
        negative_signs=np.sum(farklar < 0)
        n=positive_signs+negative_signs
        observed_signs=min(positive_signs, negative_signs)
        print("pozitif:",positive_signs,"negatif:",negative_signs,"n:",n)
        p_value=stats.binomtest(observed_signs, n, p=0.5, alternative='two-sided').pvalue
        print("p:",p_value)
        if p_value < 0.05:
            print("\tBaşkentteki GPS Jammer oranı diğer şehirlerdekinden kayda değer oranda farklıdır.")
        else:
            print("\tŞehrin başkent olmasının, şehirdeki GPS Jammer oranını değiştirdiği söylenemez.")
        sb.set(style='whitegrid')
        bas_df=pd.DataFrame()
        plt.subplot(sayi_al())
        bas_df['Ortalama']=toplam_degerler
        bas_df['Başkent']=baskent_degerler
        sb.boxplot(data=bas_df)
        plt.subplot(sayi_al())
        bas_df['Ortalama']=np.log(bas_df['Ortalama'])   
        bas_df['Başkent']=np.log(bas_df['Başkent'])
        sb.boxplot(data=bas_df)
    if yapilacaklar["video"]:
        genis_dict={"date":[]}
        max_miktar=0
        son_tarih=None
        for row in country_df.rows(named=True):
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
            max_miktar=max(max_miktar,len(genis_dict[cc]))
        to_delete=[]
        for i in genis_dict:
            if i!="date" and len(genis_dict[i])!=max_miktar:
                to_delete.append(i)
        for i in to_delete:del genis_dict[i]
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
    plt.show()