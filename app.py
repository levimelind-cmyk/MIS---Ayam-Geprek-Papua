import streamlit as st
import pandas as pd
from datetime import date

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="SCM Ayam Geprek Papua", 
    page_icon="🍗", 
    layout="wide"
)

st.title("🍗 Sistem Otomatisasi SCM - Ayam Geprek Papua")
st.caption("Prototipe Modul Vibe Coding: Kalkulator Resep (BOM) & Inventori FEFO")

# 2. Sidebar Input Operasional (Product Owner / Admin)
st.sidebar.header("⚙️ Input Operasional Harian")
porsi_terjual = st.sidebar.number_input(
    "Target / Jumlah Porsi Terjual (Porsi):", 
    min_value=1, 
    value=100, 
    step=10
)

# 3. Tab Navigation
tab1, tab2, tab3 = st.tabs(["📋 BOM Explosion (Resep Baku)", "📦 Manajemen Stok FEFO", "🚨 Alert & Auto-PO Generator"])

# --- TAB 1: BOM EXPLOSION ---
with tab1:
    st.subheader("Kalkulator Kebutuhan Bahan Baku (Bill of Materials)")
    st.write(f"Perhitungan kebutuhan kotor (*Gross Needed*) untuk **{porsi_terjual} Porsi** Ayam Geprek:")
    
    # Matriks Resep Baku per Porsi
    bom_data = {
        "Bahan Baku": ["Daging Ayam", "Tepung Terigu", "Minyak Goreng", "Cabai Rawit", "Bumbu & Bawang"],
        "Takaran / Porsi": [0.200, 0.050, 0.030, 0.015, 0.010],
        "Satuan": ["kg", "kg", "Liter", "kg", "kg"]
    }
    df_bom = pd.DataFrame(bom_data)
    
    # Hitung BOM Explosion
    df_bom["Total Kebutuhan (Gross)"] = df_bom["Takaran / Porsi"] * porsi_terjual
    
    # Tampilkan Tabel BOM
    st.dataframe(
        df_bom.style.format({"Takaran / Porsi": "{:.3f}", "Total Kebutuhan (Gross)": "{:.2f}"}),
        use_container_width=True
    )

# --- TAB 2: STOK BATCH & FEFO ---
with tab2:
    st.subheader("Manajemen Batch Stok (First Expired, First Out)")
    st.write("Sistem otomatis memprioritaskan batch bahan baku yang mendekati tanggal kedaluwarsa:")
    
    # Data Simulasi Batch Stok di Gudang
    batch_data = [
        {"ID Batch": "BTC-001", "Bahan Baku": "Daging Ayam", "Stok (kg/L)": 8.0, "Tgl Kedaluwarsa": date(2026, 10, 14)},
        {"ID Batch": "BTC-002", "Bahan Baku": "Daging Ayam", "Stok (kg/L)": 15.0, "Tgl Kedaluwarsa": date(2026, 10, 20)},
        {"ID Batch": "BTC-003", "Bahan Baku": "Cabai Rawit", "Stok (kg/L)": 1.0, "Tgl Kedaluwarsa": date(2026, 10, 13)},
        {"ID Batch": "BTC-004", "Bahan Baku": "Cabai Rawit", "Stok (kg/L)": 3.5, "Tgl Kedaluwarsa": date(2026, 10, 18)},
        {"ID Batch": "BTC-005", "Bahan Baku": "Minyak Goreng", "Stok (kg/L)": 10.0, "Tgl Kedaluwarsa": date(2026, 11, 30)},
    ]
    df_batch = pd.DataFrame(batch_data)
    
    # Algoritma Pengurutan FEFO
    df_fefo = df_batch.sort_values(by="Tgl Kedaluwarsa", ascending=True)
    
    st.dataframe(df_fefo, use_container_width=True)

# --- TAB 3: ALERT & AUTO-PO ---
with tab3:
    st.subheader("Deteksi Stok Kritis & Draf Purchase Order")
    
    # Perhitungan Komparasi Stok Daging Ayam
    total_stok_ayam = df_batch[df_batch["Bahan Baku"] == "Daging Ayam"]["Stok (kg/L)"].sum()
    kebutuhan_ayam = df_bom[df_bom["Bahan Baku"] == "Daging Ayam"]["Total Kebutuhan (Gross)"].values[0]
    sisa_stok_ayam = total_stok_ayam - kebutuhan_ayam
    
    # Indikator Visual (Metrics)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Stok Ayam Gudang", f"{total_stok_ayam:.1f} kg")
    col2.metric("Kebutuhan Dapur (BOM)", f"{kebutuhan_ayam:.1f} kg")
    col3.metric("Estimasi Sisa Stok", f"{sisa_stok_ayam:.1f} kg", delta=f"{sisa_stok_ayam:.1f} kg")
    
    # Logic Peringatan Stok Kritis & Auto-PO
    safety_stock = 5.0  # Threshold Safety Stock (kg)
    
    if sisa_stok_ayam < safety_stock:
        st.error(f"⚠️ **PERINGATAN STOK KRITIS:** Sisa stok Daging Ayam ({sisa_stok_ayam:.1f} kg) di bawah Safety Stock ({safety_stock} kg)!")
        
        st.markdown("---")
        st.markdown("### 📄 Draf Purchase Order (Auto-Generated)")
        po_qty = max(20.0, kebutuhan_ayam * 1.5)
        
        st.info(f"""
        **PURCHASE ORDER (PO) - AYAM GEPREK PAPUA**  
        * **Supplier Target:** Supplier Ayam Segar Papua  
        * **Item Material:** Daging Ayam Fillet / Potong  
        * **Kuantitas Pesanan:** {po_qty:.1f} kg  
        * **Status:** Siap Dikirim via Telegram Bot  
        """)
        
        if st.button("📲 Simulasi Kirim PO ke WhatsApp / Telegram Supplier"):
            st.success("✅ Draf PO berhasil dikirimkan ke Telegram Bot Supplier!")
    else:
        st.success("✅ Seluruh stok bahan baku dalam kondisi aman di atas batas kritis.")
