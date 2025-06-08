import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from sklearn.preprocessing import MinMaxScaler
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Rekomendasi Cafe Surabaya", layout="wide")
st.title("📍 Rekomendasi Cafe Terdekat di Surabaya")

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("dataset_cafe_surabaya.xlsx")

df = load_data()

# Deteksi lokasi user otomatis (via browser)
location = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition", key="get_location")

if location is None:
    st.warning("📍 Menunggu deteksi lokasi dari browser...")
    st.stop()

if 'coords' not in location:
    st.error("Gagal mendeteksi lokasi. Coba refresh halaman.")
    st.stop()

user_lat = location['coords']['latitude']
user_lng = location['coords']['longitude']
user_location = (user_lat, user_lng)

st.success(f"Lokasi terdeteksi: Latitude {user_lat:.5f}, Longitude {user_lng:.5f}")

if st.button("🔍 Lihat Rekomendasi"):
    # Hitung jarak
    df['jarak_km'] = df.apply(lambda row: geodesic(user_location, (row['lat'], row['lng'])).km, axis=1)

    # Normalisasi
    scaler = MinMaxScaler()
    df['rating_norm'] = scaler.fit_transform(df[['rating']])
    df['jarak_norm'] = scaler.fit_transform(df[['jarak_km']])

    # Skor
    df['skor_rekomendasi'] = 0.7 * df['rating_norm'] + 0.3 * (1 - df['jarak_norm'])

    df_sorted = df.sort_values(by='skor_rekomendasi', ascending=False).head(5)

    st.markdown("### ✅ Rekomendasi Teratas:")
    for _, row in df_sorted.iterrows():
        st.markdown(f"""
        **{row['name']}**  
        📍 {row['address']}  
        ⭐ Rating: {row['rating']}  
        🛣️ Jarak: {row['jarak_km']:.2f} km  
        [🗺️ Lihat di Google Maps]({row['google_maps_url']})  
        ---
        """)

