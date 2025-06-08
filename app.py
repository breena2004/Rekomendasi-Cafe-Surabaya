import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="Rekomendasi Cafe Surabaya", page_icon="📍", layout="centered")

# Ubah warna judul menjadi putih
st.markdown("<h2 style='text-align: center; color: white;'>📍 Rekomendasi Cafe Terdekat di Surabaya</h2>", unsafe_allow_html=True)

# Form input lokasi
with st.form(key='lokasi_form'):
    alamat_input = st.text_input("Masukkan alamat atau lokasi anda saat ini:", placeholder="Contoh: Tunjungan Plaza")
    submit = st.form_submit_button("🔍 Lihat Rekomendasi")

# Proses rekomendasi
if submit and alamat_input:
    with st.spinner("📡 Mencari lokasi Anda..."):
        geolocator = Nominatim(user_agent="cafe_locator")
        lokasi = geolocator.geocode(alamat_input)

    if lokasi:
        user_location = (lokasi.latitude, lokasi.longitude)
        st.success(f"✅ Prediksi Lokasi terdekat berhasil ditemukan: {lokasi.address}")

        # Load dataset café
        try:
            df = pd.read_excel("dataset_cafe_surabaya.xlsx")
        except Exception as e:
            st.error(f"Gagal memuat dataset: {e}")
            st.stop()

        # Pastikan kolom lat/lng ada
        if 'lat' not in df.columns or 'lng' not in df.columns:
            st.error("Dataset tidak memiliki kolom 'lat' dan 'lng'.")
            st.stop()

        # Hitung jarak dari user ke setiap cafe
        df['jarak_km'] = df.apply(
            lambda row: geodesic(user_location, (row['lat'], row['lng'])).km,
            axis=1
        )

        # Normalisasi rating dan jarak
        scaler = MinMaxScaler()
        df['rating_norm'] = scaler.fit_transform(df[['rating']])
        df['jarak_norm'] = scaler.fit_transform(df[['jarak_km']])

        # Skor rekomendasi gabungan
        df['skor_rekomendasi'] = 0.7 * df['rating_norm'] + 0.3 * (1 - df['jarak_norm'])

        # Ambil 5 terbaik
        df_sorted = df.sort_values(by='skor_rekomendasi', ascending=False).head(5)

        # Tampilkan hasil
        st.markdown("### ☕ Hasil Rekomendasi")

        for index, row in df_sorted.iterrows():
            st.markdown(f"""
            <div style="background-color: #ecf0f1; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <strong style="font-size: 18px; color: black;">{row['name']}</strong><br>
                <span style="color: black;">{row['address']}</span><br>
                <span style="color:#e67e22; font-weight:bold;">Rating: {row['rating']}</span> |
                <span style="color:#27ae60; font-weight:bold;">Jarak: {row['jarak_km']:.2f} km</span><br>
                📍 <a href="{row['google_maps_url']}" target="_blank">Lihat di Google Maps</a>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error("❌ Lokasi tidak ditemukan. Coba masukkan alamat yang lebih spesifik.")
