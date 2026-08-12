import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from google import genai
from google.genai import types 

st.set_page_config(page_title="İZKO Destekli Altın & Faiz Paneli", page_icon="💎", layout="wide") 

try:
client = genai.Client(api_key=st.secrets.get("GEMINI_API_KEY", ""))
except Exception as e:
client = None 

def fed_kalan_sure():
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

@st.cache_data(ttl=300)
def izko_fiyatlarini_cek():
fiyatlar = {
"Gram Altın": 0.0, "22 Ayar": 0.0, "Yeni Çeyrek": 0.0,
"Yeni Yarım": 0.0, "Yeni Ziynet": 0.0, "Ata Altın": 0.0
}
try:
url = "https://www.izko.org.tr/guncel-kur"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")
rows = soup.find_all("tr")
for row in rows:
cols = row.find_all("td")
if len(cols) >= 3:
urun_adi = cols.text.strip()
satis_str = cols.text.strip().replace(".", "").replace(",", ".").replace(" ₺", "")
try:
satis_fiyat = float(satis_str)
if urun_adi in fiyatlar:
fiyatlar[urun_adi] = satis_fiyat
except ValueError:
continue
return fiyatlar
except Exception as e:
return None 

st.title("💎 İZMİR KUYUMCULAR ODASI (İZKO) ENTEGRASYONLU ANALİZ PANELİ")
st.markdown(f"*{get_finans_mottosu()}*")
st.markdown("---") 

sekme1, sekme2, sekme3 = st.tabs(["📊 Canlı Takip Paneli", "🧠 Altın Bilgi Kütüphanesi", "🤖 Yapay Zeka Danışmanı"]) 

altin_ticker = yf.Ticker("GC=F")
dolar_ticker = yf.Ticker("USDTRY=X")
dx_ticker = yf.Ticker("DX-Y.NYB") 

df_ons = altin_ticker.history(period="60d", interval="1d")
df_dolar = dolar_ticker.history(period="5d", interval="1d")
df_dxy = dx_ticker.history(period="5d", interval="1d") 

izko_fiyatlari = izko_fiyatlarini_cek() 

if df_ons.empty or not izko_fiyatlari:
st.error("⚠️ İZKO veya Küresel piyasa verileri çekilemedi! İnternet bağlantınızı kontrol edin.")
else:
anlik_zaman = datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
fed_sayaci = fed_kalan_sure() 

canli_gram = izko_fiyatlari["Gram Altın"] if izko_fiyatlari["Gram Altın"] > 0 else ((float(df_ons['Close'].iloc[-1]) / 31.1034768) * float(df_dolar['Close'].iloc[-1]))
altin_22_ayar = izko_fiyatlari["22 Ayar"]
ceyrek_altin = izko_fiyatlari["Yeni Çeyrek"]
yarim_altin  = izko_fiyatlari["Yeni Yarım"]
tam_altin    = izko_fiyatlari["Yeni Ziynet"]
ata_altin    = izko_fiyatlari["Ata Altın"]

canli_ons = float(df_ons['Close'].iloc[-1])
canli_dolar = float(df_dolar['Close'].iloc[-1])
canli_dxy = float(df_dxy['Close'].iloc[-1])
dun_ons = float(df_ons['Close'].iloc[-2])
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
neden_ozeti = "Küresel piyasalarda RSI ve Hareketli Ortalamalar yukarı yönlü momentumu destekliyor. İZKO fiziki piyasalarında da talep güçlü."
elif puan <= -1:
yarin_tahmin = "AŞAĞI EĞİLİMLİ (BASKILANIYOR)"
tahmin_kutusu = st.error
neden_ozeti = "ABD Dolar Endeksi (DXY) güçlü kalmaya devam ediyor. Ons tarafında kâr satışları baskı yaratabilir."
else:
yarin_tahmin = "YATAY / DENGELİ"
tahmin_kutusu = st.warning
neden_ozeti = "Piyasalarda net bir kırılma sinyali yok. Fiyatlar dar bantta yatay hareket edebilir."

st.sidebar.subheader("🚨 Canlı Fiyat Alarmı")
hedef_gram = st.sidebar.number_input("Hedef Gram Altın Fiyatı (TL):", min_value=0.0, value=0.0, step=10.0, key="alarm_input")
if hedef_gram > 0:
if canli_gram >= hedef_gram:
st.sidebar.success(f"🔔 ALARM: İZKO Gram Altın ({canli_gram:,.2f} TL) hedefinize ulaştı!")
else:
st.sidebar.info(f"⏳ {hedef_gram} TL olması bekleniyor...")

st.sidebar.markdown("---")
st.sidebar.subheader("🧮 Altın Hesaplama Robotu")
hesap_turu = st.sidebar.selectbox("Altın Türü Seçin:", ["Gram Altın (İZKO)", "Çeyrek Altın", "Ata Altın"], key="calc_select")
altin_miktari = st.sidebar.number_input("Adet / Gram Miktarı:", min_value=0.0, value=1.0, step=1.0, key="calc_input")

if hesap_turu == "Gram Altın (İZKO)":
toplam_tl = altin_miktari * canli_gram
elif hesap_turu == "Çeyrek Altın":
toplam_tl = altin_miktari * ceyrek_altin
else:
toplam_tl = altin_miktari * ata_altin

st.sidebar.metric(f"Toplam Tutar", f"{toplam_tl:,.2f} TL")
st.sidebar.markdown("---")

st.sidebar.subheader("💼 Kademeli Alım Portföyüm")
p_turu = st.sidebar.selectbox("Altın Türü:", ["Gram Altın (İZKO)", "Çeyrek Altın", "Ata Altın"], key="p_turu_select")

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
col_zaman.metric("🕒 Canlı Sistem Zamanı", anlik_zaman)
col_fed.metric("🎯 Bir Sonraki FED Faiz Kararına", fed_sayaci)
st.markdown("---") 

### Portföy Durum Raporu Alanı

if toplam_adet > 0 and toplam_maliyet > 0:
ortalama_maliyet = toplam_maliyet / toplam_adet
if p_turu == "Gram Altın (İZKO)":
guncel_tek_fiyat = canli_gram
elif p_turu == "Çeyrek Altın":
guncel_tek_fiyat = ceyrek_altin
else:
guncel_tek_fiyat = ata_altin 

anlik_toplam_deger = toplam_adet * guncel_tek_fiyat
kar_zarar_tl = anlik_toplam_deger - toplam_maliyet
kar_zarar_yuzde = (kar_zarar_tl / toplam_maliyet) * 100

st.subheader("💼 Anlık Portföy Durum Raporunuz (İZKO Verilerine Göre)")
k_col1, k_col2, k_col3 = st.columns(3)
k_col1.metric("Toplam Portföy Değeri", f"{anlik_toplam_deger:,.2f} TL")
k_col2.metric("Ortalama Maliyetiniz", f"{ortalama_maliyet:,.2f} TL", f"{toplam_adet} Adet/Gram")
k_col3.metric("Net Kâr / Zarar Statüsü", f"{kar_zarar_tl:,.2f} TL", f"{kar_zarar_yuzde:+.2f}%")
st.markdown("---")

### Fiyat Kartları

st.subheader("📈 Küresel ve Yerel Anlık Göstergeler")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ons Altın ($)", f"{canli_ons:,.2f}", f"{ons_degisim:+.2f}%")
m2.metric("İZKO Gram Altın", f"{canli_gram:,.2f} TL")
m3.metric("USD / TRY", f"{canli_dolar:,.2f} TL")
m4.metric("DXY (Dolar Endeksi)", f"{canli_dxy:,.2f}") 

st.markdown("---")
st.subheader("🏛️ İzmir Kuyumcular Odası (İZKO) Fiziki Altın Fiyatları")
c1, c2, c3, c4 = st.columns(4)
c1.metric("22 Ayar Bilezik (Gram)", f"{altin_22_ayar:,.2f} TL")
c2.metric("Yeni Çeyrek Altın", f"{ceyrek_altin:,.2f} TL")
c3.metric("Ata Altın", f"{ata_altin:,.2f} TL")
c4.metric("Yeni Ziynet (Tam)", f"{tam_altin:,.2f} TL")
st.caption("⚠️ Fiyatlar izko.org.tr üzerinden anlık olarak çekilmektedir ve bilgilendirme amaçlıdır.") 

st.markdown("---")
st.subheader("🔮 Algoritmik Trend Eğilim Analizi (Yarın Tahmini)")
tahmin_kutusu(f"**Yarın İçin Yapay Eğilim Öngörüsü:** {yarin_tahmin}")
st.info(f"**Teknik Analiz Gerekçesi:** {neden_ozeti}") 

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

st.markdown("💡 **RSI Nedir?** Göreceli Güç Endeksi, varlığın aşırı alınıp alınmadığını (65+ riskli/pahalı) veya aşırı satılıp ucuzladığını (35- fırsat/ucuz) gösteren bir momentum indikatörüdür.")

### --- 3. SAYFA: YAPAY ZEKA DANIŞMANI ---

with sekme3:
st.subheader("🤖 Gemini Yapay Zeka Piyasa Yorumcusu")
st.write("Anlık İZKO fiyatları ile küresel indikatör verilerini Gemini modeline göndererek profesyonel bir analiz raporu oluşturabilirsiniz.") 

if st.button("✨ Yapay Zeka Analiz Raporu Oluştur"):
if not client:
st.warning("⚠️ API Anahtarı bulunamadı. Lütfen Streamlit Secrets ayarlarına 'GEMINI_API_KEY' ekleyin.")
else:
with st.spinner("Yapay zeka piyasayı yorumluyor, lütfen bekleyin..."):
try:
analiz_prompt = f"""
Bir finansal analist gibi davran. Sana güncel piyasa verilerini iletiyorum:
- Ons Altın fiyatı: {canli_ons} USD
- Dolar/TL kuru: {canli_dolar} TRY
- İZKO Gram Altın (24K) fiyatı: {canli_gram:.2f} TL
- İZKO Çeyrek Altın fiyatı: {ceyrek_altin:.2f} TL
- Dolar Endeksi (DXY): {canli_dxy}
- Altın RSI Değeri (14 Günlük): {guncel_rsi:.2f}
- Altın 20 Günlük Basit Hareketli Ortalama (SMA): {sma20:.2f}
            Bu verilere dayanarak makroekonomik riskleri, altındaki aşırı alım/satım durumunu (RSI'a bakarak) ve gram altındaki gidişatı özetleyen, yatırım tavsiyesi içermeyen 3 kısa maddelik stratejik bir piyasa analizi yaz.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=analiz_prompt,
            )
            st.success("📊 Yapay Zeka Analizi Tamamlandı!")
            st.markdown(response.text)
        except Exception as err:
            st.error(f"Yapay zeka yanıtı üretilirken bir hata oluştu: {err}")
