# LABELGUARD – OTOMATİK ETİKET KONTROL HATTI AKTİFLEŞTİRME PROJESİ
## KAVRAMSAL DOKÜMAN

### 1. PROJE GENEL BİLGİLERİ

**Proje Adı:** Etiketleme Hattı Aktifleştirme Projesi  
**Proje Tarihi:** 24.01.2025 (...)
**Proje Yeri:** İzmir Lojistik Merkezi  
**Proje Sorumluları:** Salih Doğrubak, Hüseyin Dinçer, Alican Tamer  
**Teknik Destek:** SICK Yetkilileri, Norm Bakım Müdürlüğü

### 2. PROJENİN AMACI VE KAPSAMI

**Amaç:** Etiketleme hattının aktif olarak çalışmasının sağlanması ve hat üzerindeki teknik sorunların giderilmesi.

**Kapsam:**
* Kamera sistemlerinin optimizasyonu
* Barkod okuma sorunlarının çözümü
* Yazılım iyileştirmeleri
* Hat üzerindeki fiziksel düzenlemeler
* İzlenebilirlik sisteminin kurulması

### 3. MEVCUT DURUM ANALİZİ

**Tespit Edilen Sorunlar:**
* Hat üzerindeki kameraların okutma sorunları
* Hat-kamera standının sabitlenme ihtiyacı
* Yazılımın çoklu referanslı etiketlerde eşleştirme sorunları
* Etiketlerin barkodlarında kamera flaşı kaynaklı okuma sorunları
* Hat duruşlarına neden olan sensör sorunları
* Kutuların hat üzerinde ortalanma sorunları

### 4. ÇÖZÜM YAKLAŞIMI

**Teknik Çözümler:**
* "Işık kutusu" (yüksek RGB özellikli) kurulumu
* LED aydınlatma sisteminin test edilmesi
* Yazılım güncellemeleri
* Hat üzerinde fiziksel düzenlemeler (kılavuz, stoper vb.)
* Barkod okuyucu entegrasyonu

**Yazılım İyileştirmeleri:**
* TB okutma ekran tasarımı
* Eşleşmeyen barkodların ekranda belirtilmesi
* Kullanıcı yetkilendirme sistemi
* İzlenebilirlik raporlama sistemi

### 5. PROJE AŞAMALARI

**Aşama 1: Durum Tespiti ve Analiz (20-24 Ocak 2025)**
* SICK firma yetkilileri ile hat üzerinde inceleme
* Kamera ve yazılım sorunlarının tespiti
* Çözüm önerilerinin belirlenmesi

**Aşama 2: Çözüm Tasarımı (24-29 Ocak 2025)**
* Işık kutusu teknik şartnamesinin hazırlanması
* Tedarikçi görüşmeleri ve fiyat teklifi alınması
* SAT açılması

**Aşama 3: Uygulama ve Test (Şubat-Nisan 2025)**
* LED aydınlatma testleri
* Yazılım güncellemeleri
* Hat üzerinde fiziksel düzenlemeler

### 6. PROJE DURUMU VE İLERLEME

**Tamamlanan İşler:**
* Hat ve kamera standının sabitlenmesi
* Kutunun ortalanması için kılavuz yapılması
* Işık kutusu için teklif alınması ve SAT açılması
* Demo LED'ler ile kameranın okuma performansının izlenmesi
* TB okutma ekran tasarımının yapılması
* Hattın sonuna stoper konulması
* Yazılımın sürekli hale getirilerek gözden geçirilmesi
* Eşleşmedi durumunda buton işlevlerinin kontrolü
* Data Reset butonunun yetkiye bağlanması
* Konveyör altındaki elektronik panodaki kabloların toplanması

**Devam Eden İşler:**
* Hatta yapılan işin izlenebilirliğini sağlayacak raporlama sistemi
* Barkod okuyucu entegrasyonu

**Bekleyen İşler:**
* TB alanında kullanıcı bilgisinin eklenmesi
* Hat duruş alanı oluşturulması
* 3. kamera eklenmesi değerlendirmesi

### 7. KAPASİTE HESABI VE FAZ 2 PLANLARI

**Hatta Yapılan İşler (8 Mayıs 2025 itibariyle):**

| Satır Etiketleri | Toplam Kutu Sayısı | Ortalama Sn/Kutu |
|------------------|--------------------|------------------|
| Facil klt        | 7642               | 12,27            |
| Facil Kutu       | 6341               | 10,60            |
| Nissan           | 1298               | 8,05             |
| Renault          | 14177              | 8,46             |
| Werke            | 481                | 10,17            |

| Aylar  | Toplam Kutu Sayısı | Ortalama Sn/Kutu |
|--------|--------------------|------------------|
| Şubat  | 3030               | 11,33            |
| Mart   | 10029              | 10,62            |
| Nisan  | 16234              | 9,81             |
| Mayıs  | 646                | 12,63            |
| Genel Toplam | 29939         | 10,34            |

**Kapasite Hesabı:**
* Ayda toplam ortalama 60.000 kutunun etiket değişimi yapılmaktadır.
* Mevcut durumda hatta yaklaşık 20.000 kutunun etiket değişimi yapılmaktadır.
* TOGG, Martur, Hyundai müşterilerindeki üretim etiketlerinin revizyonu ile 20.000 etiket daha hatta alınacaktır.

**Günlük Kapasite Hesabı (Tek Vardiya):**
* Günde 1 vardiya, 1 vardiya 7 saat, haftada 6 gün %80 verimlilik ile hesaplama:
  * Günlük çalışma süresi: 1 vardiya x 7 saat = 7 saat
  * Haftalık çalışma süresi: 7 saat x 6 gün = 42 saat
  * Aylık çalışma süresi: 42 saat x 4 hafta = 168 saat
  * 10 saniyede bir kutu çıkarsa: 3600 saniye/saat / 10 saniye/kutu = 360 kutu/saat
  * Aylık kapasite: 360 kutu/saat x 168 saat = 60,480 kutu/ay
  * Verimlilik: %80
  * Verimlilik ile: 60,480 kutu/ay x %80 = 48,384 kutu/ay

**Mevcut Durumdaki Çalışma Oranı:**
* Mevcut durumda hatta yaklaşık 20.000 kutunun etiket değişimi yapılmaktadır.
* Kapasite kullanım oranı: 20.000 / 48.384 = %41

### 8. FAZ 2 PLANLARI VE GELİŞTİRMELER

**FAZ 2 Hedefleri:**
* Hat kullanımının arttırılması
* Yapışkanlı etiket takma operasyonunun mekanikleştirilmesi
* Palet dizme robotu araştırması
