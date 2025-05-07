import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def process_files():
    # Dosya seçme diyaloğunu aç ve kullanıcıdan dosya yollarını al
    atıl_stok_path = filedialog.askopenfilename(title="Atıl Stok Excel Dosyasını Seç")
    zsd0500_path = filedialog.askopenfilename(title="ZSD0500 Excel Dosyasını Seç")
    stok_path = filedialog.askopenfilename(title="Stok Excel Dosyasını Seç")
    output_folder = filedialog.askdirectory(title="Çıktı Dosyasının Kaydedileceği Klasörü Seç")

    # Eğer herhangi bir dosya seçilmediyse işlemi iptal et
    if not atıl_stok_path or not zsd0500_path or not stok_path or not output_folder:
        return

    # GUI ekranını güncelle, işlem başladı
    update_status_label("Dosya oluşturuluyor...")

    # Excel dosyalarını oku
    atıl_stok_df = pd.read_excel(atıl_stok_path, dtype={'Malzeme': str})
    zsd0500_df = pd.read_excel(zsd0500_path, dtype={'Malzeme': str})
    stok_df = pd.read_excel(stok_path, dtype={'Malzeme': str})

    # Tarih sütunlarını datetime formatına çevir
    zsd0500_df['Fiili mal hrkt.trh.'] = pd.to_datetime(zsd0500_df['Fiili mal hrkt.trh.'], errors='coerce')
    stok_df['MG tarihi'] = pd.to_datetime(stok_df['MG tarihi'], errors='coerce')

    # Çıktı DataFrame'ini hazırla
    output_df = atıl_stok_df.copy()
    output_df['Fiili mal hrkt.trh.'] = ''
    output_df['Sipariş veren'] = ''
    output_df['Siparişi Veren Adı'] = ''
    output_df['En Yakın MG Tarihi'] = ''
    output_df['En Uzak MG Tarihi'] = ''

    # atıl_stok dosyasındaki her satır için işlemleri gerçekleştir
    for index, row in atıl_stok_df.iterrows():
        malzeme_kodu = row['Malzeme']
        
        # zsd0500 dosyasını işle
        zsd0500_malzeme = zsd0500_df[zsd0500_df['Malzeme'] == malzeme_kodu]
        if not zsd0500_malzeme.empty:
            en_yakin_tarih_satir = zsd0500_malzeme.loc[zsd0500_malzeme['Fiili mal hrkt.trh.'].idxmax()]
            output_df.at[index, 'Fiili mal hrkt.trh.'] = en_yakin_tarih_satir['Fiili mal hrkt.trh.']
            output_df.at[index, 'Sipariş veren'] = en_yakin_tarih_satir['Sipariş veren']
            output_df.at[index, 'Siparişi Veren Adı'] = en_yakin_tarih_satir['Siparişi Veren Adı']
        else:
            output_df.at[index, 'Fiili mal hrkt.trh.'] = 'satış yok'
            output_df.at[index, 'Sipariş veren'] = 'satış yok'
            output_df.at[index, 'Siparişi Veren Adı'] = 'satış yok'

        # stok dosyasını işle
        stok_malzeme = stok_df[stok_df['Malzeme'] == malzeme_kodu]
        if not stok_malzeme.empty and stok_malzeme['MG tarihi'].notna().any():
            en_yakin_mg_satir = stok_malzeme.loc[stok_malzeme['MG tarihi'].idxmax()]
            en_uzak_mg_satir = stok_malzeme.loc[stok_malzeme['MG tarihi'].idxmin()]
            output_df.at[index, 'En Yakın MG Tarihi'] = en_yakin_mg_satir['MG tarihi']
            output_df.at[index, 'En Uzak MG Tarihi'] = en_uzak_mg_satir['MG tarihi']
        else:
            output_df.at[index, 'En Yakın MG Tarihi'] = 'stok yok'
            output_df.at[index, 'En Uzak MG Tarihi'] = 'stok yok'

    # Çıktıyı yeni bir Excel dosyasına kaydet
    output_path = os.path.join(output_folder, "atıl_stok_cıktı.xlsx")
    output_df.to_excel(output_path, index=False)

    # İşlem tamamlandı mesajını göster
    update_status_label(f"İşlem tamamlandı. Çıktı '{output_path}' dosyasına kaydedildi.")

def update_status_label(message):
    status_label.config(text=message)
    status_label.update()

def open_gui_window():
    # Ana pencere oluştur
    root = tk.Tk()
    root.title("Dosya İşlemleri")

    # Ana pencereyi merkezle
    window_width = 400
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

    # Etiket oluştur
    global status_label
    status_label = tk.Label(root, text="Dosyaları seçin ve işlemi başlatın.", font=("Helvetica", 12))
    status_label.pack(pady=20)

    # Buton oluştur
    process_button = tk.Button(root, text="Dosyaları İşle", command=process_files)
    process_button.pack(pady=10)

    # Pencereyi göster
    root.mainloop()

# Ana işlemi başlat
open_gui_window()
