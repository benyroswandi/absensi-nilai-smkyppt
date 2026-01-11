import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import time

# --- KONFIGURASI GOOGLE SHEETS ---
# GANTI LINK DI BAWAH INI DENGAN LINK GOOGLE SHEETS ABAH
URL_SHEET = "https://https://docs.google.com/spreadsheets/d/1__d7A0qCxtkxnJT8oYXbmZfY1GAiFcyB600fBNQaJV8/edit?gid=0#gid=0"

def main():
    st.set_page_config(page_title="SMK YPPT Absensi Online", layout="wide")
    
    # Koneksi ke Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fungsi Ambil Data Siswa
    def get_data_siswa():
        return conn.read(spreadsheet=URL_SHEET, worksheet="siswa")

    # Fungsi Simpan Absensi
    def simpan_rekap(df_baru):
        df_lama = conn.read(spreadsheet=URL_SHEET, worksheet="rekap")
        df_combined = pd.concat([df_lama, df_baru], ignore_index=True)
        conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_combined)

    # --- LOGIN ADMIN (Sederhana) ---
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("<h3 style='text-align: center;'>🎓 LOGIN ADMIN</h3>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("MASUK"):
            if user == "admin" and pwd == "yppt2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Salah!")
        return

    # --- SIDEBAR & MENU ---
    menu = st.sidebar.radio("MENU", ["Input Absensi", "Monitoring", "Kelola Siswa"])
    
    if st.sidebar.button("Keluar"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- LOGIKA MENU ---
    if menu == "Input Absensi":
        st.header("📝 Input Absensi")
        df_siswa = get_data_siswa()
        
        if df_siswa.empty:
            st.warning("Data siswa belum ada. Silakan tambah di menu Kelola Siswa.")
        else:
            tgl = st.date_input("Tanggal", datetime.now())
            list_input = []
            
            for i, row in df_siswa.iterrows():
                col1, col2, col3 = st.columns([3, 4, 2])
                col1.write(row['nama'])
                stat = col2.radio(f"Status_{i}", ["Hadir", "Sakit", "Alpa"], horizontal=True, key=f"s_{i}")
                nil = col3.number_input(f"Nilai_{i}", 0, 100, 0, key=f"n_{i}")
                list_input.append([row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat])
            
            if st.button("SIMPAN KE GOOGLE SHEETS"):
                df_rekap_baru = pd.DataFrame(list_input, columns=["nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status"])
                simpan_rekap(df_rekap_baru)
                st.success("Data Berhasil Disimpan di Google Drive!")

    elif menu == "Monitoring":
        st.header("📊 Data Absensi di Google Sheets")
        df_rekap = conn.read(spreadsheet=URL_SHEET, worksheet="rekap")
        st.dataframe(df_rekap, use_container_width=True)

    elif menu == "Kelola Siswa":
        st.header("👥 Kelola Data Siswa")
        df_siswa = get_data_siswa()
        
        # Tambah Siswa Manual
        with st.expander("Tambah Siswa Baru"):
            with st.form("tambah"):
                n = st.text_input("Nama")
                k = st.selectbox("Kelas", ["X", "XI", "XII"])
                p = st.text_input("Prodi")
                if st.form_submit_button("Simpan"):
                    df_baru = pd.DataFrame([[n, k, p]], columns=["nama", "kelas", "prodi"])
                    df_final = pd.concat([df_siswa, df_baru], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_final)
                    st.success("Siswa ditambah!")
                    st.rerun()
        
        st.dataframe(df_siswa, use_container_width=True)
        st.info("Data ini tersambung langsung ke Google Sheets Abah.")

if __name__ == "__main__":
    main()

