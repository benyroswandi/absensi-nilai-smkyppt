import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
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
        [data-testid="stSidebar"] {
            background-color: #0f172a;
        }
        .sidebar-logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100px;
            margin-bottom: 10px;
        }
        .status-user {
            color: #10b981;
            font-size: 14px;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    conn = st.connection("gsheets", type=GSheetsConnection)
    waktu_sekarang = datetime.now() + timedelta(hours=7)

    def get_data(nama_sheet):
        try:
            return conn.read(spreadsheet=URL_SHEET, worksheet=nama_sheet, ttl=0)
        except:
            if nama_sheet == "siswa":
                return pd.DataFrame(columns=["nis", "nama", "kelas", "prodi"])
            else:
                return pd.DataFrame(columns=["nis", "nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi", "nama_guru", "mata_pelajaran"])

    # --- LOGIN ADMIN ---
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        empty_col1, center_col, empty_col2 = st.columns([1, 1, 1])
        with center_col:
            st.markdown("<br><br><br>", unsafe_allow_html=True) 
            st.markdown(f"<div style='text-align: center;'><h1 style='color: #ef4444;'>🎓 SMK YPPT</h1><p style='color: #ef4444; font-weight: bold;'>Sistem Absensi & Nilai Online</p></div>", unsafe_allow_html=True)
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

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<img src='{URL_LOGO}' class='sidebar-logo'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: white;'>SMK YPPT</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='status-user'>🟢 Admin Online<br>{waktu_sekarang.strftime('%d %b %Y')}</div>", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("NAVIGASI MENU", ["📝 Input Absensi", "📊 Monitoring", "📊 Rekap Bulanan", "👥 Kelola Siswa"])
        st.divider()
        if st.button("🚪 Keluar Aplikasi", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- LOGIKA MENU ---
    if menu == "📝 Input Absensi":
        st.header("📝 Input Absensi & Nilai")
        df_siswa = get_data("siswa")
        
        if df_siswa.empty:
            st.warning("Data siswa belum ada.")
        else:
            # BARIS 1: PRODI & NAMA GURU
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                prodi_terpilih = st.selectbox("Pilih Prodi/Jurusan:", sorted(df_siswa['prodi'].unique()))
            with col_a2:
                nama_guru = st.text_input("Nama Guru Pengajar:", placeholder="Contoh: Bpk. Beny")

            # BARIS 2: TANGGAL & MATA PELAJARAN
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                tgl = st.date_input("Tanggal Pelaksanaan", waktu_sekarang)
            with col_b2:
                mapel = st.text_input("Mata Pelajaran:", placeholder="Contoh: Instalasi Motor Listrik")
            
            df_filtered = df_siswa[df_siswa['prodi'] == prodi_terpilih]
            st.info(f"📋 Mengabsen {len(df_filtered)} siswa - {prodi_terpilih}")
            st.divider()

            if not nama_guru or not mapel:
                st.warning("⚠️ Mohon isi Nama Guru dan Mata Pelajaran terlebih dahulu!")

            h1, h2, h3, h4 = st.columns([1.5, 3, 4.5, 1.5])
            h1.markdown("**NIS**"); h2.markdown("**Nama Siswa**"); h3.markdown("**Status**"); h4.markdown("**Nilai**")
            
            list_input = []
            for i, row in df_filtered.iterrows():
                c1, c2, c3, c4 = st.columns([1.5, 3, 4.5, 1.5])
                c1.write(f"`{row['nis']}`"); c2.write(f"**{row['nama']}**")
                stat = c3.radio(f"S_{i}", ["Hadir", "Sakit", "Izin", "Alpa", "Kabur"], horizontal=True, key=f"rad_{i}", label_visibility="collapsed")
                nil = c4.number_input(f"N_{i}", 0, 100, 0, key=f"num_{i}", label_visibility="collapsed")
                # Data baru ditambahkan di sini: nama_guru dan mapel
                list_input.append([row['nis'], row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat, row['prodi'], nama_guru, mapel])

            if st.button("💾 SIMPAN DATA SEKARANG", type="primary", use_container_width=True):
                if not nama_guru or not mapel:
                    st.error("Gagal simpan! Nama Guru dan Mata Pelajaran wajib diisi.")
                else:
                    with st.spinner("Proses simpan..."):
                        df_rekap_baru = pd.DataFrame(list_input, columns=["nis", "nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi", "nama_guru", "mata_pelajaran"])
                        df_rekap_lama = get_data("rekap")
                        df_final = pd.concat([df_rekap_lama, df_rekap_baru], ignore_index=True)
                        conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_final)
                        st.success(f"Data absensi {mapel} berhasil disimpan!")

    elif menu == "📊 Monitoring":
        st.header("📊 Riwayat Harian (Semua Data)")
        df_rekap = get_data("rekap")
        if not df_rekap.empty:
            st.data_editor(df_rekap, use_container_width=True, num_rows="dynamic")
        else:
            st.info("Belum ada data rekapan.")

    elif menu == "📊 Rekap Bulanan":
        st.header("📊 Rekapitulasi Absensi Bulanan")
        df_rekap = get_data("rekap")
        if not df_rekap.empty:
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                bln = st.selectbox("Pilih Bulan:", sorted(df_rekap['bulan'].unique()))
            with col_r2:
                prd = st.selectbox("Pilih Prodi:", ["Semua Prodi"] + sorted(df_rekap['prodi'].unique().tolist()))
            
            df_f = df_rekap[df_rekap['bulan'] == bln]
            if prd != "Semua Prodi":
                df_f = df_f[df_f['prodi'] == prd]
            
            rekap_final = df_f.groupby(['nis', 'nama_siswa', 'prodi', 'absensi']).size().unstack(fill_value=0).reset_index()
            for col in ["Hadir", "Sakit", "Izin", "Alpa", "Kabur"]:
                if col not in rekap_final.columns: rekap_final[col] = 0
            
            rerata = df_f.groupby('nis')['nilai'].mean().reset_index()
            rekap_final = rekap_final.merge(rerata, on='nis').rename(columns={'nilai': 'Rata-rata Nilai'})
            st.dataframe(rekap_final, use_container_width=True)

    elif menu == "👥 Kelola Siswa":
        st.header("👥 Manajemen Data Siswa")
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
        st.subheader("🗑️ Hapus Data Siswa")
        if not df_siswa.empty:
            filter_prodi = st.selectbox("Filter Prodi untuk Hapus:", ["Tampilkan Semua"] + sorted(df_siswa['prodi'].unique().tolist()))
            df_view = df_siswa if filter_prodi == "Tampilkan Semua" else df_siswa[df_siswa['prodi'] == filter_prodi]
            for i, row in df_view.iterrows():
                c1, c2, c3, c4 = st.columns([2, 5, 2, 3])
                c1.write(f"`{row['nis']}`"); c2.write(f"**{row['nama']}**"); c3.write(f"{row['prodi']}")
                if c4.button(f"🗑️ HAPUS", key=f"del_{i}"):
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_siswa.drop(i))
                    st.rerun()

if __name__ == "__main__":
    main()
