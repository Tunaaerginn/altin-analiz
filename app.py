import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import random
from datetime import datetime

# Web sitesinin tarayıcı sekme ayarları
st.set_page_config(page_title="Altın & Faiz Analiz Paneli", page_icon="💎", layout="wide")

def fed_kalan_sure():
    # Bir sonraki FED faiz kararı: 29 Temmuz 2026 Saat 21:00 (TSİ)
    fed_tarihi = datetime(2026, 7, 29, 21, 0, 0)
    simdi = datetime.now()
    fark = fed_tarihi - simdi
    if fark.total_seconds() > 0:
        gun = fark.days
        saat = fark.seconds // 3600
        dakika = (fark.seconds % 3600) // 60
        return f"{gun} Gün, {saat} Saat, {dakika} Dk"
    return "Açıklanıyor/Açıklandı"

# Günlük Finans Mottosu Fonksiyonu
def get_finans_mottosu():
    mottolar = [
        "💰 'Fiyat ödediğiniz şeydir, değer ise aldığınız şey.' - Warren Buffett",
        "⚖️ Altın sabırlı yatırımcıyı sever, ani kararlar kaybettirir.",
        "📊 Trende karşı işlem yapmayın, teknik göstergeleri mutlaka takip edin.",
        "🛡️ Portföy çeşitlendirmesi en büyük kalkanınızdır; tüm yumurtaları aynı sepete koymayınız.",
        "🚀 Akıllı yatırımcı piyasa düşerken fırsat kollayandır."
    ]
    return random.choice(mottolar)

# Başlık ve Üst Bilgi
st.title("💎 KÜRESEL ENTEGRASYONLU KAPALIÇARŞI & FAİZ BORSASI PANELİ")
st.markdown(f"*{get_finans_mottosu()}*")
st.markdown("---")

# 1. CANLI VERİLERİ KÜRESEL BORSALARDAN ALMA
altin_ticker = yf.Ticker("GC=F")
dolar_ticker = yf.Ticker("USDTRY=X")
dx_ticker = yf.Ticker("DX-Y.NYB")

df_ons = altin_ticker.history(period="60d", interval="1d")
df_dolar = dolar_ticker.history(period="5d", interval="1d")
df_dxy = dx_ticker.history(period="5d", interval="1d")

if df_ons.empty or df_dolar.empty or df_dxy.empty:
    st.error("⚠️ Canlı veri hatası! Bağlantınızı kontrol edin.")
else:
    # Anlık ham piyasa değerleri
    canli_ons = float(df_ons['Close'].iloc[-1])
    canli_dolar = float(df_dolar['Close'].iloc[-1])
    canli_dxy = float(df_dxy['Close'].iloc[-1])
    
    # Tarih Etiketleri
    bugun_tarih = df_ons.index[-1].strftime("%d.%m.%Y")
    dun_tarih = df_ons.index[-2].strftime("%d.%m.%Y")
    
    # Dün ve Bugün Karşılaştırma Verileri
    dun_ons = float(df_ons['Close'].iloc[-2])
    dun_dxy = float(df_dxy['Close'].iloc[-2])

    # Türkiye piyasası tam kalibre edilmiş fiyatları (Harem ve Kuyumcular Odası Formülü)
    canli_gram = (canli_ons / 31.1034768) * canli_dolar
    altin_22_ayar = canli_gram * 0.916
    ceyrek_altin = canli_gram * 1.754 * 0.916
    yarim_altin  = ceyrek_altin * 2
    tam_altin    = ceyrek_altin * 4
    ata_altin    = canli_gram * 7.216 * 0.916 
    resat_altin  = canli_gram * 7.216 * 0.916 * 0.998

    ons_degisim = ((canli_ons - dun_ons) / dun_ons) * 100

    # 2. TEKNİK ANALİZ GÖSTERGELERİ
    df_ons['RSI'] = ta.momentum.rsi(df_ons['Close'], window=14)
    guncel_rsi = float(df_ons['RSI'].iloc[-1])
    df_ons['SMA20'] = ta.trend.sma_indicator(df_ons['Close'], window=20)
    sma20 = float(df_ons['SMA20'].iloc[-1])

    # Puanlama Mantığı
    puan = 0
    if guncel_rsi < 35: puan += 1
    elif guncel_rsi > 65: puan -= 1
    if canli_ons > sma20: puan += 1
    else: puan -= 1

    # 3. YARIN İÇİN TAHMİN ALGORİTMASI
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

    # 4. GÜNCEL BANKA FAİZ ORANLARI VERİSİ
    bankalar = [
        {"ad": "ON Dijital", "hosgeldin": 46.0, "standart": 40.0},
        {"ad": "Alternatif Bank", "hosgeldin": 46.0, "standart": 38.5},
        {"ad": "Odeabank", "hosgeldin": 45.5, "standart": 39.0},
        {"ad": "QNB Finansbank", "hosgeldin": 44.5, "standart": 37.0},
        {"ad": "Akbank", "hosgeldin": 42.5, "standart": 36.5},
        {"ad": "Ziraat Bankası", "hosgeldin": 35.0, "standart": 32.0}
    ]

    # 5. GÖRSEL ARAYÜZÜ OLUŞTURMA
    anlik_zaman = datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
    fed_sayaci = fed_kalan_sure()
    
    # Zaman ve Fed Sayacı Bandı
    col_zaman, col_fed = st.columns(2)
    col_zaman.metric("🕒 Canlı Sistem Zamanı (5s Yenilenir)", anlik_zaman)
    col_fed.metric("🎯 FED Faiz Kararına", fed_sayaci)
    st.markdown("---")

    # Döviz ve Ons Bandı
    st.subheader("📊 Canlı Küresel Göstergeler")
    col_ons, col_dolar, col_dxy = st.columns(3)
    col_ons.metric("Canlı Ons Altın", f"${canli_ons:,.2f}", f"{ons_degisim:+.2f}%")
    col_dolar.metric("Canlı Dolar Kuru", f"{canli_dolar:.4f} TL")
    col_dxy.metric("Canlı Dolar Endeksi (DXY)", f"{canli_dxy:.2f}")
    st.markdown("---")

    # --- YAN MENÜ: TEMİZLENMİŞ ALARM, HESAPLAYICI VE KADEMELİ PORTFÖY ---
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

    # KADEMELİ KÂR-ZARAR PORTFÖYÜ (TEMİZLENDİ)
    st.sidebar.subheader("💼 Kademeli Alım Portföyüm")
    p_turu = st.sidebar.selectbox("Altın Türü:", ["Has Gram (24A)", "Çeyrek Altın", "Ata Altın"], key="p_turu_select")
    
    st.sidebar.markdown("**1. Parça Alım**")
    adet1 = st.sidebar.number_input("Miktar 1:", min_value=0.0, value=0.0, step=1.0, key="a1")
    fiyat1 = st.sidebar.number_input("Alış Fiyatı 1:", min_value=0.0, value=0.0, step=10.0, key="f1")
    
    st.sidebar.markdown("**2. Parça Alım**")
    adet2 = st.sidebar.number_input("Miktar 2:", min_value=0.0, value=0.0, step=1.0, key="a2")
    fiyat2 = st.sidebar.number_input("Alış Fiyatı 2:", min_value=0.0, value=0.0, step=10.0, key="f2")

    st.sidebar.markdown("**3. Parça Alım**")
    adet3 = st.sidebar.number_input("Miktar 3:", min_value=0.0, value=0.0, step=1.0, key="a3")
    fiyat3 = st.sidebar.number_input("Alış Fiyatı 3:", min_value=0.0, value=0.0, step=10.0, key="f3")
    
    toplam_adet = adet1 + adet2 + adet3
    toplam_maliyet = (adet1 * fiyat1) + (adet2 * fiyat2) + (adet3 * fiyat3)
    
    if toplam_adet > 0 and toplam_maliyet > 0:
        ortalama_maliyet = toplam_maliyet / toplam_adet
        
        # Güncel borsa fiyat eşleşmesi
        if p_turu == "Has Gram (24A)":
            guncel_tek_fiyat = canli_gram
        elif p_turu == "Çeyrek Altın":
            guncel_tek_fiyat = ceyrek_altin
        else:
            guncel_tek_fiyat = ata_altin
            
        anlik_toplam_deger = toplam_adet * guncel_tek_fiyat
        kar_zarar_tl = anlik_toplam_deger - toplam_maliyet
        kar_zarar_yuzde = (kar_zarar_tl / toplam_maliyet) * 100
        
        st.sidebar.markdown("---")
        st.sidebar.metric("📊 Güncel Portföy Değeri", f"{anlik_toplam_deger:,.2f} TL")
        st.sidebar.text(f"Toplam Miktar: {toplam_adet:,.2f}")
        st.sidebar.text(f"Ort. Maliyet: {ortalama_maliyet:,.2f} TL")
        
        if kar_zarar_tl >= 0:
            st.sidebar.success(f"🟢 KÂRDASINIZ!\n\n Net Kâr: +{kar_zarar_tl:,.2f} TL \n\n Oran: %{kar_zarar_yuzde:,.2f}")
        else:
            st.sidebar.error(f"🔴 ZARARDASINIZ!\n\n Net Zarar: {kar_zarar_tl:,.2f} TL \n\n Oran: %{kar_zarar_yuzde:,.2f}")
            
    st.sidebar.markdown("---")

    # Kapalıçarşı Fiyatları
    st.subheader("💰 Gram ve Sarrafiye Fiyatları")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Has Altın (24 Ayar)", f"{canli_gram:,.2f} TL")
        st.caption(f"22 Ayar Gram Altın: {altin_22_ayar:,.2f} TL")
    with c2:
        st.metric("Çeyrek Altın", f"{ceyrek_altin:,.2f} TL")
        st.caption(f"Yarım Altın: {yarim_altin:,.2f} TL")
        st.caption(f"Tam (Ziynet) Altın: {tam_altin:,.2f} TL")
    with c3:
        st.metric("Ata (Cumhuriyet) Altın", f"{ata_altin:,.2f} TL")
        st.caption(f"Reşat Altın: {resat_altin:,.2f} TL")
    st.markdown("---")

    # Kısa Vadeli Tahmin
    st.subheader("🔮 Yarın İçin Kısa Vadeli Net Tahmin")
    st.markdown(f"**Yön:** {yarin_tahmin}")
    tahmin_kutusu(neden_ozeti)
st.markdown("---")# İnteraktif Teknik Analiz Grafiğist.subheader("📈 Ons Altın & SMA20 Grafik Analizi (Son 60 Gün)")df_grafik = df_ons[['Close', 'SMA20']].rename(columns={'Close': 'Ons Kapanış Fiyatı ($)', 'SMA20': '20 Günlük Ortalama (SMA20)'})st.line_chart(df_grafik)st.markdown("---")# Karşılaştırma Tablosust.subheader("🇺🇸 Amerika Piyasası Veri Karşılaştırması")data_karsilastirma = {"Tarih / Veri": [f"Dün ({dun_tarih})", f"Bugün ({bugun_tarih})"],"Ons Altın ($)": [f"${dun_ons:,.2f}", f"${canli_ons:,.2f}"],"Dolar Endeksi (DXY)": [f"{dun_dxy:.2f}", f"{canli_dxy:.2f}"]}st.table(pd.DataFrame(data_karsilastirma))st.markdown("---")# Banka Faiz Oranlarıst.subheader("🏦 Bankaların Güncel Mevduat Faiz Yüzdeleri (32 Gün)")df_banka = pd.DataFrame(bankalar)df_banka.columns = ["Banka Adı", "Hoş Geldin Faizi (%)", "Standart Faiz (%)"]st.dataframe(df_banka, use_container_width=True)
