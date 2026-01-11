import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import io

# --- KONFIGURASI GOOGLE SHEETS ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1__d7A0qCxtkxnJT8oYXbmZfY1GAiFcyB600fBNQaJV8/edit?usp=sharing"

def main():
    st.set_page_config(page_title="SMK YPPT Absensi Online", layout="wide")
    
    conn = st.connection("gsheets", type=GSheetsConnection)

    def get_data(nama_sheet):
        try:
            return conn.read(spreadsheet=URL_SHEET, worksheet=nama_sheet, ttl=0)
        except:
            if nama_sheet == "siswa":
                return pd.DataFrame(columns=["nama", "kelas", "prodi"])
            else:
                return pd.DataFrame(columns=["nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi"])

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

    menu = st.sidebar.radio("MENU", ["Input Absensi", "Monitoring", "Kelola Siswa"])
    if st.sidebar.button("Keluar"):
        st.session_state["authenticated"] = False
        st.rerun()

    if menu == "Input Absensi":
        st.header("📝 Input Absensi & Nilai")
        df_siswa = get_data("siswa")
        if df_siswa.empty:
            st.warning("Data siswa kosong.")
        else:
            st.subheader("🔍 Filter Kelompok Siswa")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                daftar_prodi = sorted(df_siswa['prodi'].unique())
                prodi_terpilih = st.selectbox("Pilih Program Keahlian (Prodi):", daftar_prodi)
            df_filtered = df_siswa[df_siswa['prodi'] == prodi_terpilih]
            with col_f2:
                tgl = st.date_input("Tanggal Pelaksanaan", datetime.now())
            
            st.info(f"Menampilkan {len(df_filtered)} siswa untuk Prodi: {prodi_terpilih}")
            st.divider()

            list_input = []
            for i, row in df_filtered.iterrows():
                c1, c2, c3 = st.columns([3, 4, 2])
                c1.write(f"**{row['nama']}**")
                stat = c2.radio(f"Status_{i}", ["Hadir", "Sakit", "Izin", "Alpa"], horizontal=True, key=f"rad_{i}")
                nil = c3.number_input(f"Nilai_{i}", 0, 100, 0, key=f"num_{i}")
                list_input.append([row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat, row['prodi']])

            if st.button("SIMPAN SEMUA DATA PRODI INI", type="primary", use_container_width=True):
                df_rekap_baru = pd.DataFrame(list_input, columns=["nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi"])
                df_rekap_lama = get_data("rekap")
                df_final = pd.concat([df_rekap_lama, df_rekap_baru], ignore_index=True)
                conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_final)
                st.success("Data Berhasil Disimpan!")

    elif menu == "Monitoring":
        st.header("📊 Hasil Absensi & Download")
        df_rekap = get_data("rekap")
        
        if not df_rekap.empty:
            # Filter tampilan
            prodi_list = ["Semua"] + sorted(df_rekap['prodi'].unique().tolist())
            pilihan = st.selectbox("Filter Tampilan Prodi:", prodi_list)
            
            df_tampil = df_rekap if pilihan == "Semua" else df_rekap[df_rekap['prodi'] == pilihan]
            
            # Tombol Download Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_tampil.to_excel(writer, index=False, sheet_name='Rekap_Absensi')
            
            st.download_button(
                label="📥 Download Rekap (Excel)",
                data=buffer.getvalue(),
                file_name=f"rekap_absensi_{pilihan}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
            
            st.dataframe(df_tampil, use_container_width=True)
        else:
            st.info("Belum ada data rekap.")

    elif menu == "Kelola Siswa":
        st.header("👥 Kelola Siswa")
        df_siswa = get_data("siswa")
        with st.form("tambah_siswa"):
            n = st.text_input("Nama Siswa")
            k = st.selectbox("Kelas", ["X", "XI", "XII"])
            p = st.text_input("Prodi", value="T. DKV")
            if st.form_submit_button("Simpan Siswa"):
                df_baru = pd.DataFrame([[n, k, p]], columns=["nama", "kelas", "prodi"])
                df_final = pd.concat([df_siswa, df_baru], ignore_index=True)
                conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_final)
                st.success("Siswa Berhasil Ditambah!")
                st.rerun()
        st.dataframe(df_siswa, use_container_width=True)

if __name__ == "__main__":
    main()
