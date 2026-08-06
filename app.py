import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
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

# Başlık ve Üst Bilgi
st.title("💎 KÜRESEL ENTEGRASYONLU KAPALIÇARŞI & FAİZ BORSASI PANELİ")
st.markdown("---")

try:
    # 1. CANLI VERİLERİ KÜRESEL BORSALARDAN ALMA
    altin_ticker = yf.Ticker("GC=F")
    dolar_ticker = yf.Ticker("USDTRY=X")
    dx_ticker = yf.Ticker("DX-Y.NYB") # ABD Dolar Endeksi (DXY)
    
    df_ons = altin_ticker.history(period="60d", interval="1d")
    df_dolar = dolar_ticker.history(period="5d", interval="1d")
    df_dxy = dx_ticker.history(period="5d", interval="1d")

    if df_ons.empty or df_dolar.empty or df_dxy.empty:
        st.error("⚠️ Canlı veri hatası! Bağlantınızı kontrol edin.")
    else:
        # Anlık ham piyasa değerleri
        canli_ons = df_ons['Close'].iloc[-1]
        canli_dolar = df_dolar['Close'].iloc[-1]
        canli_dxy = df_dxy['Close'].iloc[-1]
        
        # Tarih Etiketleri
        bugun_tarih = df_ons.index[-1].strftime("%d.%m.%Y")
        dun_tarih = df_ons.index[-2].strftime("%d.%m.%Y")
        
        # Dün ve Bugün Karşılaştırma Verileri
        dun_ons = df_ons['Close'].iloc[-2]
        dun_dxy = df_dxy['Close'].iloc[-2]

        # Türkiye piyasası kalibre edilmiş fiyatları
        canli_gram = (canli_ons / 31.1034768) * canli_dolar
        altin_22_ayar = canli_gram * 0.916
        ceyrek_altin = canli_gram * 1.635
        yarim_altin  = ceyrek_altin * 2
        tam_altin    = ceyrek_altin * 4
        ata_altin    = canli_gram * 6.721
        resat_altin  = canli_gram * 6.735

        ons_degisim = ((canli_ons - dun_ons) / dun_ons) * 100

        # 2. TEKNİK ANALİZ GÖSTERGELERİ
        df_ons['RSI'] = ta.momentum.rsi(df_ons['Close'], window=14)
        guncel_rsi = df_ons['RSI'].iloc[-1]
        df_ons['SMA20'] = ta.trend.sma_indicator(df_ons['Close'], window=20)
        sma20 = df_ons['SMA20'].iloc[-1]

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
            neden_ozeti = "Fed Faizin Artmıyacağını Açıkladı Faizciler Altına Geçiyor Ve Emlak&Altın Piyasasını Güçlendiriyor."
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
        col_zaman.metric("🕒 Sistem Zamanı", anlik_zaman)
        col_fed.metric("🎯 FED Faiz Kararına", fed_sayaci)
        st.markdown("---")

        # Döviz ve Ons Bandı
        st.subheader("📊 Canlı Küresel Göstergeler")
        col_ons, col_dolar, col_dxy = st.columns(3)
        col_ons.metric("Canlı Ons Altın", f"${canli_ons:,.2f}", f"{ons_degisim:+.2f}%")
        col_dolar.metric("Canlı Dolar Kuru", f"{canli_dolar:.4f} TL")
        col_dxy.metric("Canlı Dolar Endeksi (DXY)", f"{canli_dxy:.2f}")
        st.markdown("---")

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
        tahmin_kutusu(f"**Yön:** {yarin_tahmin} \n\n **Özet Gerekçe:** {neden_ozeti}")
        st.markdown("---")

        # Karşılaştırma Tablosu
        st.subheader("🇺🇸 Amerika Piyasası Veri Karşılaştırması")
        data_karsilastirma = {
            "Tarih / Veri": [f"Dün ({dun_tarih})", f"Bugün ({bugun_tarih})"],
            "Ons Altın ($)": [f"${dun_ons:,.2f}", f"${canli_ons:,.2f}"],
            "Dolar Endeksi (DXY)": [f"{dun_dxy:.2f}", f"{canli_dxy:.2f}"]
        }
        st.table(pd.DataFrame(data_karsilastirma))
        st.markdown("---")

        # Banka Faiz Oranları
        st.subheader("🏦 Bankaların Güncel Mevduat Faiz Yüzdeleri (32 Gün)")
        df_banka = pd.DataFrame(bankalar)
        df_banka.columns = ["Banka Adı", "Hoş Geldin Faizi (%)", "Standart Faiz (%)"]
        st.dataframe(df_banka, use_container_width=True)

except Exception as e:
    st.error(f"Sistemde bir hata oluştu: {str(e)}")

# Sayfayı her 5 saniyede bir otomatik yenilemek için
time.sleep(5)
st.rerun()
