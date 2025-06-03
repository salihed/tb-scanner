import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import json
import os
import io

# Streamlit Sayfa Yapılandırması
st.set_page_config(
    page_title="Görev Takip Sistemi",
    page_icon="📋",
    layout="wide"
)

# Veri dosyası yolu
DATA_FILE = "gorevler_v2.json"

# Veri yükleme ve kaydetme fonksiyonları
def load_tasks():
    """Görevleri dosyadan yükle"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task in data:
                    if task.get('termin') and isinstance(task['termin'], str):
                        task['termin'] = datetime.fromisoformat(task['termin'])
                    if task.get('olusturma') and isinstance(task['olusturma'], str):
                        task['olusturma'] = datetime.fromisoformat(task['olusturma'])
                    if task.get('tamamlanma') and isinstance(task['tamamlanma'], str):
                        task['tamamlanma'] = datetime.fromisoformat(task['tamamlanma'])
                return data
        except Exception as e:
            st.error(f"Veri yükleme hatası: {e}")
    return []

def save_tasks(tasks):
    """Görevleri dosyaya kaydet"""
    try:
        data_to_save = []
        for task in tasks:
            task_copy = task.copy()
            if task_copy.get('termin') and isinstance(task_copy['termin'], datetime):
                task_copy['termin'] = task_copy['termin'].isoformat()
            if task_copy.get('olusturma') and isinstance(task_copy['olusturma'], datetime):
                task_copy['olusturma'] = task_copy['olusturma'].isoformat()
            if task_copy.get('tamamlanma') and isinstance(task_copy['tamamlanma'], datetime):
                task_copy['tamamlanma'] = task_copy['tamamlanma'].isoformat()
            data_to_save.append(task_copy)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Veri kaydetme hatası: {e}")
        return False

# Session state'de görevleri sakla
if 'task_db' not in st.session_state:
    st.session_state.task_db = load_tasks()

if 'selected_tasks_to_delete' not in st.session_state:
    st.session_state.selected_tasks_to_delete = set()

if 'selected_tasks_in_trash' not in st.session_state:
    st.session_state.selected_tasks_in_trash = set()

if 'selected_completed_tasks_to_trash' not in st.session_state:
    st.session_state.selected_completed_tasks_to_trash = set()


# Yardımcı fonksiyonlar
def get_next_task_id():
    """Benzersiz yeni görev ID'si oluştur"""
    if not st.session_state.task_db:
        return 1
    return max(task['id'] for task in st.session_state.task_db) + 1

def parse_date(text):
    """Tarih metinlerini datetime objesine çevir"""
    if not text:
        return None
    formats = ["%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%y", "%d/%m/%y"]
    for fmt in formats:
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
    return None

def extract_task_info(text):
    """Doğal dil metininden görev bilgilerini çıkar"""
    if not text.strip():
        return None
    
    parsed = {
        "gorev": "-", "kategori": "-", "termin": None,
        "periyot": "-", "sorumlu": "-", "not": text.strip()
    }
    
    lines = text.strip().split('\n')
    first_line_processed_for_note = False

    if lines:
        first_line = lines[0].strip()
        if ',' in first_line:
            parts = [p.strip() for p in first_line.split(',')]
            parsed["gorev"] = parts[0]
            
            if len(parts) > 1:
                date_candidate = parse_date(parts[1])
                if date_candidate:
                    parsed["termin"] = date_candidate
                    if len(parts) > 2: parsed["kategori"] = parts[2]
                    if len(parts) > 3: parsed["sorumlu"] = parts[3]
                    if len(parts) > 4: 
                        parsed["not"] = ", ".join(parts[4:])
                        first_line_processed_for_note = True
                else:
                    parsed["kategori"] = parts[1]
                    if len(parts) > 2: parsed["sorumlu"] = parts[2]
                    if len(parts) > 3: 
                        parsed["not"] = ", ".join(parts[3:])
                        first_line_processed_for_note = True
        else:
             if not re.search(r"\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}", first_line):
                parsed["gorev"] = first_line

    temp_note_lines = []
    for line_idx, line_content in enumerate(lines):
        line = line_content.strip()
        if line_idx == 0 and first_line_processed_for_note:
            continue

        if line.lower().startswith('gorev:'):
            candidate_gorev = line[len('gorev:'):].strip()
            if parsed["gorev"] == "-" or (line_idx > 0 and parsed["gorev"] != candidate_gorev) :
                 parsed["gorev"] = candidate_gorev or "-"
        elif line.lower().startswith('termin:') or (not parsed.get("termin") and parse_date(line) and not parsed.get("gorev") == line):
            date_str = line[len('termin:'):].strip() if line.lower().startswith('termin:') else line
            dt = parse_date(date_str)
            if dt: parsed["termin"] = dt
            elif line_idx > 0 or not first_line_processed_for_note : temp_note_lines.append(line_content)
        elif line.lower().startswith('kategori:'):
            parsed["kategori"] = line[len('kategori:'):].strip() or "-"
        elif line.lower().startswith('sorumlu:'):
            parsed["sorumlu"] = line[len('sorumlu:'):].strip() or "-"
        elif line.lower().startswith('periyot:'):
            periyot_match = re.search(r"periyot[:\-\s]+(\d+)(?:\s*(gün|ay))?", line, re.IGNORECASE)
            if periyot_match:
                days = int(periyot_match.group(1))
                if periyot_match.group(2) and 'ay' in periyot_match.group(2).lower():
                    days *= 30
                parsed["periyot"] = str(days) + " gün"
            elif line_idx > 0 or not first_line_processed_for_note : temp_note_lines.append(line_content)
        elif line.lower().startswith('not:'):
            parsed["not"] = line[len('not:'):].strip()
            temp_note_lines = [line[len('not:'):].strip()]
            first_line_processed_for_note = True
        elif line_idx > 0 or (line_idx == 0 and not first_line_processed_for_note and parsed["gorev"] != line_content.strip()):
            temp_note_lines.append(line_content)
    
    if not first_line_processed_for_note and temp_note_lines:
        final_note = "\n".join(temp_note_lines).strip()
        if len(lines) == 1 and parsed["gorev"] == final_note and parsed["gorev"] != "-":
            if not any(parsed[k] and parsed[k] != "-" for k in ["kategori", "termin", "periyot", "sorumlu"]):
                 parsed["not"] = "-"
            else:
                 parsed["not"] = final_note
        else:
            parsed["not"] = final_note
    elif not parsed["not"] and (parsed["gorev"] == text.strip()):
        parsed["not"] = "-"

    for key in ["gorev", "kategori", "sorumlu", "periyot", "not"]:
        if not parsed.get(key):
            parsed[key] = "-"
            
    if parsed["termin"] is None and parsed.get("termin", "-") != "-":
        parsed["termin"] = "-"
        
    return parsed


def add_task(parsed_data):
    """Yeni görev ekle"""
    if not parsed_data or parsed_data["gorev"] == "-":
        return False, "Görev adı gerekli!"
    
    new_task = {
        "id": get_next_task_id(),
        "gorev": parsed_data["gorev"],
        "kategori": parsed_data["kategori"],
        "termin": parsed_data["termin"] if parsed_data["termin"] != "-" else None,
        "periyot": parsed_data["periyot"] if parsed_data["periyot"] != "-" else None,
        "sorumlu": parsed_data["sorumlu"],
        "not": parsed_data["not"] if parsed_data["not"] != "-" else "",
        "durum": "bekliyor",
        "olusturma": datetime.now(),
        "tamamlanma": None
    }
    
    st.session_state.task_db.append(new_task)
    save_tasks(st.session_state.task_db)
    return True, "Görev başarıyla eklendi!"

def complete_task(task_id):
    """Görevi tamamla"""
    task_found = False
    task_name_completed = ""
    for task in st.session_state.task_db:
        if task['id'] == task_id and task['durum'] == 'bekliyor':
            task['durum'] = 'tamamlandi'
            task['tamamlanma'] = datetime.now()
            task_name_completed = task['gorev']
            task_found = True
            
            if task.get('periyot') and task.get('termin'):
                try:
                    periyot_days = int(task['periyot'].split()[0])
                    new_date = task['termin'] + timedelta(days=periyot_days)
                    
                    new_periodic_task = task.copy()
                    new_periodic_task['id'] = get_next_task_id()
                    new_periodic_task['termin'] = new_date
                    new_periodic_task['durum'] = 'bekliyor'
                    new_periodic_task['olusturma'] = datetime.now()
                    new_periodic_task['tamamlanma'] = None
                    
                    st.session_state.task_db.append(new_periodic_task)
                except ValueError:
                    st.warning(f"Periyot formatı ({task['periyot']}) anlaşılamadı, yinelenen görev oluşturulamadı.")
            break 
    
    if task_found:
        save_tasks(st.session_state.task_db)
        return f"✅ Görev tamamlandı: {task_name_completed}"
    return "❌ Tamamlanacak görev bulunamadı veya zaten tamamlanmış."


def update_task_note_by_id(task_id, new_note):
    """Görev notunu ID ile güncelle (değiştir)"""
    task_found = False
    for task in st.session_state.task_db:
        if task['id'] == task_id:
            task['not'] = new_note
            task_found = True
            break
    
    if task_found:
        save_tasks(st.session_state.task_db)
        return f"✅ Not güncellendi: {task['gorev']}"
    return "❌ Görev bulunamadı."

def move_task_to_trash(task_id):
    """Görevi çöp kutusuna taşı"""
    task_found = False
    for task in st.session_state.task_db:
        if task['id'] == task_id:
            task['durum'] = 'silindi'
            task_found = True
            break
    if task_found:
        save_tasks(st.session_state.task_db)
        return True
    return False

def restore_task_from_trash(task_id):
    """Görevi çöp kutusundan geri yükle"""
    task_found = False
    for task in st.session_state.task_db:
        if task['id'] == task_id and task['durum'] == 'silindi':
            task['durum'] = 'bekliyor'
            task['tamamlanma'] = None
            task_found = True
            break
    if task_found:
        save_tasks(st.session_state.task_db)
        return True
    return False

def permanently_delete_task(task_id):
    """Görevi kalıcı olarak sil"""
    original_len = len(st.session_state.task_db)
    st.session_state.task_db = [task for task in st.session_state.task_db if task['id'] != task_id]
    if len(st.session_state.task_db) < original_len:
        save_tasks(st.session_state.task_db)
        return True
    return False

# Filtreleme fonksiyonları (silinmiş görevleri dışarıda bırakacak şekilde güncellendi)
def get_active_tasks():
    """Aktif (silinmemiş) görevleri getir"""
    return [task for task in st.session_state.task_db if task['durum'] != 'silindi']

def get_tasks_for_period(days=7, reference_date=None):
    """Belirli bir dönem için bekleyen görevleri getir"""
    if reference_date is None:
        reference_date = datetime.now()
    
    end_date = reference_date + timedelta(days=days)
    
    return [
        task for task in get_active_tasks() 
        if task.get('termin') and 
           task['termin'] <= end_date and 
           task['durum'] == 'bekliyor'
    ]

def search_tasks(query):
    """Aktif görevlerde arama yap - Tüm metin bazlı sütunları içerir"""
    if not query:
        return []
    query = query.lower()
    return [
        task for task in get_active_tasks()
        if query in task['gorev'].lower() or 
           query in (task.get('not') or '').lower() or
           query in (task.get('kategori') or '').lower() or
           query in (task.get('sorumlu') or '').lower() or
           query in (task.get('periyot') or '').lower() or
           query in (task.get('durum') or '').lower() or
           query == str(task['id']).lower()
    ]

def get_tasks_by_status(status):
    """Duruma göre aktif görevleri getir ('bekliyor' veya 'tamamlandi')"""
    return [task for task in get_active_tasks() if task['durum'] == status]

def get_deleted_tasks():
    """Silinmiş görevleri (çöp kutusu) getir"""
    return [task for task in st.session_state.task_db if task['durum'] == 'silindi']


def get_tasks_by_category(category):
    """Kategoriye göre aktif görevleri getir"""
    return [
        task for task in get_active_tasks() 
        if task.get('kategori') and category.lower() in task['kategori'].lower()
    ]

def tasks_to_dataframe(tasks):
    """Görevleri pandas DataFrame'e çevir"""
    data = []
    for task in tasks:
        data.append({
            "ID": task['id'],
            "Görev": task['gorev'],
            "Kategori": task.get('kategori', '-'),
            "Termin": task['termin'].strftime('%d.%m.%Y') if task.get('termin') else '-',
            "Sorumlu": task.get('sorumlu', '-'),
            "Periyot": task.get('periyot') or '-',
            "Durum": task['durum'].capitalize(),
            "Oluşturma": task['olusturma'].strftime('%d.%m.%Y %H:%M') if task.get('olusturma') else '-',
            "Tamamlanma": task['tamamlanma'].strftime('%d.%m.%Y %H:%M') if task.get('tamamlanma') else '-',
            "Not": task.get('not', '')
        })
    return pd.DataFrame(data)

def download_excel(df, filename):
    """DataFrame'i Excel dosyası olarak indirme bağlantısı oluştur"""
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer

# Streamlit Arayüzü
st.markdown("<h2 style='text-align: left; color: black; font-size: 28px; margin-bottom: 0px;'>📋 Akıllı Görev Takip Sistemi</h2>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.markdown("<h3 style='font-size: 20px;'>🎯 Menü</h3>", unsafe_allow_html=True)
    menu_options = [
        "📝 Yeni Görev", "📅 Bu Hafta", "📋 Tüm Görevler", 
        "✅ Tamamlananlar", "📁 Kategoriler", "🔍 Arama",
        "✔️ Görev Tamamla", "📝 Not Güncelle", "📊 İstatistikler", "🗑️ Çöp Kutusu"
    ]
    menu = st.radio("İşlem Seçin:", menu_options)
    
    st.markdown("---")
    st.markdown("<h4 style='font-size: 18px;'>📊 Özet (Aktif Görevler)</h4>", unsafe_allow_html=True)
    bekleyen = len(get_tasks_by_status('bekliyor'))
    tamamlanan_aktif = len(get_tasks_by_status('tamamlandi'))
    st.metric("Bekleyen Görevler", bekleyen)
    st.metric("Tamamlanan Görevler (Aktif)", tamamlanan_aktif)
    st.metric("Çöp Kutusundaki Görevler", len(get_deleted_tasks()))


if menu == "📝 Yeni Görev":
    st.markdown("<h3 style='font-size: 20px;'>📝 Yeni Görev Ekle</h3>", unsafe_allow_html=True)
    
    with st.form("new_task_form"):
        st.markdown("""
        **Görev bilgilerini aşağıdaki formatlarda yazabilirsiniz:**
        - Tek satır: `Görev Adı, Tarih (örn: 5.06.2025), Kategori, Sorumlu, Notunuz`
        - Çok satır (anahtar kelimelerle): `Görev: Proje sunumu hazırla`
          `Termin: 15.12.2024`
          `Kategori: İş`
          `Sorumlu: Ahmet`
          `Periyot: 30 gün`
          `Not: Sunum detayları ve önemli noktalar...`
        `Eksik bilgiler '-' veya boş olarak kaydedilir. 'Not' alanı için virgüllü formatta en sona yazılanlar veya 'Not:' anahtar kelimesi kullanılır.`
        """, unsafe_allow_html=True)
        
        task_text = st.text_area(
            "Görev Açıklaması ve Detayları:",
            height=200,
            placeholder="EKX Bakım, 5.06.2025, bakım, GokselA, Yıllık kontrol yapılacak.\n\nveya\n\nGörev: Raporu tamamla\nTermin: 20.08.2025\nNot: İstatistikleri eklemeyi unutma."
        )
        
        submitted = st.form_submit_button("💾 Görevi Kaydet", type="primary")
        
        if submitted:
            if task_text.strip():
                parsed = extract_task_info(task_text)
                if parsed:
                    success, message = add_task(parsed)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.error("Görev bilgileri ayrıştırılamadı.")
            else:
                st.warning("Lütfen görev bilgilerini girin!")

elif menu == "📅 Bu Hafta":
    st.markdown("<h3 style='font-size: 20px;'>📅 Bu Hafta Yapılacaklar (Bekleyen)</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        days = st.selectbox("Dönem:", [7, 14, 30], index=0, format_func=lambda x: f"{x} gün")
    
    tasks = get_tasks_for_period(days)
    if tasks:
        tasks.sort(key=lambda x: (x.get('termin') or datetime.max, x.get('olusturma') or datetime.min))
        df = tasks_to_dataframe(tasks)
        st.dataframe(df[["ID", "Görev", "Kategori", "Termin", "Sorumlu", "Not"]], use_container_width=True) 
        
        excel_buffer = download_excel(df, "bu_hafta_gorevler.xlsx")
        st.download_button(
            label="📥 Excel'e İndir", data=excel_buffer,
            file_name="bu_hafta_gorevler.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info(f"📅 Önümüzdeki {days} gün içinde ve geçmişte bekleyen görev bulunmuyor.")

elif menu == "📋 Tüm Görevler":
    st.markdown("<h3 style='font-size: 20px;'>📋 Tüm Aktif Görevler</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        durum_filter = st.selectbox("Durum:", ["Tümü (Aktif)", "Bekliyor", "Tamamlandı"], key="tum_durum_filter")
    with col2:
        sort_by = st.selectbox("Sıralama:", ["Termin", "Oluşturma", "Görev Adı"], key="tum_sort_by")
    with col3:
        order = st.selectbox("Sıra:", ["Artan", "Azalan"], key="tum_order")
    
    tasks_to_show = []
    if durum_filter == "Bekliyor":
        tasks_to_show = get_tasks_by_status('bekliyor')
    elif durum_filter == "Tamamlandı":
        tasks_to_show = get_tasks_by_status('tamamlandi')
    else:
        tasks_to_show = get_active_tasks()
    
    if sort_by == "Termin":
        tasks_to_show.sort(key=lambda x: (x.get('termin') or (datetime.max if order == "Artan" else datetime.min)), reverse=(order == "Azalan"))
    elif sort_by == "Oluşturma":
        tasks_to_show.sort(key=lambda x: x['olusturma'], reverse=(order == "Azalan"))
    else:
        tasks_to_show.sort(key=lambda x: x['gorev'].lower(), reverse=(order == "Azalan"))
    
    df_for_export = tasks_to_dataframe(tasks_to_show)

    st.markdown("---")
    
    st.markdown("<h4 style='font-size: 18px;'>Görevleri Çöp Kutusuna Taşı</h4>", unsafe_allow_html=True)
    
    current_task_ids = {task['id'] for task in tasks_to_show}
    st.session_state.selected_tasks_to_delete = st.session_state.selected_tasks_to_delete.intersection(current_task_ids)
    
    if tasks_to_show:
        st.write(f"📊 Toplam **{len(tasks_to_show)}** aktif görev bulundu.")

        display_data = []
        for task in tasks_to_show:
            is_selected = task['id'] in st.session_state.selected_tasks_to_delete
            display_data.append({
                "Seç": is_selected,
                "ID": task['id'],
                "Görev": task['gorev'],
                "Kategori": task.get('kategori', '-'),
                "Termin": task['termin'].strftime('%d.%m.%Y') if task.get('termin') else '-',
                "Sorumlu": task.get('sorumlu', '-'),
                "Periyot": task.get('periyot') or '-',
                "Durum": task['durum'].capitalize(),
                "Oluşturma": task['olusturma'].strftime('%d.%m.%Y %H:%M') if task.get('olusturma') else '-',
                "Tamamlanma": task['tamamlanma'].strftime('%d.%m.%Y %H:%M') if task.get('tamamlanma') else '-',
                "Not": task.get('not', '')
            })
        
        display_df = pd.DataFrame(display_data)

        edited_df = st.data_editor(
            display_df,
            column_config={
                "Seç": st.column_config.CheckboxColumn(
                    "Seç",
                    help="Çöp kutusuna taşımak için görevleri seçin",
                    default=False,
                )
            },
            hide_index=True,
            use_container_width=True,
            key="active_tasks_editor"
        )

        newly_selected_ids = {row['ID'] for idx, row in edited_df.iterrows() if row['Seç']}
        st.session_state.selected_tasks_to_delete = newly_selected_ids

        if st.session_state.selected_tasks_to_delete:
            if st.button("🗑️ Seçilenleri Çöp Kutusuna Taşı", type="primary"):
                deleted_count = 0
                for task_id in list(st.session_state.selected_tasks_to_delete):
                    if move_task_to_trash(task_id):
                        deleted_count +=1
                st.success(f"{deleted_count} görev çöp kutusuna taşındı.")
                st.session_state.selected_tasks_to_delete.clear()
                st.rerun()
        else:
            st.info("Çöp kutusuna taşımak için görevleri tabloda seçin.")
    else:
        st.info("Filtrelerinize uygun aktif görev bulunamadı.")
    
    st.markdown("---")
    excel_buffer_all = download_excel(df_for_export, "tum_aktif_gorevler.xlsx")
    st.download_button(
        label="📥 Tüm Listeyi Excel'e İndir", data=excel_buffer_all,
        file_name="tum_aktif_gorevler.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


elif menu == "✅ Tamamlananlar":
    st.markdown("<h3 style='font-size: 20px;'>✅ Tamamlanan Aktif Görevler</h3>", unsafe_allow_html=True)
    
    completed_tasks = get_tasks_by_status('tamamlandi')
    completed_tasks.sort(key=lambda x: x.get('tamamlanma', datetime.min), reverse=True)
    
    if completed_tasks:
        st.success(f"🎉 Toplam **{len(completed_tasks)}** aktif görev tamamlandı!")
        
        st.markdown("---")
        st.markdown("<h4 style='font-size: 18px;'>Görevleri Çöp Kutusuna Taşı</h4>", unsafe_allow_html=True)
        
        current_completed_task_ids = {task['id'] for task in completed_tasks}
        st.session_state.selected_completed_tasks_to_trash = st.session_state.selected_completed_tasks_to_trash.intersection(current_completed_task_ids)

        display_data_completed = []
        for task in completed_tasks:
            is_selected = task['id'] in st.session_state.selected_completed_tasks_to_trash
            display_data_completed.append({
                "Seç": is_selected,
                "ID": task['id'],
                "Görev": task['gorev'],
                "Kategori": task.get('kategori', '-'),
                "Termin": task['termin'].strftime('%d.%m.%Y') if task.get('termin') else '-',
                "Sorumlu": task.get('sorumlu', '-'),
                "Periyot": task.get('periyot') or '-',
                "Durum": task['durum'].capitalize(),
                "Oluşturma": task['olusturma'].strftime('%d.%m.%Y %H:%M') if task.get('olusturma') else '-',
                "Tamamlanma": task['tamamlanma'].strftime('%d.%m.%Y %H:%M') if task.get('tamamlanma') else '-',
                "Not": task.get('not', '')
            })
        
        display_df_completed = pd.DataFrame(display_data_completed)

        edited_df_completed = st.data_editor(
            display_df_completed,
            column_config={
                "Seç": st.column_config.CheckboxColumn(
                    "Seç",
                    help="Çöp kutusuna taşımak için görevleri seçin",
                    default=False,
                )
            },
            hide_index=True,
            use_container_width=True,
            key="completed_tasks_editor"
        )

        newly_selected_completed_ids = {row['ID'] for idx, row in edited_df_completed.iterrows() if row['Seç']}
        st.session_state.selected_completed_tasks_to_trash = newly_selected_completed_ids

        if st.session_state.selected_completed_tasks_to_trash:
            if st.button("🗑️ Seçilen Tamamlananları Çöp Kutusuna Taşı", type="primary"):
                deleted_count = 0
                for task_id in list(st.session_state.selected_completed_tasks_to_trash):
                    if move_task_to_trash(task_id):
                        deleted_count +=1
                st.success(f"{deleted_count} tamamlanan görev çöp kutusuna taşındı.")
                st.session_state.selected_completed_tasks_to_trash.clear()
                st.rerun()
        else:
            st.info("Çöp kutusuna taşımak için görevleri tabloda seçin.")
        
        st.markdown("---")

        # Excel indirme butonu, data_editor'daki veriyi kullanarak
        excel_buffer = download_excel(edited_df_completed.drop(columns=["Seç"]), "tamamlanan_gorevler.xlsx")
        st.download_button(
            label="📥 Tamamlanan Görevleri Excel'e İndir", data=excel_buffer,
            file_name="tamamlanan_gorevler.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Henüz tamamlanmış aktif görev bulunmuyor.")

elif menu == "📁 Kategoriler":
    st.markdown("<h3 style='font-size: 20px;'>📁 Kategoriye Göre Aktif Görevler</h3>", unsafe_allow_html=True)
    
    active_tasks = get_active_tasks()
    categories = set()
    for task in active_tasks:
        if task.get('kategori') and task['kategori'] != '-':
            categories.add(task['kategori'])
    
    if categories:
        selected_category = st.selectbox("Kategori Seçin:", sorted(list(categories)))
        
        if selected_category:
            category_tasks = get_tasks_by_category(selected_category)
            category_tasks.sort(key=lambda x: (x.get('termin') or datetime.max, x.get('olusturma') or datetime.min))

            if category_tasks:
                st.write(f"📊 **{selected_category}** kategorisinde **{len(category_tasks)}** aktif görev bulundu.")
                df = tasks_to_dataframe(category_tasks)
                st.dataframe(df, use_container_width=True)
                
                excel_buffer = download_excel(df, f"{selected_category}_gorevler.xlsx")
                st.download_button(
                    label="📥 Excel'e İndir", data=excel_buffer,
                    file_name=f"{selected_category}_gorevler.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("Bu kategoride aktif görev bulunamadı.")
    else:
        st.info("Henüz kategorize edilmiş aktif görev bulunmuyor.")

elif menu == "🔍 Arama":
    st.markdown("<h3 style='font-size: 20px;'>🔍 Aktif Görevlerde Arama</h3>", unsafe_allow_html=True)
    
    search_query = st.text_input("🔍 Arama terimi girin:", placeholder="Görev adı, kategori, sorumlu, not veya ID...")
    
    if search_query:
        results = search_tasks(search_query)
        results.sort(key=lambda x: (x.get('termin') or datetime.max, x.get('olusturma') or datetime.min))
        
        if results:
            st.success(f"🎯 **{len(results)}** sonuç bulundu.")
            df = tasks_to_dataframe(results)
            st.dataframe(df, use_container_width=True)
            
            excel_buffer = download_excel(df, "arama_sonuclari.xlsx")
            st.download_button(
                label="📥 Excel'e İndir", data=excel_buffer,
                file_name="arama_sonuclari.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Arama kriterinize uygun aktif görev bulunamadı.")

elif menu == "✔️ Görev Tamamla":
    st.markdown("<h3 style='font-size: 20px;'>✔️ Görev Tamamla</h3>", unsafe_allow_html=True)
    
    pending_tasks = get_tasks_by_status('bekliyor')
    pending_tasks.sort(key=lambda x: (x.get('termin') or datetime.max, x.get('olusturma') or datetime.min))

    if pending_tasks:
        task_options = {f"{task['gorev']} (ID: {task['id']})": task['id'] for task in pending_tasks}
        selected_task_display_name = st.selectbox("Tamamlanacak görevi seçin:", list(task_options.keys()))
        
        if selected_task_display_name:
            selected_task_id = task_options[selected_task_display_name]
            if st.button("✅ Tamamlandı Olarak İşaretle", type="primary"):
                result = complete_task(selected_task_id)
                st.success(result)
                st.rerun()
    else:
        st.info("Tamamlanacak bekleyen görev bulunmuyor.")

elif menu == "📝 Not Güncelle":
    st.markdown("<h3 style='font-size: 20px;'>📝 Not Güncelleme</h3>", unsafe_allow_html=True)
    
    all_active_tasks = get_active_tasks()
    all_active_tasks.sort(key=lambda x: (x.get('termin') or datetime.max, x.get('olusturma') or datetime.min))

    if all_active_tasks:
        task_options = {f"{task['gorev']} (ID: {task['id']})": task['id'] for task in all_active_tasks}
        selected_task_display_name = st.selectbox("Notu güncellenecek görevi seçin:", list(task_options.keys()))
        
        if selected_task_display_name:
            selected_task_id = task_options[selected_task_display_name]
            task_to_edit = next((t for t in all_active_tasks if t['id'] == selected_task_id), None)

            if task_to_edit:
                current_note = task_to_edit.get('not', '')
                new_note_content = st.text_area("Notu Düzenle:", value=current_note, height=150)
                
                if st.button("💾 Notu Güncelle", type="primary"):
                    result = update_task_note_by_id(selected_task_id, new_note_content)
                    st.success(result)
                    st.rerun()
            else:
                st.error("Seçilen görev bulunamadı.")
    else:
        st.info("Notu güncellenecek aktif görev bulunmuyor.")

elif menu == "🗑️ Çöp Kutusu":
    st.markdown("<h3 style='font-size: 20px;'>🗑️ Çöp Kutusu</h3>", unsafe_allow_html=True)
    deleted_tasks = get_deleted_tasks()
    deleted_tasks.sort(key=lambda x: x.get('olusturma') or datetime.min, reverse=True)

    if not deleted_tasks:
        st.info("Çöp kutusu boş.")
    else:
        st.write(f"Çöp kutusunda **{len(deleted_tasks)}** görev bulunuyor.")
        
        current_trash_task_ids = {task['id'] for task in deleted_tasks}
        st.session_state.selected_tasks_in_trash = st.session_state.selected_tasks_in_trash.intersection(current_trash_task_ids)

        display_data_trash = []
        for task in deleted_tasks:
            is_selected = task['id'] in st.session_state.selected_tasks_in_trash
            display_data_trash.append({
                "Seç": is_selected,
                "ID": task['id'],
                "Görev": task['gorev'],
                "Kategori": task.get('kategori', '-'),
                "Termin": task['termin'].strftime('%d.%m.%Y') if task.get('termin') else '-',
                "Sorumlu": task.get('sorumlu', '-'),
                "Periyot": task.get('periyot') or '-',
                "Durum": task['durum'].capitalize(),
                "Oluşturma": task['olusturma'].strftime('%d.%m.%Y %H:%M') if task.get('olusturma') else '-',
                "Tamamlanma": task['tamamlanma'].strftime('%d.%m.%Y %H:%M') if task.get('tamamlanma') else '-',
                "Not": task.get('not', '')
            })
        
        display_df_trash = pd.DataFrame(display_data_trash)

        edited_df_trash = st.data_editor(
            display_df_trash,
            column_config={
                "Seç": st.column_config.CheckboxColumn(
                    "Seç",
                    help="İşlem yapmak için görevleri seçin",
                    default=False,
                )
            },
            hide_index=True,
            use_container_width=True,
            key="trash_tasks_editor"
        )
        
        newly_selected_trash_ids = {row['ID'] for idx, row in edited_df_trash.iterrows() if row['Seç']}
        st.session_state.selected_tasks_in_trash = newly_selected_trash_ids


        col_actions1, col_actions2, col_actions3 = st.columns(3)
        with col_actions1:
            if st.session_state.selected_tasks_in_trash:
                if st.button("🔥 Seçilenleri Kalıcı Sil", type="primary"):
                    count = 0
                    for task_id in list(st.session_state.selected_tasks_in_trash):
                        if permanently_delete_task(task_id):
                            count +=1
                    st.success(f"{count} görev kalıcı olarak silindi.")
                    st.session_state.selected_tasks_in_trash.clear()
                    st.rerun()
            else:
                st.info("İşlem için çöp kutusundaki görevleri seçin.")
        with col_actions2:
            if st.session_state.selected_tasks_in_trash:
                 if st.button("🔄 Seçilenleri Geri Yükle"):
                    count = 0
                    for task_id in list(st.session_state.selected_tasks_in_trash):
                        if restore_task_from_trash(task_id):
                            count +=1
                    st.success(f"{count} görev geri yüklendi.")
                    st.session_state.selected_tasks_in_trash.clear()
                    st.rerun()
        
        with col_actions3:
            if st.button("💥 Tüm Çöp Kutusunu Boşalt", type="secondary"):
                st.warning("Bu işlem geri alınamaz! Emin misiniz?")
                confirm_empty = st.checkbox("Evet, tüm çöp kutusunu kalıcı olarak silmeyi onayla", key="confirm_empty_trash_all")
                if confirm_empty:
                    if st.button("Onaylıyorum, Hepsini Sil!", key="final_confirm_empty_trash"):
                        count = 0
                        for task in list(deleted_tasks): 
                            if permanently_delete_task(task['id']):
                                count +=1
                        st.success(f"Çöp kutusundaki {count} görevin tümü kalıcı olarak silindi.")
                        st.rerun()


elif menu == "📊 İstatistikler":
    st.markdown("<h3 style='font-size: 20px;'>📊 Görev İstatistikleri</h3>", unsafe_allow_html=True)
    
    total_tasks_in_db = len(st.session_state.task_db)
    active_pending_tasks = len(get_tasks_by_status('bekliyor'))
    active_completed_tasks = len(get_tasks_by_status('tamamlandi'))
    deleted_task_count = len(get_deleted_tasks())
    total_active_tasks = active_pending_tasks + active_completed_tasks
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Toplam Kayıtlı Görev (DB)", total_tasks_in_db)
    with col2:
        st.metric("Aktif Bekleyen", active_pending_tasks)
    with col3:
        st.metric("Aktif Tamamlanan", active_completed_tasks)
    with col4:
        completion_rate = (active_completed_tasks / total_active_tasks * 100) if total_active_tasks > 0 else 0
        st.metric("Aktif Tamamlanma Oranı", f"{completion_rate:.1f}%")
    
    st.metric("Çöp Kutusundaki Görevler", deleted_task_count, delta_color="off")


    st.markdown("<h4 style='font-size: 18px;'>📁 Aktif Görevlerin Kategori Dağılımı</h4>", unsafe_allow_html=True)
    categories = {}
    for task in get_active_tasks():
        cat = task.get('kategori') or 'Kategorisiz'
        if cat == "-": cat = 'Kategorisiz'
        categories[cat] = categories.get(cat, 0) + 1
    
    if categories:
        cat_df = pd.DataFrame(list(categories.items()), columns=['Kategori', 'Görev Sayısı'])
        cat_df = cat_df.sort_values(by='Görev Sayısı', ascending=False)
        st.dataframe(cat_df, use_container_width=True)
        
        try:
            import altair as alt
            chart = alt.Chart(cat_df).mark_bar().encode(
                x=alt.X('Kategori', sort=None),
                y='Görev Sayısı',
                tooltip=['Kategori', 'Görev Sayısı']
            ).properties(
                title='Kategoriye Göre Aktif Görev Sayıları'
            )
            st.altair_chart(chart, use_container_width=True)
        except ImportError:
            st.info("Grafik gösterimi için 'altair' kütüphanesi kurulabilir: pip install altair")

    else:
        st.info("Aktif görevlerde kategori bilgisi bulunmuyor.")


st.markdown("---")
st.markdown("<p style='font-size: 14px;'>💡 **İpucu:** Görev bilgilerini hızlıca girmek için virgülle ayırabilirsiniz: `Görev Adı, Tarih, Kategori, Sorumlu, Notunuz`. Daha detaylı giriş için anahtar kelimeleri kullanın (örn: `Termin: GG.AA.YYYY`).</p>", unsafe_allow_html=True)