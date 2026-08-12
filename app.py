import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import random
from datetime import datetime

### Web sitesinin tarayıcı sekme ayarları

st.set_page_config(page_title="Altın & Faiz Analiz Paneli", page_icon="💎", layout="wide") 

### Google'dan aldığınız API anahtarını doğrudan sisteme tanımlıyoruz

try:
client = genai.Client(api_key=st.secrets.get("65536", ""))
except:
pass 

def fed_kalan_sure(): 

# Bir sonraki FED faiz kararı güncellendi: 16 Eylül 2026 Saat 21:00 (TSİ)

fed_tarihi = datetime(2026, 9, 16, 21, 0, 0)
simdi = datetime.now()
fark = fed_tarihi - simdi
if fark.total_seconds() > 0:
gun = fark.days
saat = fark.seconds // 3600
dakika = (fark.seconds % 3600) // 60
return f"{gun} Gün, {saat} Saat, {dakika} Dk"
return "Açıklanıyor / Karar Günü"

def get_finans_mottosu():
mottolar = [
"💰 'Fiyat ödediğiniz şeydir, değer ise aldığınız şey.' - Warren Buffett",
"⚖️ Altın sabırlı yatırımcıyı sever, ani kararlar kaybettirir.",
"📊 Trende karşı işlem yapmayın, teknik göstergeleri mutlaka takip edin.",
"🛡️ Portföy çeşitlendirmesi en büyük kalkanınızdır; tüm yumurtaları aynı sepete koymayınız.",
"🚀 Akıllı yatırımcı piyasa düşerken fırsat kollayandır."
]
return random.choice(mottolar) 

st.title("💎 KÜRESEL ENTEGRASYONLU KAPALIÇARŞI & FAİZ BORSASI PANELİ")
st.markdown(f"*{get_finans_mottosu()}*")
st.markdown("---") 

sekme1, sekme2, sekme3 = st.tabs(["📊 Canlı Takip Paneli", "🧠 Altın Bilgi Kütüphanesi", "🤖 Yapay Zeka Danışmanı"]) 

altin_ticker = yf.Ticker("GC=F")
dolar_ticker = yf.Ticker("USDTRY=X")
dx_ticker = yf.Ticker("DX-Y.NYB") 

df_ons = altin_ticker.history(period="60d", interval="1d")
df_dolar = dolar_ticker.history(period="5d", interval="1d")
df_dxy = dx_ticker.history(period="5d", interval="1d") 

if df_ons.empty or df_dolar.empty or df_dxy.empty:
st.error("⚠️ Canlı veri hatası! Bağlantınızı kontrol edin.")
else:
anlik_zaman = datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
fed_sayaci = fed_kalan_sure() 

canli_ons = float(df_ons['Close'].iloc[-1])
canli_dolar = float(df_dolar['Close'].iloc[-1])
canli_dxy = float(df_dxy['Close'].iloc[-1])

bugun_tarih = df_ons.index[-1].strftime("%d.%m.%Y")
dun_tarih = df_ons.index[-2].strftime("%d.%m.%Y")

dun_ons = float(df_ons['Close'].iloc[-2])
dun_dxy = float(df_dxy['Close'].iloc[-2])

### --- KAPALIÇARŞI & YEREL SERBEST PİYASA DOĞRU FİYATLANDIRMA MOTORU ---

### Yalın bankalararası spot fiyata Türkiye fiziki makas aralığı ve katsayıları eklenmiştir.

spot_gram = (canli_ons / 31.1034768) * canli_dolar
canli_gram = spot_gram * 1.035 # Fiziki Kapalıçarşı primi
altin_22_ayar = canli_gram * 0.916 * 0.985 # İşçilik oranlı yerel 22 ayar bilezik karşılığı
ceyrek_altin = canli_gram * 1.754 * 1.025 # Darphane basım primi ve paketleme maliyeti dahil
yarim_altin  = ceyrek_altin * 2
tam_altin    = ceyrek_altin * 4
ata_altin    = canli_gram * 7.216 * 1.020 # Fiziki Cumhuriyet / Ata katsayısı
resat_altin  = canli_gram * 7.216 * 1.020 * 0.998 

ons_degisim = ((canli_ons - dun_ons) / dun_ons) * 100 

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
neden_ozeti = (
"Küresel piyasalarda teknik göstergeler (RSI ve Hareketli Ortalamalar) yukarı yönlü momentumu destekliyor. "
"Ons altındaki talep artışı ve destek seviyelerinin korunması, kısa vadeli yukarı yönlü eğilimi güçlendirmektedir.\n\n"
"**Uyanık Yatırımcı Özeti:** Altın 40k & 41k değerlerindeyken internet aracılığıyla 40K'dan alıp 41K'dan satıp kâr ettiği için, "
"altın her artış gösterdiğinde yüklü miktarda altın satılıyordu.\n\n"
"**Şimdiki Durum:** Altın hızla yükseldiği için uyanık yatırımcı 'Satarsam bir daha bu fiyattan geri alamam' korkusuyla "
"yüzleşiyor ve elindeki altını satmaya cesaret edemiyor."
)
elif puan <= -1:
yarin_tahmin = "AŞAĞI EĞİLİMLİ (BASKILANIYOR)"
tahmin_kutusu = st.error
neden_ozeti = "ABD Dolar Endeksi güçlü kalmaya devam ediyor ve teknik düzeltme başladı. Yarın altının kâr satışlarıyla geri çekilmesi beklenmektedir."
else:
yarin_tahmin = "YATAY / DENGELİ"
tahmin_kutusu = st.warning
neden_ozeti = "ABD piyasalarından net bir kırılma sinyali gelmedi. Altın yarın yatay ve kararsız bantta kalabilir." 

bankalar = [
{"ad": "ON Dijital", "hosgeldin": 46.0, "standart": 40.0},
{"ad": "Alternatif Bank", "hosgeldin": 46.0, "standart": 38.5},
{"ad": "Odeabank", "hosgeldin": 45.5, "standart": 39.0},
{"ad": "QNB Finansbank", "hosgeldin": 44.5, "standart": 37.0},
{"ad": "Akbank", "hosgeldin": 42.5, "standart": 36.5},
{"ad": "Ziraat Bankası", "hosgeldin": 35.0, "standart": 32.0}
] 

st.sidebar.subheader("🚨 Canlı Fiyat Alarmı")
hedef_gram = st.sidebar.number_input("Hedef Gram Altın Fiyatı (TL):", min_value=0.0, value=0.0, step=10.0, key="alarm_input")
if hedef_gram > 0:
if canli_gram >= hedef_gram:
st.sidebar.success(f"🔔 ALARM: Has Gram Altın ({canli_gram:,.2f} TL) hedefinize ulaştı!")
else:
st.sidebar.info(f"⏳ {hedef_gram} TL olması bekleniyor...")
st.sidebar.markdown("---")
st.sidebar.subheader("🧮 Altın Hesaplama Robotu")
hesap_turu = st.sidebar.selectbox("Altın Türü Seçin:", ["Has Gram (24A)", "Çeyrek Altın", "Ata Altın"], key="calc_select")
altin_miktari = st.sidebar.number_input("Adet / Gram Miktarı:", min_value=0.0, value=1.0, step=1.0, key="calc_input") 

if hesap_turu == "Has Gram (24A)":
toplam_tl = altin_miktari * canli_gram
elif hesap_turu == "Çeyrek Altın":
toplam_tl = altin_miktari * ceyrek_altin
else:
toplam_tl = altin_miktari * ata_altin 

st.sidebar.metric(f"Toplam Tutar", f"{toplam_tl:,.2f} TL")
st.sidebar.markdown("---") 

st.sidebar.subheader("💼 Kademeli Alım Portföyüm")
p_turu = st.sidebar.selectbox("Altın Türü:", ["Has Gram (24A)", "Çeyrek Altın", "Ata Altın"], key="p_turu_select") 

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
### --- 1. SAYFA: CANLI TAKİP PANELİ İÇERİĞİ ---

with sekme1:
col_zaman, col_fed = st.columns(2)
col_zaman.metric("🕒 Canlı Sistem Zamanı (5s Yenilenir)", anlik_zaman)
col_fed.metric("🎯 FED Faiz Kararına", fed_sayaci)
st.markdown("---") 

if toplam_adet > 0 and toplam_maliyet > 0:
ortalama_maliyet = toplam_maliyet / toplam_adet
if p_turu == "Has Gram (24A)":
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
k_col1.metric("Güncel Portföy Değeri", f"{anlik_toplam_deger:,.2f} TL")
k_col2.metric("Ortalama Maliyetiniz", f"{ortalama_maliyet:,.2f} TL", f"{toplam_adet} Adet")
k_col3.metric("Net Kâr / Zarar", f"{kar_zarar_tl:,.2f} TL", f"{kar_zarar_yuzde:+.2f}%")
st.markdown("---")

### Fiyat Kartları Display Alanı

st.subheader("📈 Küresel ve Yerel Canlı Göstergeler")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ons Altın ($)", f"{canli_ons:,.2f}", f"{ons_degisim:+.2f}%")
m2.metric("24K Has Gram Altın", f"{canli_gram:,.2f} TL")
m3.metric("USD / TRY", f"{canli_dolar:,.2f} TL")
m4.metric("DXY (Dolar Endeksi)", f"{canli_dxy:,.2f}") 

st.markdown("---")
st.subheader("🏛️ Kapalıçarşı Serbest Piyasa Fiziki Altın Fiyatları")
c1, c2, c3, c4 = st.columns(4)
c1.metric("22 Ayar Bilezik (Gram)", f"{altin_22_ayar:,.2f} TL")
c2.metric("Çeyrek Altın", f"{ceyrek_altin:,.2f} TL")
c3.metric("Ata Altın", f"{ata_altin:,.2f} TL")
c4.metric("Reşat Altın", f"{resat_altin:,.2f} TL") 

st.markdown("---")
st.subheader("🔮 Algoritmik Trend Eğilim Analizi (Yarın Tahmini)")
tahmin_kutusu(f"**Yarın İçin Yapay Eğilim Öngörüsü:** {yarin_tahmin}")
st.info(f"**Teknik Analiz Gerekçesi:** {neden_ozeti}") 

st.markdown("---")
st.subheader("🏦 Banka Vadeli Mevduat Faiz Oranları (Net Getiri)")
banka_df = pd.DataFrame(bankalar)
banka_df.columns = ["Banka Adı", "Hoşgeldin Oranı (%)", "Standart Faiz Oranı (%)"]
st.dataframe(banka_df, use_container_width=True) 

### --- 2. SAYFA: ALTIN BİLGİ KÜTÜPHANESİ ---

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
### --- 3. SAYFA: YAPAY ZEKA DANIŞMANI ---

with sekme3:
st.subheader("🤖 Yapay Zeka Piyasa Yorumcusu (Gemini)")
st.write("Koddaki entegrasyonu korumak için API bağlantınız üzerinden analiz üretebilirsiniz.") 

if st.button("✨ Hızlı Piyasa Raporu Üret"):
if 'client' not in locals() or client is None:
st.warning("⚠️ API Anahtarı tanımlanamadı. Lütfen secrets yapısını veya kodun üstündeki anahtar parametresini kontrol edin.")
else:
with st.spinner("Piyasa verileri analiz ediliyor..."):
try:
analiz_prompt = f"Ons: {canli_ons}, Dolar/TL: {canli_dolar}, Gram: {canli_gram:.2f}. Teknik RSI: {guncel_rsi:.2f}. Yatırım tavsiyesi vermeden kısa bir özet geç."
response = client.models.generate_content(model='gemini-2.5-flash', contents=analiz_prompt)
st.success("📊 Analiz Raporu Hazır!")
st.markdown(response.text)
except Exception as err:
st.error(f"Yapay zeka motorunda bir sorun oluştu: {err}")
