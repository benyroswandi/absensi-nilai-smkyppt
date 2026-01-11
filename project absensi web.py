import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import io

# --- KONFIGURASI GOOGLE SHEETS ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1__d7A0qCxtkxnJT8oYXbmZfY1GAiFcyB600fBNQaJV8/edit?usp=sharing"

def main():
    st.set_page_config(page_title="SMK YPPT Absensi Online", layout="wide", page_icon="🎓")
    
    # --- CSS UNTUK PERCANTIK TAMPILAN ---
    st.markdown("""
        <style>
        /* Desain Box Login */
        .login-box {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0px 10px 25px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        /* Merapatkan baris di Header Login */
        .header-text {
            line-height: 1;
            margin-bottom: 20px;
        }
        /* Percantik Tombol */
        .stButton>button {
            border-radius: 10px;
            font-weight: bold;
            background-color: #007bff;
            color: white;
            height: 3em;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
        }
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
        }
        </style>
    """, unsafe_allow_html=True)

    conn = st.connection("gsheets", type=GSheetsConnection)

    def get_data(nama_sheet):
        try:
            return conn.read(spreadsheet=URL_SHEET, worksheet=nama_sheet, ttl=0)
        except:
            if nama_sheet == "siswa":
                return pd.DataFrame(columns=["nis", "nama", "kelas", "prodi"])
            else:
                return pd.DataFrame(columns=["nis", "nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi"])

    # --- LOGIN ADMIN ---
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        empty_col1, center_col, empty_col2 = st.columns([1, 1, 1])
        
        with center_col:
            st.markdown("<br><br>", unsafe_allow_html=True) 
            # HEADER LOGIN YANG DIRAPATKAN
            st.markdown("""
                <div class='header-text' style='text-align: center;'>
                    <h1 style='color: #ef4444; margin-bottom: 0;'>🎓 SMK YPPT</h1>
                    <h4 style='color: #ef4444; font-weight: bold; font-size: 1.1em; margin-top: 0;'>Sistem Absensi & Nilai Online</h4>
                    <h4 style='color: #ef4444; margin-top: 5px; margin-bottom: 5px;'>TP. 2025/2026</h4>
                </div>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div class='login-box'>", unsafe_allow_html=True)
                user = st.text_input("Username Admin")
                pwd = st.text_input("Password", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 MASUK KE SISTEM", use_container_width=True):
                    if user == "admin" and pwd == "yppt2026":
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("Username atau Password Salah!")
                st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- MENU (SETELAH LOGIN) ---
    st.sidebar.markdown("<h2 style='text-align: center; color: white;'>SMK YPPT</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align: center; color: #94a3b8;'>TP. 2025/2026</p>", unsafe_allow_html=True)
    st.sidebar.divider()
    menu = st.sidebar.radio("NAVIGASI MENU", ["📝 Input Absensi", "📊 Monitoring", "👥 Kelola Siswa"])
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Keluar Aplikasi", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- LOGIKA MENU ---
    if menu == "📝 Input Absensi":
        st.header("📝 Input Absensi & Nilai")
        df_siswa = get_data("siswa")
        if df_siswa.empty:
            st.warning("Data siswa belum ada. Silakan isi di menu Kelola Siswa.")
        else:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                daftar_prodi = sorted(df_siswa['prodi'].unique())
                prodi_terpilih = st.selectbox("Pilih Prodi/Jurusan:", daftar_prodi)
            df_filtered = df_siswa[df_siswa['prodi'] == prodi_terpilih]
            with col_f2:
                tgl = st.date_input("Tanggal", datetime.now())
            
            st.info(f"📋 Mengabsen {len(df_filtered)} siswa - {prodi_terpilih}")
            st.divider()
            
            h1, h2, h3, h4 = st.columns([1.5, 3, 4, 2])
            h1.markdown("**NIS**")
            h2.markdown("**Nama Siswa**")
            h3.markdown("**Status**")
            h4.markdown("**Nilai**")
            
            list_input = []
            for i, row in df_filtered.iterrows():
                st.markdown("<div style='padding: 5px;'>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1.5, 3, 4, 2])
                c1.write(f"`{row['nis']}`")
                c2.write(f"**{row['nama']}**")
                stat = c3.radio(f"S_{i}", ["Hadir", "Sakit", "Izin", "Alpa"], horizontal=True, key=f"rad_{i}", label_visibility="collapsed")
                nil = c4.number_input(f"N_{i}", 0, 100, 0, key=f"num_{i}", label_visibility="collapsed")
                list_input.append([row['nis'], row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat, row['prodi']])
                st.markdown("</div>", unsafe_allow_html=True)

            if st.button("💾 SIMPAN DATA SEKARANG", type="primary", use_container_width=True):
                with st.spinner("Proses simpan..."):
                    df_rekap_baru = pd.DataFrame(list_input, columns=["nis", "nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi"])
                    df_rekap_lama = get_data("rekap")
                    df_final = pd.concat([df_rekap_lama, df_rekap_baru], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_final)
                    st.success("Data berhasil diamankan ke Google Sheets!")

    elif menu == "📊 Monitoring":
        st.header("📊 Rekapitulasi Data")
        df_rekap = get_data("rekap")
        if not df_rekap.empty:
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                prodi_list = ["Semua Prodi"] + sorted(df_rekap['prodi'].unique().tolist())
                pilihan = st.selectbox("Tampilkan Berdasarkan Prodi:", prodi_list)
            df_tampil = df_rekap if pilihan == "Semua Prodi" else df_rekap[df_rekap['prodi'] == pilihan]
            
            with col_d2:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_tampil.to_excel(writer, index=False, sheet_name='Rekap')
                st.download_button(label="📥 Download Excel", data=buffer.getvalue(), 
                                   file_name=f"rekap_yppt_{datetime.now().strftime('%d%m%Y')}.xlsx",
                                   mime="application/vnd.ms-excel")
            
            st.subheader("📝 Edit atau Hapus Baris Rekap")
            df_edited = st.data_editor(df_rekap, use_container_width=True, num_rows="dynamic")
            if st.button("💾 UPDATE DATA REKAP", type="primary"):
                conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_edited)
                st.success("Rekap berhasil diperbarui!")
                st.rerun()
        else:
            st.info("Belum ada data di dalam rekap.")

    elif menu == "👥 Kelola Siswa":
        st.header("👥 Manajemen Data Siswa")
        df_siswa = get_data("siswa")
        
        with st.expander("➕ Tambah Siswa Baru"):
            with st.form("tambah_siswa"):
                c1, c2 = st.columns(2)
                nis = c1.text_input("NIS")
                n = c2.text_input("Nama Lengkap")
                k = c1.selectbox("Kelas", ["10", "11", "12"])
                p = c2.text_input("Prodi", value="T. Listrik")
                if st.form_submit_button("Simpan Siswa"):
                    df_baru = pd.DataFrame([[nis, n, k, p]], columns=["nis", "nama", "kelas", "prodi"])
                    df_final = pd.concat([df_siswa, df_baru], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_final)
                    st.success("Siswa ditambahkan!")
                    st.rerun()

        st.divider()
        if not df_siswa.empty:
            for i, row in df_siswa.iterrows():
                c1, c2, c3, c4 = st.columns([2, 5, 2, 2])
                c1.write(f"`{row['nis']}`")
                c2.write(f"**{row['nama']}**")
                c3.write(f"{row['prodi']}")
                if c4.button("🗑️", key=f"del_{i}"):
                    df_siswa_baru = df_siswa.drop(i)
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_siswa_baru)
                    st.rerun()

if __name__ == "__main__":
    main()




