import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from sklearn.preprocessing import MinMaxScaler

# Konfigurasi halaman
st.set_page_config(page_title="Rekomendasi Cafe Surabaya", page_icon="📍", layout="centered")

# Tambahkan CSS untuk support light dan dark mode
st.markdown("""
<style>
body {
    background-color: transparent;
}
h2 {
    text-align: center;
}

@media (prefers-color-scheme: dark) {
    h2 {
        color: white;
    }
    .cafe-box {
        background-color: #2c3e50;
        color: white;
    }
    .cafe-name {
        color: white;
    }
    .cafe-address {
        color: #ecf0f1;
    }
}
@media (prefers-color-scheme: light) {
    h2 {
        color: #2c3e50;
    }
    .cafe-box {
        background-color: #ecf0f1;
        color: black;
    }
    .cafe-name {
        color: black;
    }
    .cafe-address {
        color: black;
    }
}
</style>
""", unsafe_allow_html=True)

# Judul
st.markdown("<h2>📍 Rekomendasi Cafe Terdekat di Surabaya</h2>", unsafe_allow_html=True)

# Form input lokasi
with st.form(key='lokasi_form'):
    alamat_input = st.text_input("Masukkan alamat atau lokasi anda saat ini:", placeholder="Contoh: Tunjungan Plaza, Surabaya")
    submit = st.form_submit_button("🔍 Lihat Rekomendasi")

# Proses rekomendasi
if submit and alamat_input:
    with st.spinner("📡 Mencari lokasi Anda..."):
        geolocator = Nominatim(user_agent="cafe_locator")
        lokasi = geolocator.geocode(alamat_input)

    if lokasi:
        user_location = (lokasi.latitude, lokasi.longitude)
        st.success(f"✅ Prediksi Lokasi berhasil ditemukan: {lokasi.address}")

        try:
            df = pd.read_excel("dataset_cafe_surabaya.xlsx")
        except Exception as e:
            st.error(f"Gagal memuat dataset: {e}")
            st.stop()

        if 'lat' not in df.columns or 'lng' not in df.columns:
            st.error("Dataset tidak memiliki kolom 'lat' dan 'lng'.")
            st.stop()

        df['jarak_km'] = df.apply(
            lambda row: geodesic(user_location, (row['lat'], row['lng'])).km,
            axis=1
        )

        scaler = MinMaxScaler()
        df['rating_norm'] = scaler.fit_transform(df[['rating']])
        df['jarak_norm'] = scaler.fit_transform(df[['jarak_km']])

        df['skor_rekomendasi'] = 0.3 * df['rating_norm'] + 0.7 * (1 - df['jarak_norm'])

        df_sorted = df.sort_values(by='skor_rekomendasi', ascending=False).head(20)

        st.markdown("### ☕ Hasil Rekomendasi")

        for _, row in df_sorted.iterrows():
            st.markdown(f"""
            <div class="cafe-box" style="padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <div class="cafe-name" style="font-size: 18px; font-weight: bold;">{row['name']}</div>
                <div class="cafe-address">{row['address']}</div>
                <div>
                    <span style="color:#e67e22; font-weight:bold;">Rating: {row['rating']}</span> |
                    <span style="color:#27ae60; font-weight:bold;">Jarak: {row['jarak_km']:.2f} km</span>
                </div>
                📍 <a href="{row['google_maps_url']}" target="_blank">Lihat di Google Maps</a>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error("❌ Lokasi tidak ditemukan. Coba masukkan alamat yang lebih spesifik.")
