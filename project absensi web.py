import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
import io

# --- KONFIGURASI GOOGLE SHEETS ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1__d7A0qCxtkxnJT8oYXbmZfY1GAiFcyB600fBNQaJV8/edit?usp=sharing"
URL_LOGO = "https://raw.githubusercontent.com/benyroswandi/absensi-nilai-smkyppt/main/logo_yppt.png"

def main():
    st.set_page_config(page_title="SMK YPPT - Absensi & Nilai", layout="wide", page_icon="🎓")
    
    st.markdown("""
        <style>
        .login-box { background-color: #ffffff; padding: 25px; border-radius: 15px; box-shadow: 0px 10px 25px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
        .stButton>button { border-radius: 10px; font-weight: bold; background-color: #ef4444; color: white; height: 3em; }
        [data-testid="stSidebar"] { background-color: #0f172a; }
        .sidebar-logo { display: block; margin-left: auto; margin-right: auto; width: 100px; margin-bottom: 10px; }
        .status-user { color: #10b981; font-size: 14px; text-align: center; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    conn = st.connection("gsheets", type=GSheetsConnection)
    waktu_sekarang = datetime.now() + timedelta(hours=7)

    def get_data(nama_sheet):
        try:
            return conn.read(spreadsheet=URL_SHEET, worksheet=nama_sheet, ttl=0)
        except:
            return pd.DataFrame()

    # --- LOGIN ---
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        empty_col1, center_col, empty_col2 = st.columns([1, 1, 1])
        with center_col:
            st.markdown("<br><br>", unsafe_allow_html=True) 
            st.markdown(f"<div style='text-align: center;'><h1 style='color: #ef4444;'>🎓 SMK YPPT</h1><p style='font-weight: bold;'>Sistem Absensi & Nilai Online</p></div>", unsafe_allow_html=True)
            with st.container():
                st.markdown("<div class='login-box'>", unsafe_allow_html=True)
                st.info("Silakan masukkan akun admin sekolah")
                user = st.text_input("Username")
                pwd = st.text_input("Password", type="password")
                if st.button("🚀 MASUK KE SISTEM", use_container_width=True):
                    if user == "admin" and pwd == "yppt2026":
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("Akun tidak ditemukan!")
                st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<img src='{URL_LOGO}' class='sidebar-logo'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: white;'>SMK YPPT</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='status-user'>🟢 Status: Online<br>{waktu_sekarang.strftime('%d %b %Y')}</div>", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("MENU UTAMA", ["📝 Input Absensi", "📊 Monitoring Harian", "📊 Rekap Bulanan", "👥 Kelola Siswa"])
        st.divider()
        if st.button("🚪 Keluar", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- LOGIKA MENU ---
    if menu == "📝 Input Absensi":
        st.header("📝 Input Absensi & Nilai")
        df_siswa = get_data("siswa")
        
        if df_siswa.empty:
            st.warning("Data siswa belum ada.")
        else:
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                prodi_terpilih = st.selectbox("Pilih Prodi/Jurusan:", sorted(df_siswa['prodi'].unique()))
            with col_a2:
                nama_guru = st.text_input("Nama Guru Pengajar:")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                tgl = st.date_input("Tanggal", waktu_sekarang)
            with col_b2:
                mapel = st.text_input("Mata Pelajaran:")
            
            df_filtered = df_siswa[df_siswa['prodi'] == prodi_terpilih]
            st.divider()

            if not nama_guru or not mapel:
                st.warning("⚠️ Mohon isi Nama Guru dan Mata Pelajaran untuk mengaktifkan tabel absensi.")
            else:
                h1, h2, h3, h4 = st.columns([1.5, 3, 4.5, 1.5])
                h1.markdown("**NIS**"); h2.markdown("**Nama Siswa**"); h3.markdown("**Status**"); h4.markdown("**Nilai**")
                
                list_input = []
                for i, row in df_filtered.iterrows():
                    c1, c2, c3, c4 = st.columns([1.5, 3, 4.5, 1.5])
                    c1.write(f"`{row['nis']}`"); c2.write(f"**{row['nama']}**")
                    stat = c3.radio(f"S_{i}", ["Hadir", "Sakit", "Izin", "Alpa", "Kabur"], horizontal=True, key=f"rad_{i}", label_visibility="collapsed")
                    nil = c4.number_input(f"N_{i}", 0, 100, 0, key=f"num_{i}", label_visibility="collapsed")
                    list_input.append([row['nis'], row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat, row['prodi'], nama_guru, mapel])

                if st.button("💾 SIMPAN DATA", type="primary", use_container_width=True):
                    with st.spinner("Menyimpan ke sistem..."):
                        df_rekap_baru = pd.DataFrame(list_input, columns=["nis", "nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi", "nama_guru", "mata_pelajaran"])
                        df_rekap_lama = get_data("rekap")
                        df_final = pd.concat([df_rekap_lama, df_rekap_baru], ignore_index=True)
                        conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_final)
                        st.success(f"Berhasil! Data absensi {mapel} telah tersimpan.")
                        st.balloons()

    elif menu == "📊 Monitoring Harian":
        st.header("📊 Riwayat Absensi")
        df_rekap = get_data("rekap")
        if not df_rekap.empty:
            st.data_editor(df_rekap, use_container_width=True)
        else:
            st.info("Belum ada riwayat.")

    elif menu == "📊 Rekap Bulanan":
        st.header("📊 Rekapitulasi Bulanan")
        df_rekap = get_data("rekap")
        if not df_rekap.empty:
            col_r1, col_r2 = st.columns(2)
            bln = col_r1.selectbox("Pilih Bulan:", sorted(df_rekap['bulan'].unique()))
            prd = col_r2.selectbox("Pilih Prodi:", ["Semua"] + sorted(df_rekap['prodi'].unique().tolist()))
            
            df_f = df_rekap[df_rekap['bulan'] == bln]
            if prd != "Semua": df_f = df_f[df_f['prodi'] == prd]
            
            rekap_final = df_f.groupby(['nis', 'nama_siswa', 'prodi', 'absensi']).size().unstack(fill_value=0).reset_index()
            for col in ["Hadir", "Sakit", "Izin", "Alpa", "Kabur"]:
                if col not in rekap_final.columns: rekap_final[col] = 0
            
            rerata = df_f.groupby('nis')['nilai'].mean().reset_index()
            rekap_final = rekap_final.merge(rerata, on='nis').rename(columns={'nilai': 'Rata-rata Nilai'})
            st.dataframe(rekap_final, use_container_width=True)

    elif menu == "👥 Kelola Siswa":
        st.header("👥 Data Siswa")
        df_siswa = get_data("siswa")
        with st.expander("➕ Tambah Siswa Baru"):
            with st.form("tambah"):
                c1, c2 = st.columns(2)
                nis, n = c1.text_input("NIS"), c2.text_input("Nama Lengkap")
                k, p = c1.selectbox("Kelas", ["10", "11", "12"]), c2.text_input("Prodi")
                if st.form_submit_button("Simpan"):
                    df_baru = pd.DataFrame([[nis, n, k, p]], columns=["nis", "nama", "kelas", "prodi"])
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=pd.concat([df_siswa, df_baru]))
                    st.rerun()

        st.divider()
        if not df_siswa.empty:
            filt = st.selectbox("Cari berdasarkan Prodi:", ["Semua"] + sorted(df_siswa['prodi'].unique().tolist()))
            df_v = df_siswa if filt == "Semua" else df_siswa[df_siswa['prodi'] == filt]
            for i, row in df_v.iterrows():
                c1, c2, c3, c4 = st.columns([2, 5, 2, 3])
                c1.write(f"`{row['nis']}`"); c2.write(f"**{row['nama']}**"); c3.write(f"{row['prodi']}")
                if c4.button(f"🗑️ Hapus", key=f"d_{i}"):
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_siswa.drop(i))
                    st.rerun()

if __name__ == "__main__":
    main()
