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
                return pd.DataFrame(columns=["nis", "nama", "kelas", "prodi"])
            else:
                return pd.DataFrame(columns=["nis", "nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi"])

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
            h1, h2, h3, h4 = st.columns([1.5, 3, 4, 2])
            h1.markdown("**NIS**")
            h2.markdown("**Nama Siswa**")
            h3.markdown("**Status Kehadiran**")
            h4.markdown("**Nilai**")
            st.divider()

            list_input = []
            for i, row in df_filtered.iterrows():
                c1, c2, c3, c4 = st.columns([1.5, 3, 4, 2])
                c1.write(f"`{row['nis']}`")
                c2.write(f"**{row['nama']}**")
                stat = c3.radio(f"Status_{i}", ["Hadir", "Sakit", "Izin", "Alpa"], horizontal=True, key=f"rad_{i}", label_visibility="collapsed")
                nil = c4.number_input(f"Nilai_{i}", 0, 100, 0, key=f"num_{i}", label_visibility="collapsed")
                list_input.append([row['nis'], row['nama'], tgl.strftime('%Y-%m-%d'), tgl.strftime('%B'), stat, nil, stat, row['prodi']])

            st.divider()
            if st.button("SIMPAN SEMUA DATA PRODI INI", type="primary", use_container_width=True):
                with st.spinner("Menyimpan ke database..."):
                    df_rekap_baru = pd.DataFrame(list_input, columns=["nis", "nama_siswa", "tanggal", "bulan", "absensi", "nilai", "status", "prodi"])
                    df_rekap_lama = get_data("rekap")
                    df_final = pd.concat([df_rekap_lama, df_rekap_baru], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_final)
                    st.success(f"Alhamdulillah! Data {len(list_input)} siswa sudah masuk rekap.")

    elif menu == "Monitoring":
        st.header("📊 Hasil Absensi & Edit Data")
        df_rekap = get_data("rekap")
        if not df_rekap.empty:
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                prodi_list = ["Semua"] + sorted(df_rekap['prodi'].unique().tolist())
                pilihan = st.selectbox("Filter Tampilan Prodi:", prodi_list)
            df_tampil = df_rekap if pilihan == "Semua" else df_rekap[df_rekap['prodi'] == pilihan]
            with col_d2:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_tampil.to_excel(writer, index=False, sheet_name='Rekap')
                st.download_button(label="📥 Download", data=buffer.getvalue(), 
                                   file_name=f"rekap_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                   mime="application/vnd.ms-excel")
            st.divider()
            st.subheader("📝 Mode Edit Data")
            df_edited = st.data_editor(df_rekap, use_container_width=True, num_rows="dynamic")
            if st.button("💾 SIMPAN PERUBAHAN EDIT", type="primary", use_container_width=True):
                with st.spinner("Memperbarui data..."):
                    conn.update(spreadsheet=URL_SHEET, worksheet="rekap", data=df_edited)
                    st.success("Perubahan data berhasil disimpan!")
                    st.rerun()
        else:
            st.info("Belum ada data rekap.")

    elif menu == "Kelola Siswa":
        st.header("👥 Kelola Siswa")
        df_siswa = get_data("siswa")
        
        # --- Form Tambah Siswa ---
        with st.expander("➕ Tambah Siswa Baru"):
            with st.form("tambah_siswa"):
                nis = st.text_input("NIS Siswa")
                n = st.text_input("Nama Siswa")
                k = st.selectbox("Kelas", ["X", "XI", "XII"])
                p = st.text_input("Prodi", value="T. DKV")
                if st.form_submit_button("Simpan Siswa"):
                    df_baru = pd.DataFrame([[nis, n, k, p]], columns=["nis", "nama", "kelas", "prodi"])
                    df_final = pd.concat([df_siswa, df_baru], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_final)
                    st.success("Siswa Berhasil Ditambah!")
                    st.rerun()

        st.divider()
        st.subheader("📋 Daftar & Hapus Siswa")
        
        if not df_siswa.empty:
            for i, row in df_siswa.iterrows():
                c1, c2, c3, c4 = st.columns([2, 5, 2, 2])
                c1.write(f"`{row['nis']}`")
                c2.write(f"**{row['nama']}** ({row['prodi']})")
                if c4.button("🗑️ Hapus", key=f"del_{i}"):
                    # Proses Hapus
                    df_siswa_baru = df_siswa.drop(i)
                    conn.update(spreadsheet=URL_SHEET, worksheet="siswa", data=df_siswa_baru)
                    st.success(f"Siswa {row['nama']} berhasil dihapus!")
                    st.rerun()
        else:
            st.info("Belum ada data siswa.")

if __name__ == "__main__":
    main()
