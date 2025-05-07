import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Depo boyutları
depo_x = 165
depo_y = 88

# Raf bilgileri
raf_yuksekligi = 0.8  # metre (kat arası mesafe)
raf_kat_sayisi = 14

# Palet bilgileri
palet_genisligi = 0.8  # metre
palet_uzunlugu = 1.2  # metre

# Depo çizimi
fig, ax = plt.subplots(figsize=(depo_x / 10, depo_y / 10))

# Depo sınırları
ax.set_xlim(0, depo_x)
ax.set_ylim(0, depo_y)

# Raf çizimi (örnek bir bölüm)
raf_baslangic_x = 10  # rafların başladığı x koordinatı
raf_baslangic_y = 4   # rafların başladığı y koordinatı
raf_bolum_x = 20  # örnek bölüm genişliği
raf_bolum_y = 20  # örnek bölüm yüksekliği

for kat in range(raf_kat_sayisi):
    for x in range(raf_baslangic_x, raf_baslangic_x + raf_bolum_x, int(palet_uzunlugu * 2)):
        for y in range(raf_baslangic_y, raf_baslangic_y + raf_bolum_y, int(palet_genisligi * 2)):
            raf = patches.Rectangle((x, y + kat * raf_yuksekligi), palet_uzunlugu, raf_yuksekligi, linewidth=1, edgecolor='g', facecolor='none')
            ax.add_patch(raf)

# Palet çizimi (örnek bir bölüm)
for x in range(raf_baslangic_x, raf_baslangic_x + raf_bolum_x, int(palet_uzunlugu * 2)):
    for y in range(raf_baslangic_y, raf_baslangic_y + raf_bolum_y, int(palet_genisligi * 2)):
        palet = patches.Rectangle((x, y), palet_uzunlugu, palet_genisligi, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(palet)

# Çizim ayarları
ax.set_aspect('equal', adjustable='box')
plt.gca().invert_yaxis()
plt.title("Depo Layout - Örnek Bölüm")
plt.show()
