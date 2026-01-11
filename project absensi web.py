import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- KONFIGURASI GOOGLE SHEETS ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1__d7A0qCxtkxnJT8oYXbmZfY1GAiFcyB600fBNQaJV8/edit?usp=sharing"

def main():
    st.set_page_config(page_title="SMK YPPT Absensi Online", layout="wide")
    
    # Koneksi ke Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # --- FUNGSI INTERNAL (Harus di dalam main) ---
    def get_data_siswa():
        # Menggunakan format export agar lebih stabil
        url_csv = URL_SHEET.replace("/edit?usp=sharing", "/export?format=csv&gid=0")
        try:
            return pd.read_csv(url_csv)
        except:
            return pd.DataFrame(columns=["nama", "kelas", "prodi"])

    def simpan_rekap(df_baru):
        df_lama = conn.read(spreadsheet=URL_SHEET, worksheet="rekap")
        df_combined = pd.concat([df_lama, df_baru], ignore_index=True)
        conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_combined)

    # --- LOGIN ADMIN ---
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("<h3 style='text-align: center;'>🎓 LOGIN ADMIN</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.button("MASUK", use_container_width=True):
                if user == "admin" and pwd == "yppt2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Username atau Password Salah!")
        return

    # --- SIDEBAR & MENU ---
    st.sidebar.title(f"Halo, Abah")
    menu = st.sidebar.radio("MENU", ["Input Absensi", "Monitoring", "Kelola Siswa"])
    
    if st.sidebar.button("Keluar"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- LOGIKA MENU ---
    if menu == "Input Absensi":
        st.header("📝 Input Absensi")
        df_siswa = get_data_siswa()
        
        if df_siswa.empty:
            st.warning("Data siswa belum ada di Google Sheets.")
        else:
            tgl = st.date_input("Tanggal", datetime.now())
            list_input = []
            
            for i, row in df_siswa.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 4, 2])
                    col1.write(f"**{row['nama']}**")
                    stat = col2.radio(f"Status", ["Hadir", "Sakit", "Alpa"], horizontal=True, key=f"s_{i}")
                    nil = col3.number_input(f"Nilai", 0, 100, 0, key=f"n_{i}")
                    list_input.append([row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat])
                st.divider()
            
            if st.button("SIMPAN KE GOOGLE SHEETS", type="primary"):
                df_rekap_baru = pd.DataFrame(list_input, columns=["nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status"])
                simpan_rekap(df_rekap_baru)
                st.success("Data Berhasil Disimpan!")

    elif menu == "Monitoring":
        st.header("📊 Data Absensi di Google Sheets")
        try:
            df_rekap = conn.read(spreadsheet=URL_SHEET, worksheet="rekap")
            st.dataframe(df_rekap, use_container_width=True)
        except:
            st.error("Gagal membaca tab 'rekap'. Pastikan tab tersebut ada di Google Sheets.")

    elif menu == "Kelola Siswa":
        st.header("👥 Kelola Data Siswa")
        df_siswa = get_data_siswa()
        
        with st.expander("Tambah Siswa Baru"):
            with st.form("tambah"):
                n = st.text_input("Nama Siswa")
                k = st.selectbox("Kelas", ["X", "XI", "XII"])
                p = st.text_input("Prodi", value="T DKV")
                if st.form_submit_button("Simpan"):
                    df_baru = pd.DataFrame([[n, k, p]], columns=["nama", "kelas", "prodi"])
                    df_final = pd.concat([df_siswa, df_baru], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_final)
                    st.success("Siswa berhasil ditambah!")
                    st.rerun()
        
        st.subheader("Daftar Siswa Saat Ini")
        st.dataframe(df_siswa, use_container_width=True)

if __name__ == "__main__":
    main()
