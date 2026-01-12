import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta # Tambah timedelta untuk selisih waktu
import io

# --- KONFIGURASI GOOGLE SHEETS ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1__d7A0qCxtkxnJT8oYXbmZfY1GAiFcyB600fBNQaJV8/edit?usp=sharing"

# --- URL LOGO GITHUB ABAH ---
URL_LOGO = "https://raw.githubusercontent.com/benyroswandi/absensi-nilai-smkyppt/main/logo_yppt.png"

def main():
    st.set_page_config(page_title="SMK YPPT Absensi Online", layout="wide", page_icon="🎓")
    
    # --- CSS UNTUK PERCANTIK TAMPILAN ---
    st.markdown("""
        <style>
        .login-box {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0px 10px 25px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        .stButton>button {
            border-radius: 10px;
            font-weight: bold;
            background-color: #ef4444; 
            color: white;
            height: 3em;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #b91c1c;
            transform: translateY(-2px);
        }
        [data-testid="stSidebar"] {
            background-color: #0f172a;
        }
        /* Style Logo Sidebar */
        .sidebar-logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100px;
            margin-bottom: 10px;
        }
        /* Status Login Style */
        .status-user {
            color: #10b981;
            font-size: 14px;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    conn = st.connection("gsheets", type=GSheetsConnection)

    # --- FUNGSI AMBIL WAKTU WIB ---
    # Menambah 7 jam dari waktu server (UTC) agar jadi WIB
    waktu_sekarang = datetime.now() + timedelta(hours=7)

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
            st.markdown("<br><br><br>", unsafe_allow_html=True) 
            st.markdown(f"""
                <div style='text-align: center;'>
                    <h1 style='color: #ef4444; margin-bottom: 0;'>🎓 SMK YPPT</h1>
                    <p style='color: #ef4444; font-weight: bold; font-size: 1.2em; margin-top: 5px;'>Sistem Absensi & Nilai Online</p>
                    <p style='color: #ef4444; margin-top: 5px; margin-bottom: 20px;'>TP. 2025/2026</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div class='login-box'>", unsafe_allow_html=True)
                user = st.text_input("Username Admin")
                pwd = st.text_input("Password", type="password")
                if st.button("🚀 MASUK KE SISTEM", use_container_width=True):
                    if user == "admin" and pwd == "yppt2026":
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("Username atau Password Salah!")
                st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- SIDEBAR (JAM DIHAPUS, DIGANTI STATUS) ---
    with st.sidebar:
        st.markdown(f"<img src='{URL_LOGO}' class='sidebar-logo'>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white; margin-bottom:0;'>SMK YPPT</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 5px;'>TP. 2025/2026</p>", unsafe_allow_html=True)
        
        # Pengganti Jam: Info Login
        st.markdown(f"<div class='status-user'>🟢 Admin Online<br>{waktu_sekarang.strftime('%d %b %Y')}</div>", unsafe_allow_html=True)
        
        st.divider()
        menu = st.sidebar.radio("NAVIGASI MENU", ["📝 Input Absensi", "📊 Monitoring & Edit", "👥 Kelola Siswa"])
        st.divider()
        
        if st.sidebar.button("🚪 Keluar Aplikasi", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- LOGIKA MENU ---
    if menu == "📝 Input Absensi":
        st.header("📝 Input Absensi & Nilai")
        df_siswa = get_data("siswa")
        if df_siswa.empty:
            st.warning("Data siswa belum ada.")
        else:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                prodi_terpilih = st.selectbox("Pilih Prodi/Jurusan:", sorted(df_siswa['prodi'].unique()))
            df_filtered = df_siswa[df_siswa['prodi'] == prodi_terpilih]
            with col_f2:
                # Tanggal default sudah disesuaikan ke WIB
                tgl = st.date_input("Tanggal Pelaksanaan", waktu_sekarang)
            
            st.info(f"📋 Mengabsen {len(df_filtered)} siswa - {prodi_terpilih}")
            st.divider()
            
            h1, h2, h3, h4 = st.columns([1.5, 3, 4, 2])
            h1.markdown("**NIS**"); h2.markdown("**Nama Siswa**"); h3.markdown("**Status**"); h4.markdown("**Nilai**")
            
            list_input = []
            for i, row in df_filtered.iterrows():
                c1, c2, c3, c4 = st.columns([1.5, 3, 4, 2])
                c1.write(f"`{row['nis']}`"); c2.write(f"**{row['nama']}**")
                stat = c3.radio(f"S_{i}", ["Hadir", "Sakit", "Izin", "Alpa"], horizontal=True, key=f"rad_{i}", label_visibility="collapsed")
                nil = c4.number_input(f"N_{i}", 0, 100, 0, key=f"num_{i}", label_visibility="collapsed")
                list_input.append([row['nis'], row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat, row['prodi']])

            if st.button("💾 SIMPAN DATA SEKARANG", type="primary", use_container_width=True):
                with st.spinner("Proses simpan..."):
                    df_rekap_baru = pd.DataFrame(list_input, columns=["nis", "nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi"])
                    df_rekap_lama = get_data("rekap")
                    df_final = pd.concat([df_rekap_lama, df_rekap_baru], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_final)
                    st.success("Data berhasil disimpan!")

    elif menu == "📊 Monitoring & Edit":
        st.header("📊 Rekapitulasi Data")
        df_rekap = get_data("rekap")
        if not df_rekap.empty:
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                pilihan = st.selectbox("Tampilkan Berdasarkan Prodi:", ["Semua Prodi"] + sorted(df_rekap['prodi'].unique().tolist()))
            df_tampil = df_rekap if pilihan == "Semua Prodi" else df_rekap[df_rekap['prodi'] == pilihan]
            
            with col_d2:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_tampil.to_excel(writer, index=False, sheet_name='Rekap')
                st.download_button(label="📥 Download Excel", data=buffer.getvalue(), 
                                   file_name=f"rekap_yppt_{datetime.now().strftime('%d%m%Y')}.xlsx",
                                   mime="application/vnd.ms-excel")
            
            st.data_editor(df_rekap, use_container_width=True, num_rows="dynamic")
        else:
            st.info("Belum ada data.")

    elif menu == "👥 Kelola Siswa":
        st.header("👥 Manajemen Data Siswa (Tambah & Hapus")
        df_siswa = get_data("siswa")
        with st.expander("➕ Tambah Siswa Baru"):
            with st.form("tambah_siswa"):
                c1, c2 = st.columns(2)
                nis, n = c1.text_input("NIS"), c2.text_input("Nama Lengkap")
                k, p = c1.selectbox("Kelas", ["10", "11", "12"]), c2.text_input("Prodi", value="T. Listrik")
                if st.form_submit_button("Simpan Siswa"):
                    df_baru = pd.DataFrame([[nis, n, k, p]], columns=["nis", "nama", "kelas", "prodi"])
                    df_final = pd.concat([df_siswa, df_baru], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_final)
                    st.rerun()

        st.divider()
        if not df_siswa.empty:
            for i, row in df_siswa.iterrows():
                c1, c2, c3, c4 = st.columns([2, 5, 2, 3])
                c1.write(f"`{row['nis']}`"); c2.write(f"**{row['nama']}**"); c3.write(f"{row['prodi']}")
                if c4.button(f"🗑️ HAPUS SISWA", key=f"del_{i}"):
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_siswa.drop(i))
                    st.rerun()

if __name__ == "__main__":
    main()




