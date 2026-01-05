import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time
from fpdf import FPDF
import streamlit.components.v1 as components

# --- KONFIGURASI DATABASE ---
NAMA_DB = 'absensinilai_web.db'

def init_db():
    conn = sqlite3.connect(NAMA_DB)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS siswa (id INTEGER PRIMARY KEY, nama TEXT UNIQUE, kelas TEXT DEFAULT "X", prodi TEXT DEFAULT "Umum", nilai_akhir REAL DEFAULT 0)')
    c.execute('''CREATE TABLE IF NOT EXISTS rekap 
                 (id_siswa INTEGER, tanggal TEXT, bulan TEXT, absensi TEXT, nilai REAL, status TEXT DEFAULT "Hadir",
                  FOREIGN KEY(id_siswa) REFERENCES siswa(id))''')
    conn.commit()
    conn.close()

def export_to_pdf(df, judul):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "LAPORAN SMK YPPT GARUT", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 7, f"Data: {judul}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    
    cols_to_print = ["tanggal", "nama", "kelas", "prodi", "absensi", "nilai"]
    for col in cols_to_print:
        pdf.cell(31, 10, str(col).upper(), 1, 0, 'C', True)
    pdf.ln()
    
    pdf.set_font("Arial", '', 9)
    for _, row in df.iterrows():
        for col in cols_to_print:
            pdf.cell(31, 10, str(row[col]), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

def apply_custom_style():
    st.markdown("""
        <style>
        /* Background Utama */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                        url('https://images.unsplash.com/photo-1580582932707-520aed937b7b?q=80&w=1632&auto=format&fit=crop');
            background-size: cover;
        }
        
        /* Sidebar & Divider Emas */
        [data-testid="stSidebar"] {
            background-color: #1a1a1a !important;
            border-right: 2px solid #FFD700;
        }
        
        /* INI KUNCI DIVIDER EMAS */
        [data-testid="stSidebar"] hr {
            border: none;
            height: 1.5px;
            background: linear-gradient(90deg, transparent, #FFD700, transparent);
            opacity: 1 !important;
        }

        /* Teks Global */
        h1, h2, h3, p, span, label { color: white }

        /* Perapat Baris */
        [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
        .stRadio > div { margin-bottom: -20px !important; }
        .stNumberInput { margin-top: -10px !important; }
        </style>
    """, unsafe_allow_html=True)

def halaman_login():
    apply_custom_style()
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col_kiri, col_tengah, col_kanan = st.columns([2, 1, 2]) 
    with col_tengah:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>🎓 LOGIN ADMIN</h3>", unsafe_allow_html=True)
        st.divider()
        user = st.text_input(
            "Username", 
            placeholder="Username", 
            type="password",           # Membuat ketikan jadi bintang
            label_visibility="collapsed" # Menghilangkan tulisan 'Username' di atas box
        )
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True) # Jeda sedikit
        pwd = st.text_input(
            "Password", 
            placeholder="Password", 
            type="password",           # Membuat ketikan jadi bintang
            label_visibility="collapsed" # Menghilangkan tulisan 'Password' di atas box
        )
        if st.button("MASUK KE SISTEM", width='stretch', type="primary"):
            if user.strip() == "admin" and pwd.strip() == "yppt2026":
                st.session_state["authenticated"] = True
                import time
                st.rerun()
            else:
                st.error("Maaf Salah Username atau Password!")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 12px; margin-top: 20px;'>© 2026 BR DEVELOPER</p>", unsafe_allow_html=True)

def halaman_input():
    st.markdown("<h2 style='text-align: center; color: white;'>📝 INPUT KEGIATAN SISWA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFD700;'>Program Keahlian: T DKV - SMK YPPT Garut</p>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(NAMA_DB)
    df_siswa = pd.read_sql_query("SELECT * FROM siswa ORDER BY nama ASC", conn)
    conn.close()

    if df_siswa.empty:
        st.warning("Data siswa kosong!")
        return
    
    with st.container(border=True):
        col_tgl, col_bln = st.columns(2)
        with col_tgl:
            tgl = st.date_input("📅 Pilih Tanggal", datetime.now(), key="tgl_absen")
        with col_bln:
            bulan = st.selectbox("🌙 Bulan", ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'])
    
    with st.form("absen_form"):
        list_data = []
        for i, row in df_siswa.iterrows():
            col_nama, col_stat, col_nil = st.columns([3, 4, 2])
            col_nama.write(f"**{row['nama']}**")
            stat = col_stat.radio(f"S_{row['id']}", ["Hadir", "Sakit", "Alpa"], horizontal=True, label_visibility="collapsed")
            nil = col_nil.number_input(f"N_{row['id']}", 0, 100, 0, label_visibility="collapsed")
            list_data.append({'id': row['id'], 'stat': stat, 'nil': nil})
        
        if st.form_submit_button("💾 SIMPAN DATA", width='stretch'):
            conn = sqlite3.connect(NAMA_DB)
            curr = conn.cursor()
            for d in list_data:
                v_nil = d['nil'] if d['stat'] == "Hadir" else 0
                curr.execute("INSERT OR REPLACE INTO rekap (id_siswa, tanggal, bulan, absensi, nilai, status) VALUES (?,?,?,?,?,?)", 
                             (d['id'], tgl.strftime('%Y-%m-%d'), bulan, d['stat'], v_nil, d['stat']))
            conn.commit()
            conn.close()
            st.success("Berhasil!")

def main():
    st.set_page_config(page_title="SMK YPPT Absensi", layout="wide")
    init_db()

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        halaman_login()
    else:
        apply_custom_style()
        
        # --- SIDEBAR KINCLONG ---
        with st.sidebar:
            # 1. Logo Paling Atas
            _, col_logo, _ = st.columns([1, 2, 1])
            with col_logo:
                st.image("logo_yppt.png", width=110)
            
            # 2. Teks di Bawah Logo (Emas Menyala)
            st.markdown("""
                <div style='text-align: center; margin-top: 10px; margin-bottom: 20px;'>
                    <h2 style='
                        color: #FFD700 !important; 
                        font-family: sans-serif;
                        font-weight: 800; 
                        margin-bottom: 0px; 
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                        letter-spacing: 1px;
                        display: block;
                    '>SMK YPPT</h2>
                    <p style='color: #FFFFFF !important; margin-bottom: 0px; font-size: 14px; font-weight: bold;'>TERAKREDITASI : A</p>
                    <p style='color: #CCCCCC !important; font-size: 11px; font-style: italic;'>Jl. Nusa Indah No. 33, Tarogong Kidul, Garut</p>
                </div>
            """, unsafe_allow_html=True)
            st.divider()
        # 3. Navigasi
            menu = st.sidebar.radio("PILIHAN UTAMA ", ["Input Absensi", "Monitoring & Ekspor", "Kelola Siswa"])
            st.divider()
            if st.sidebar.button("🚪 Keluar (Log Out)", use_container_width=True):
                st.session_state["authenticated"] = False
                st.rerun()
            # st.divider()
        # --- 4. JAM DIGITAL & TANGGAL (KINCLONG) ---
            html_chat = """
            <div style="
                background: rgba(255, 215, 0, 0.1); 
                padding: 10px; 
                border-radius: 10px; 
                border: 1px solid rgba(255, 215, 0, 0.3);
                text-align: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            ">
                <div id="clock" style="
                    color: #FFD700; 
                    font-size: 24px; 
                    font-weight: bold;
                    text-shadow: 0px 0px 5px rgba(255, 215, 0, 0.5);
                ">00:00:00</div>
                <div id="date" style="color: white; font-size: 12px; margin-top: 3px;">Memuat Tanggal...</div>
            </div>

            <script>
                function updateClock() {
                    const now = new Date();
                    const hours = String(now.getHours()).padStart(2, '0');
                    const minutes = String(now.getMinutes()).padStart(2, '0');
                    const seconds = String(now.getSeconds()).padStart(2, '0');
                    document.getElementById('clock').textContent = hours + ":" + minutes + ":" + seconds;
                    
                    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                    document.getElementById('date').textContent = now.toLocaleDateString('id-ID', options);
                }
                setInterval(updateClock, 1000);
                updateClock();
            </script>
            """
            # Memanggil komponen HTML (height disesuaikan agar tidak ada scrollbar)
            components.html(html_chat, height=100)

        # --- LOGIKA MENU ---
        if menu == "Input Absensi":
            halaman_input()

        elif menu == "Monitoring & Ekspor":
            st.markdown("<h2 style='text-align: center;'>📊 MONITORING & EXPOR</h2>", unsafe_allow_html=True)
            conn = sqlite3.connect(NAMA_DB)
            df = pd.read_sql_query("SELECT rekap.rowid, siswa.nama, siswa.kelas, siswa.prodi, rekap.absensi, rekap.nilai, rekap.tanggal FROM rekap JOIN siswa ON rekap.id_siswa = siswa.id ORDER BY rekap.tanggal DESC", conn)
            conn.close()

            if not df.empty:
                edited = st.data_editor(df, width='stretch', hide_index=True)
                c1, c2 = st.columns(2)
                if c1.button("💾 SIMPAN PERUBAHAN", width='stretch'):
                    conn = sqlite3.connect(NAMA_DB)
                    for _, r in edited.iterrows():
                        conn.execute("UPDATE rekap SET absensi=?, nilai=? WHERE rowid=?", (r['absensi'], r['nilai'], r['rowid']))
                    conn.commit(); conn.close()
                    st.rerun()
                pdf = export_to_pdf(edited, "Laporan")
                c2.download_button("📄 Expor ke PDF", pdf, "Laporan.pdf", width='stretch')
            else:
                st.info("Data kosong")

        elif menu == "Kelola Siswa":
            st.markdown("<h2 style='text-align: center;'>👥 KELOLA DATA SISWA</h2>", unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["📥 Import Data (Excel/CSV)", "➕ Tambah Manual"])
            
            with tab1:
                st.markdown("### Import Data Siswa")
                st.info("Pastikan file memiliki kolom: **nama**, **kelas**, **prodi**")
                file_upload = st.file_uploader("Pilih file Excel atau CSV", type=['csv', 'xlsx'])
                
                if file_upload is not None:
                    try:
                        if file_upload.name.endswith('.csv'):
                            df_import = pd.read_csv(file_upload)
                        else:
                            df_import = pd.read_excel(file_upload)
                        
                        st.write("Pratinjau Data:")
                        st.dataframe(df_import.head(), width='stretch')
                        
                        if st.button("🚀 PROSES IMPORT SEKARANG", use_container_width=True):
                            conn = sqlite3.connect(NAMA_DB)
                            sukses = 0
                            gagal = 0
                            for _, row in df_import.iterrows():
                                try:
                                    conn.execute("INSERT INTO siswa (nama, kelas, prodi) VALUES (?, ?, ?)", 
                                               (row['nama'], row['kelas'], row['prodi']))
                                    sukses += 1
                                except:
                                    gagal += 1
                            conn.commit()
                            conn.close()
                            st.success(f"Berhasil mengimport {sukses} siswa! (Gagal/Duplikat: {gagal})")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")

            with tab2:
                st.markdown("### Tambah Siswa Manual")
                with st.form("tambah_siswa"):
                    nama_baru = st.text_input("Nama Lengkap")
                    kelas_baru = st.selectbox("Kelas", ["X", "XI", "XII"])
                    prodi_baru = st.text_input("Prodi (Contoh: T DKV)")
                    if st.form_submit_button("Simpan Siswa"):
                        if nama_baru:
                            conn = sqlite3.connect(NAMA_DB)
                            try:
                                conn.execute("INSERT INTO siswa (nama, kelas, prodi) VALUES (?, ?, ?)", 
                                           (nama_baru, kelas_baru, prodi_baru))
                                conn.commit()
                                st.success("Siswa berhasil ditambahkan!")
                            except:
                                st.error("Nama siswa sudah ada!")
                            conn.close()
                            st.rerun()
                
            # Tampilkan Daftar Siswa yang Ada
            st.divider()
            st.markdown("### Daftar Siswa Terdaftar")
            conn = sqlite3.connect(NAMA_DB)
            df_list = pd.read_sql_query("SELECT nama, kelas, prodi FROM siswa ORDER BY nama ASC", conn)
            conn.close()
            st.dataframe(df_list, width='stretch')
            st.info("Menu Kelola Siswa di sini.")

if __name__ == "__main__":

    main()

