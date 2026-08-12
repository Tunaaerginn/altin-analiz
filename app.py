import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import random 

st.set_page_config(page_title="Hatasız Altın Analiz Paneli", page_icon="💎", layout="wide") 

def get_finans_mottosu():
mottolar = [
"💰 'Fiyat ödediğiniz şeydir, değer ise aldığınız şey.' - Warren Buffett",
"⚖️ Altın sabırlı yatırımcıyı sever, ani kararlar kaybettirir.",
"📊 Trende karşı işlem yapmayın, teknik göstergeleri mutlaka takip edin.",
"🛡️ Portföy çeşitlendirmesi en büyük kalkanınızdır; tüm yumurtaları aynı sepete koymayınız.",
"🚀 Akıllı yatırımcı piyasa düşerken fırsat kollayandır."
]
return random.choice(mottolar) 

st.title("💎 KÜRESEL ENTEGRASYONLU FİZİKİ ALTIN & ANALİZ PANELİ")
st.markdown(f"*{get_finans_mottosu()}*")
st.markdown("---") 

sekme1, sekme2 = st.tabs(["📊 Canlı Takip Paneli", "🧠 Altın Bilgi Kütüphanesi"]) 

altin_ticker = yf.Ticker("GC=F")
dolar_ticker = yf.Ticker("USDTRY=X")
dx_ticker = yf.Ticker("DX-Y.NYB") 

df_ons = altin_ticker.history(period="60d", interval="1d")
df_dolar = dolar_ticker.history(period="5d", interval="1d")
df_dxy = dx_ticker.history(period="5d", interval="1d") 

if df_ons.empty or df_dolar.empty or df_dxy.empty:
st.error("⚠️ Küresel veri hatası! Bağlantınızı kontrol edin.")
else:
canli_ons = float(df_ons['Close'].iloc[-1])
canli_dolar = float(df_dolar['Close'].iloc[-1])
canli_dxy = float(df_dxy['Close'].iloc[-1])
dun_ons = float(df_ons['Close'].iloc[-2])
ons_degisim = ((canli_ons - dun_ons) / dun_ons) * 100 

### Matematiksel Türkiye Fiziki Altın Piyasası Formülleri

### Bankalar arası kur yerine serbest piyasa katsayıları ve işçilik primleri eklenmiştir.

saf_gram = (canli_ons / 31.1034768) * canli_dolar
canli_gram = saf_gram * 1.035 # %3.5 Kapalıçarşı / Fiziki prim eklemesi
altin_22_ayar = canli_gram * 0.916 * 0.985 # 22 Ayar işçilikli has karşılığı
ceyrek_altin = canli_gram * 1.754 * 1.025 # Darphane basım primi dahil
yarim_altin  = ceyrek_altin * 2
tam_altin    = ceyrek_altin * 4
ata_altin    = canli_gram * 7.216 * 1.02 

df_ons['RSI'] = ta.momentum.rsi(df_ons['Close'], window=14)
guncel_rsi = float(df_ons['RSI'].iloc[-1])
df_ons['SMA20'] = ta.trend.sma_indicator(df_ons['Close'], window=20)
sma20 = float(df_ons['SMA20'].iloc[-1]) 

puan = 0
if guncel_rsi < 35: puan += 1
elif guncel_rsi > 65: puan -= 1
if canli_ons > sma20: puan += 1
else: puan -= 1
if canli_dxy > 104.5: puan -= 1
else: puan += 1 

if puan >= 1:
yarin_tahmin = "YUKARI EĞİLİMLİ (DESTEKLENİYOR)"
tahmin_kutusu = st.success
neden_ozeti = "Küresel göstergeler (RSI ve SMA) yukarı yönlü ivmeyi onaylıyor. Fiziki piyasalarda güvenli liman talebi fiyatı destekliyor."
elif puan <= -1:
yarin_tahmin = "AŞAĞI EĞİLİMLİ (BASKILANIYOR)"
tahmin_kutusu = st.error
neden_ozeti = "ABD Dolar Endeksi güç kazanıyor. Kısa vadeli teknik kar satışları fiziki piyasada fiyatları baskılayabilir."
else:
yarin_tahmin = "YATAY / DENGELİ"
tahmin_kutusu = st.warning
neden_ozeti = "Ons tarafında net bir kırılma yok. İç piyasada fiyatlar yatay bantta dengeleniyor." 

st.sidebar.subheader("🚨 Canlı Fiyat Alarmı")
hedef_gram = st.sidebar.number_input("Hedef Gram Altın Fiyatı (TL):", min_value=0.0, value=0.0, step=10.0, key="alarm_input")
if hedef_gram > 0:
if canli_gram >= hedef_gram:
st.sidebar.success(f"🔔 ALARM: Gram Altın ({canli_gram:,.2f} TL) hedefinize ulaştı!")
else:
st.sidebar.info(f"⏳ {hedef_gram} TL olması bekleniyor...") 

st.sidebar.markdown("---")
st.sidebar.subheader("🧮 Altın Hesaplama Robotu")
hesap_turu = st.sidebar.selectbox("Altın Türü Seçin:", ["Gram Altın", "Çeyrek Altın", "Ata Altın"], key="calc_select")
altin_miktari = st.sidebar.number_input("Adet / Gram Miktarı:", min_value=0.0, value=1.0, step=1.0, key="calc_input") 

if hesap_turu == "Gram Altın":
toplam_tl = altin_miktari * canli_gram
elif hesap_turu == "Çeyrek Altın":
toplam_tl = altin_miktari * ceyrek_altin
else:
toplam_tl = altin_miktari * ata_altin 

st.sidebar.metric(f"Toplam Tutar", f"{toplam_tl:,.2f} TL")
st.sidebar.markdown("---") 

st.sidebar.subheader("💼 Kademeli Alım Portföyüm")
p_turu = st.sidebar.selectbox("Altın Türü:", ["Gram Altın", "Çeyrek Altın", "Ata Altın"], key="p_turu_select") 

st.sidebar.markdown("**1. Parça Alım**")
ade1 = st.sidebar.number_input("Miktar 1:", min_value=0.0, value=0.0, step=1.0, key="a1")
fiyat1 = st.sidebar.number_input("Alış Fiyatı 1:", min_value=0.0, value=0.0, step=10.0, key="f1") 

st.sidebar.markdown("**2. Parça Alım**")
adet2 = st.sidebar.number_input("Miktar 2:", min_value=0.0, value=0.0, step=1.0, key="a2")
fiyat2 = st.sidebar.number_input("Alış Fiyatı 2:", min_value=0.0, value=0.0, step=10.0, key="f2") 

st.sidebar.markdown("**3. Parça Alım**")
adet3 = st.sidebar.number_input("Miktar 3:", min_value=0.0, value=0.0, step=1.0, key="a3")
fiyat3 = st.sidebar.number_input("Alış Fiyatı 3:", min_value=0.0, value=0.0, step=10.0, key="f3") 

toplam_adet = ade1 + adet2 + adet3
toplam_maliyet = (ade1 * fiyat1) + (adet2 * fiyat2) + (adet3 * fiyat3)
with sekme1:
if toplam_adet > 0 and toplam_maliyet > 0:
ortalama_maliyet = toplam_maliyet / toplam_adet
if p_turu == "Gram Altın":
guncel_tek_fiyat = canli_gram
elif p_turu == "Çeyrek Altın":
guncel_tek_fiyat = ceyrek_altin
else:
guncel_tek_fiyat = ata_altin
anlik_toplam_deger = toplam_adet * guncel_tek_fiyat
kar_zarar_tl = anlik_toplam_deger - toplam_maliyet
kar_zarar_yuzde = (kar_zarar_tl / toplam_maliyet) * 100
st.subheader("💼 Anlık Portföy Durum Raporunuz")
k_col1, k_col2, k_col3 = st.columns(3)
k_col1.metric("Toplam Portföy Değeri", f"{anlik_toplam_deger:,.2f} TL")
k_col2.metric("Ortalama Maliyetiniz", f"{ortalama_maliyet:,.2f} TL", f"{toplam_adet} Adet/Gram")
k_col3.metric("Net Kâr / Zarar Statüsü", f"{kar_zarar_tl:,.2f} TL", f"{kar_zarar_yuzde:+.2f}%")
st.markdown("---")
st.subheader("📈 Küresel ve Yerel Anlık Göstergeler")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ons Altın ($)", f"{canli_ons:,.2f}", f"{ons_degisim:+.2f}%")
m2.metric("Fiziki Has Gram Altın", f"{canli_gram:,.2f} TL")
m3.metric("USD / TRY", f"{canli_dolar:,.2f} TL")
m4.metric("DXY (Dolar Endeksi)", f"{canli_dxy:,.2f}")
st.markdown("---")
st.subheader("🏛️ Türkiye Serbest Piyasa Fiziki Altın Fiyatları")
c1, c2, c3, c4 = st.columns(4)
c1.metric("22 Ayar Bilezik (Gram)", f"{altin_22_ayar:,.2f} TL")
c2.metric("Çeyrek Altın (Fiziki)", f"{ceyrek_altin:,.2f} TL")
c3.metric("Ata Altın (Cumhuriyet)", f"{ata_altin:,.2f} TL")
c4.metric("Yarım Altın (Fiziki)", f"{yarim_altin:,.2f} TL")
st.caption("⚠️ Bu fiyatlar küresel spot piyasa verilerine fiziki işçilik, sigorta ve darphane primleri eklenerek hesaplanmıştır.")
st.markdown("---")
st.subheader("🔮 Algoritmik Trend Eğilim Analizi (Yarın Tahmini)")
tahmin_kutusu(f"**Yarın İçin Yapay Eğilim Öngörüsü:** {yarin_tahmin}")
st.info(f"**Teknik Analiz Gerekçesi:** {neden_ozeti}")
with sekme2:
st.subheader("🧠 Temel Altın ve Finans Bilgileri")
st.write("Yatırım yaparken bilmeniz gereken altın türleri, saflık oranları ve standartlar:")
info_df = pd.DataFrame({
"Altın Türü": ["Has Altın (24 Ayar)", "22 Ayar Altın", "Ata / Cumhuriyet", "Çeyrek Altın"],
"Milyem (Saflık)": ["0.995 / 0.999", "0.916", "0.916", "0.916"],
"Ağırlık (Gram)": ["1.00g", "1.00g", "7.216g", "1.754g"],
"Kullanım Alanı": ["Külçe / Gram Yatırım", "Bilezik / Takı", "Devlet Darphane Yatırım", "Yastıkaltı Birikim"]
})
st.table(info_df)
st.markdown("💡 **RSI Nedir?** Göreceli Güç Endeksi, varlığın aşırı alınıp alınmadığını (65+ riskli) veya aşırı satılıp ucuzladığını (35- fırsat) gösteren bir momentum indikatörüdür.")
