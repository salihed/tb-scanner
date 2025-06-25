import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta

# --- Streamlit Sayfa Ayarları ---
st.set_page_config(
    page_title="Görev Takip Sistemi",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    .task-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: white;
    }
    .overdue {
        border-left: 4px solid #dc3545;
    }
    .due-today {
        border-left: 4px solid #ffc107;
    }
    .upcoming {
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Başlatma ---
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = 'Tümü'
if 'selected_filter' not in st.session_state:
    st.session_state.selected_filter = 'Bu Hafta'
if 'show_create_task' not in st.session_state:
    st.session_state.show_create_task = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- Google Sheets Yetkilendirme ---
try:
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=credentials)
    SHEET_ID = st.secrets["spreadsheet"]["id"]
except:
    st.error("Google Sheets bağlantısı kurulamadı. Lütfen ayarları kontrol edin.")
    st.stop()

SHEET_NAME = "Tasks"

# --- Sabit Kategoriler ---
CATEGORIES = ["Arıza", "Bakım", "Satınalma", "Satış", "Operasyon", "Eğitim", "NDIGITAL", "5S&Kaizen", "Kavramsal"]

# --- Google Sheets Fonksiyonları ---
def read_sheet(range_):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=range_
        ).execute()
        values = result.get("values", [])
        if not values:
            return pd.DataFrame()
        
        headers = values[0] if values else []
        data_rows = values[1:] if len(values) > 1 else []
        
        if not data_rows:
            return pd.DataFrame(columns=headers if headers else get_required_columns())
        
        max_cols = len(headers) if headers else len(get_required_columns())
        normalized_rows = []
        for row in data_rows:
            normalized_row = row[:]
            while len(normalized_row) < max_cols:
                normalized_row.append("")
            normalized_row = normalized_row[:max_cols]
            normalized_rows.append(normalized_row)
        
        if headers:
            df = pd.DataFrame(normalized_rows, columns=headers)
        else:
            df = pd.DataFrame(normalized_rows, columns=get_required_columns())
        
        return df
        
    except Exception as e:
        st.error(f"Google Sheets'ten okunamadı: {e}")
        return pd.DataFrame()

def get_required_columns():
    return ["ID", "Başlık", "Sorumlu", "Sorumlu Email", "Kategori", "Termin", "Durum", "Açıklama", "Oluşturulma Tarihi", "Tamamlanma Tarihi"]

def write_sheet(range_name, values):
    try:
        clean_values = []
        for row in values:
            clean_row = []
            for cell in row:
                if pd.isna(cell) or cell == 'NaN' or str(cell) == 'nan':
                    clean_row.append("")
                else:
                    clean_row.append(str(cell))
            clean_values.append(clean_row)
        
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body={"values": clean_values}
        ).execute()
    except Exception as e:
        st.error(f"Google Sheets'e yazılamadı: {e}")
        raise

def save_tasks_to_sheet(df):
    """DataFrame'i Google Sheets'e güvenli şekilde kaydeder"""
    try:
        # DataFrame'i temizle
        df_clean = df.fillna("")
        
        # Tüm sheet'i temizle
        service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_NAME}!A1:Z1000"
        ).execute()
        
        # Yeni veriyi yaz
        values = [df_clean.columns.tolist()] + df_clean.values.tolist()
        write_sheet(f"{SHEET_NAME}!A1", values)
        
    except Exception as e:
        st.error(f"Veri kaydedilirken hata: {e}")
        raise

@st.cache_data(ttl=60)
def load_tasks():
    df = read_sheet(f"{SHEET_NAME}!A1:Z1000")
    required_columns = get_required_columns()
    
    if df.empty:
        df = pd.DataFrame(columns=required_columns)
    else:
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        df = df[required_columns]
        df = df.fillna("")
        
        # ID'leri kontrol et, boşsa yeni ID ata
        if 'ID' in df.columns:
            df['ID'] = df['ID'].replace("", pd.NA)
            # Boş ID'lere yeni ID ata (sadece boş olanlara)
            empty_ids = df['ID'].isna()
            if empty_ids.any():
                max_id = 0
                for id_val in df['ID'].dropna():
                    try:
                        max_id = max(max_id, int(str(id_val).split('_')[0]))
                    except:
                        pass
                
                new_ids = range(max_id + 1, max_id + 1 + empty_ids.sum())
                df.loc[empty_ids, 'ID'] = [str(i) for i in new_ids]
    
    return df

# --- Filtre Fonksiyonları ---
def get_date_filter_options():
    bugun = datetime.today().date()
    return {
        "Bu Hafta": lambda x: bugun <= datetime.strptime(x, "%Y-%m-%d").date() <= bugun + timedelta(days=(6 - bugun.weekday())) if x else False,
        "Termini Geçenler": lambda x: datetime.strptime(x, "%Y-%m-%d").date() < bugun if x else False,
        "Bu Ay": lambda x: bugun <= datetime.strptime(x, "%Y-%m-%d").date() <= bugun + timedelta(days=30) if x else False,
        "Gelecek": lambda x: datetime.strptime(x, "%Y-%m-%d").date() > bugun + timedelta(days=30) if x else False,
        "Tümü": lambda x: True
    }

def filter_tasks(df, search_query="", category="Tümü", date_filter="Bu Hafta", status_filter=None):
    if df.empty:
        return df
        
    filtered_df = df.copy()
    
    if search_query:
        mask = (
            filtered_df["Başlık"].str.contains(search_query, case=False, na=False) |
            filtered_df["Sorumlu"].str.contains(search_query, case=False, na=False) |
            filtered_df["Açıklama"].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if category != "Tümü":
        filtered_df = filtered_df[filtered_df["Kategori"] == category]
    
    if date_filter != "Tümü":
        date_filters = get_date_filter_options()
        if date_filter in date_filters:
            filtered_df = filtered_df[filtered_df["Termin"].apply(date_filters[date_filter])]
    
    if status_filter and "Durum" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Durum"].isin(status_filter)]
    
    return filtered_df

# --- Üst Menü ---
def render_header():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("### 🧩 **GTS**")
    
    with col2:
        search_query = st.text_input("🔍 Arama (Başlık, Sorumlu, Açıklama)", 
                                   value=st.session_state.search_query,
                                   key="search_input")
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            st.rerun()
    
    with col3:
        if st.button("➕ Yeni Görev", type="primary", use_container_width=True):
            st.session_state.show_create_task = True
            st.rerun()

# --- Sol Kenar Çubuğu ---
def render_sidebar():
    st.sidebar.markdown("### 📋 Menü")
    
    st.sidebar.markdown("### 📁 Kategoriler")
    selected_category = st.sidebar.selectbox("Kategori Seçin", ["Tümü"] + CATEGORIES, 
                                           index=0 if st.session_state.selected_category == "Tümü" else CATEGORIES.index(st.session_state.selected_category) + 1)
    
    if selected_category != st.session_state.selected_category:
        st.session_state.selected_category = selected_category
        st.rerun()
    
    st.sidebar.markdown("### 🔍 Filtreler")
    filter_options = ["Bu Hafta", "Termini Geçenler", "Bu Ay", "Gelecek", "Tümü"]
    selected_filter = st.sidebar.selectbox("Zaman Filtresi", filter_options,
                                         index=filter_options.index(st.session_state.selected_filter))
    
    if selected_filter != st.session_state.selected_filter:
        st.session_state.selected_filter = selected_filter
        st.rerun()
    
    status_options = st.sidebar.multiselect("Durum Filtresi", 
                                           ["Aktif", "Beklemede", "Tamamlandı", "İptal"], 
                                           default=["Aktif", "Beklemede"])
    
    return status_options

# --- Görev Oluşturma ---
def create_task_modal():
    if st.session_state.show_create_task:
        with st.form("create_task_form"):
            st.subheader("🆕 Yeni Görev Oluştur")
            
            col1, col2 = st.columns(2)
            with col1:
                baslik = st.text_input("Görev Başlığı *")
                sorumlu = st.text_input("Sorumlu Kişi *")
                kategori = st.selectbox("Kategori *", CATEGORIES)
            
            with col2:
                sorumlu_email = st.text_input("Sorumlu Email *")
                termin = st.date_input("Termin Tarihi *", value=datetime.today() + timedelta(days=7))
                durum = st.selectbox("Durum", ["Aktif", "Beklemede"], index=0)
            
            aciklama = st.text_area("Açıklama")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("✅ Oluştur", type="primary")
            with col_cancel:
                cancelled = st.form_submit_button("❌ İptal")
            
            if cancelled:
                st.session_state.show_create_task = False
                st.rerun()
            
            if submitted:
                if not baslik or not sorumlu or not sorumlu_email or not kategori:
                    st.error("⚠️ Zorunlu alanları doldurunuz!")
                    return
                
                try:
                    df = load_tasks()
                    
                    # Yeni ID oluştur - en büyük ID'yi bul ve 1 artır
                    if df.empty:
                        new_id = "1"
                    else:
                        max_id = 0
                        for id_val in df['ID']:
                            try:
                                # Sadece sayısal kısmı al (ID_1 formatında olabilir)
                                numeric_part = int(str(id_val).split('_')[0])
                                max_id = max(max_id, numeric_part)
                            except:
                                pass
                        new_id = str(max_id + 1)
                    
                    yeni_gorev = {
                        "ID": new_id,
                        "Başlık": baslik,
                        "Sorumlu": sorumlu,
                        "Sorumlu Email": sorumlu_email,
                        "Kategori": kategori,
                        "Termin": termin.strftime("%Y-%m-%d"),
                        "Durum": durum,
                        "Açıklama": aciklama,
                        "Oluşturulma Tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Tamamlanma Tarihi": ""
                    }
                    
                    new_df = pd.concat([df, pd.DataFrame([yeni_gorev])], ignore_index=True)
                    save_tasks_to_sheet(new_df)
                    
                    st.success("✅ Görev başarıyla oluşturuldu!")
                    st.session_state.show_create_task = False
                    st.cache_data.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Görev oluşturulurken hata: {e}")

# --- Görev Tablosu ---
def render_task_table(df):
    if df.empty:
        st.info("📭 Görev bulunamadı – Bu hafta görüntülenecek göreviniz yok")
        return
    
    st.subheader(f"📋 Görevler ({len(df)} adet)")
    
    for idx, row in df.iterrows():
        bugun = datetime.today().date()
        try:
            termin_tarihi = datetime.strptime(row["Termin"], "%Y-%m-%d").date()
            if termin_tarihi < bugun:
                status_icon = "🚨"
            elif termin_tarihi == bugun:
                status_icon = "⏰"
            else:
                status_icon = "📅"
        except:
            status_icon = "📋"
        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{status_icon} {row['Başlık']}**")
                st.caption(f"👤 {row['Sorumlu']} | 📂 {row['Kategori']} | ID: {row['ID']}")
                if row['Açıklama']:
                    st.caption(f"📝 {row['Açıklama'][:50]}...")
            
            with col2:
                st.write(f"📅 **{row['Termin']}**")
                st.caption(f"🔖 {row['Durum']}")
            
            with col3:
                if st.button("✏️", key=f"edit_{row['ID']}_{idx}", help="Düzenle"):
                    st.session_state[f"edit_mode_{row['ID']}"] = True
                    st.rerun()
            
            with col4:
                if row['Durum'] in ['Aktif', 'Beklemede']:
                    if st.button("✅", key=f"complete_{row['ID']}_{idx}", help="Tamamla"):
                        complete_task(row['ID'])
            
            with col5:
                if st.button("❌", key=f"cancel_{row['ID']}_{idx}", help="İptal"):
                    cancel_task(row['ID'])
            
            if st.session_state.get(f"edit_mode_{row['ID']}", False):
                edit_task_form(row)
            
            st.divider()

# --- Görev İşlemleri (Düzeltilmiş) ---
def complete_task(task_id):
    """Görevi tamamla - sadece durum günceller, yeni satır oluşturmaz"""
    try:
        # Önce cache'i temizle ve güncel veriyi al
        st.cache_data.clear()
        df = load_tasks()
        
        # ID ile eşleşen satırı bul
        task_mask = df["ID"] == str(task_id)
        matching_tasks = df[task_mask]
        
        if matching_tasks.empty:
            st.error(f"❌ ID {task_id} bulunamadı!")
            return
        
        if len(matching_tasks) > 1:
            st.error(f"❌ ID {task_id} için birden fazla kayıt bulundu! Veri tutarsızlığı var.")
            return
        
        # Görevi güncelle - mevcut satırda
        df.loc[task_mask, "Durum"] = "Tamamlandı"
        df.loc[task_mask, "Tamamlanma Tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Kaydet
        save_tasks_to_sheet(df)
        st.success("✅ Görev tamamlandı!")
        st.cache_data.clear()
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Görev tamamlanırken hata: {e}")

def cancel_task(task_id):
    """Görevi iptal et - sadece durum günceller, satırı silmez"""
    try:
        # Önce cache'i temizle ve güncel veriyi al
        st.cache_data.clear()
        df = load_tasks()
        
        # ID ile eşleşen satırı bul
        task_mask = df["ID"] == str(task_id)
        matching_tasks = df[task_mask]
        
        if matching_tasks.empty:
            st.error(f"❌ ID {task_id} bulunamadı!")
            return
        
        if len(matching_tasks) > 1:
            st.error(f"❌ ID {task_id} için birden fazla kayıt bulundu! Veri tutarsızlığı var.")
            return
        
        # Görevi güncelle - mevcut satırda
        df.loc[task_mask, "Durum"] = "İptal"
        df.loc[task_mask, "Tamamlanma Tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Kaydet
        save_tasks_to_sheet(df)
        st.success("✅ Görev iptal edildi!")
        st.cache_data.clear()
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Görev iptal edilirken hata: {e}")

def edit_task_form(task_row):
    """Görev düzenleme formu - sadece mevcut satırı günceller"""
    with st.form(f"edit_task_{task_row['ID']}"):
        st.subheader(f"✏️ Görev Düzenle - ID: {task_row['ID']}")
        
        col1, col2 = st.columns(2)
        with col1:
            baslik = st.text_input("Başlık", value=task_row["Başlık"])
            sorumlu = st.text_input("Sorumlu", value=task_row["Sorumlu"])
            kategori = st.selectbox("Kategori", CATEGORIES, 
                                  index=CATEGORIES.index(task_row["Kategori"]) if task_row["Kategori"] in CATEGORIES else 0)
        
        with col2:
            sorumlu_email = st.text_input("Email", value=task_row["Sorumlu Email"])
            termin = st.date_input("Termin", value=datetime.strptime(task_row["Termin"], "%Y-%m-%d"))
            durum = st.selectbox("Durum", ["Aktif", "Beklemede", "Tamamlandı", "İptal"],
                               index=["Aktif", "Beklemede", "Tamamlandı", "İptal"].index(task_row["Durum"]) 
                               if task_row["Durum"] in ["Aktif", "Beklemede", "Tamamlandı", "İptal"] else 0)
        
        aciklama = st.text_area("Açıklama", value=task_row["Açıklama"])
        
        col_update, col_cancel = st.columns(2)
        with col_update:
            updated = st.form_submit_button("💾 Güncelle", type="primary")
        with col_cancel:
            cancelled = st.form_submit_button("❌ İptal")
        
        if cancelled:
            st.session_state[f"edit_mode_{task_row['ID']}"] = False
            st.rerun()
            
        if updated:
            if not baslik or not sorumlu or not sorumlu_email:
                st.error("⚠️ Zorunlu alanları doldurunuz!")
                return
            
            try:
                # Cache'i temizle ve güncel veriyi al
                st.cache_data.clear()
                df = load_tasks()
                
                # ID ile eşleşen satırı bul
                task_mask = df["ID"] == str(task_row['ID'])
                matching_tasks = df[task_mask]
                
                if matching_tasks.empty:
                    st.error(f"❌ ID {task_row['ID']} bulunamadı!")
                    return
                
                if len(matching_tasks) > 1:
                    st.error(f"❌ ID {task_row['ID']} için birden fazla kayıt bulundu! Veri tutarsızlığı var.")
                    return
                
                # Mevcut satırı güncelle
                df.loc[task_mask, "Başlık"] = baslik
                df.loc[task_mask, "Sorumlu"] = sorumlu
                df.loc[task_mask, "Sorumlu Email"] = sorumlu_email
                df.loc[task_mask, "Kategori"] = kategori
                df.loc[task_mask, "Termin"] = termin.strftime("%Y-%m-%d")
                df.loc[task_mask, "Durum"] = durum
                df.loc[task_mask, "Açıklama"] = aciklama
                
                # Eğer durum tamamlandı olarak değiştirildi ve daha önce tamamlanma tarihi yoksa ekle
                if durum in ["Tamamlandı", "İptal"] and not task_row["Tamamlanma Tarihi"]:
                    df.loc[task_mask, "Tamamlanma Tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Kaydet
                save_tasks_to_sheet(df)
                st.success("✅ Görev güncellendi!")
                st.session_state[f"edit_mode_{task_row['ID']}"] = False
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Görev güncellenirken hata: {e}")

# --- Ana Uygulama ---
def main():
    render_header()
    create_task_modal()
    status_filter = render_sidebar()
    df = load_tasks()
    st.title("🧩 Görev Takip Sistemi")
    filtered_df = filter_tasks(
        df, 
        search_query=st.session_state.search_query,
        category=st.session_state.selected_category,
        date_filter=st.session_state.selected_filter,
        status_filter=status_filter
    )
    render_task_table(filtered_df)

if __name__ == "__main__":
    main()