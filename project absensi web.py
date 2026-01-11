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

    # --- FUNGSI AMBIL DATA ---
    def get_data(nama_sheet):
        try:
            return conn.read(spreadsheet=URL_SHEET, worksheet=nama_sheet, ttl=0)
        except:
            if nama_sheet == "siswa":
                return pd.DataFrame(columns=["nama", "kelas", "prodi"])
            else:
                return pd.DataFrame(columns=["nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status"])

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

    # --- MENU ---
    menu = st.sidebar.radio("MENU", ["Input Absensi", "Monitoring", "Kelola Siswa"])
    if st.sidebar.button("Keluar"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- LOGIKA MENU ---
    if menu == "Input Absensi":
        st.header("📝 Input Absensi")
        df_siswa = get_data("siswa")
        
        if df_siswa.empty:
            st.warning("Data siswa kosong.")
        else:
            tgl = st.date_input("Tanggal", datetime.now())
            list_input = []
            for i, row in df_siswa.iterrows():
                col1, col2, col3 = st.columns([3, 4, 2])
                col1.write(f"**{row['nama']}**")
                stat = col2.radio(f"Status_{i}", ["Hadir", "Sakit", "Alpa"], horizontal=True, label_visibility="collapsed")
                nil = col3.number_input(f"Nilai_{i}", 0, 100, 0, label_visibility="collapsed")
                list_input.append([row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat])
                st.divider()
            
            if st.button("SIMPAN DATA", type="primary"):
                df_rekap_baru = pd.DataFrame(list_input, columns=["nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status"])
                df_rekap_lama = get_data("rekap")
                df_final = pd.concat([df_rekap_lama, df_rekap_baru], ignore_index=True)
                conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_final)
                st.success("Berhasil Simpan ke Google Sheets!")

    elif menu == "Monitoring":
        st.header("📊 Hasil Absensi")
        df_rekap = get_data("rekap")
        st.dataframe(df_rekap, use_container_width=True)

    elif menu == "Kelola Siswa":
        st.header("👥 Kelola Siswa")
        df_siswa = get_data("siswa")
        with st.form("tambah_siswa"):
            n = st.text_input("Nama Siswa")
            k = st.selectbox("Kelas", ["X", "XI", "XII"])
            p = st.text_input("Prodi", value="T DKV")
            if st.form_submit_button("Simpan Siswa"):
                df_baru = pd.DataFrame([[n, k, p]], columns=["nama", "kelas", "prodi"])
                df_final = pd.concat([df_siswa, df_baru], ignore_index=True)
                conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_final)
                st.success("Siswa Berhasil Ditambah!")
                st.rerun()
        st.dataframe(df_siswa, use_container_width=True)

if __name__ == "__main__":
    main()
