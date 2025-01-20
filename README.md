# VBI

**VBI**, [Gpsjam](https://gpsjam.org) kaynağından elde edilen Jammer verilerini kullanarak, ülkelerdeki jammer oranının nelerden etkilendiğini incelemeyi amaçlayan bir projedir. Veri setinin işlenme verimliliğini artırmak amacıyla, projede çoğunlukla **Pandas** yerine **Polars** kütüphanesi tercih edilmiştir. Bu proje, ülkelerdeki **basın özgürlüğü endeksi**, **yolsuzluk**, **HDI (İnsani Gelişmişlik Endeksi)** ve **savaş içerisindeki ülkeler** gibi veri setlerinin, jammer oranlarıyla olan korelasyonunu incelemeyi hedefler.

Test ederken ilk çalıştırmadan önce `veriler.py` dosyasının, devamında `main.py` dosyasının çalıştırılması gerekiyor.