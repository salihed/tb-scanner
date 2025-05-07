# Atıl Stok Hareketleri Projesi

Bu proje, belirli Excel dosyalarındaki verileri analiz ederek ve işleyerek yeni bir Excel dosyası oluşturmayı amaçlamaktadır. Proje Python programlama dili ve pandas kütüphanesi kullanılarak geliştirilmiştir.

## Dosya Yapısı

- `atıl_stok.xlsx`: Atıl stok verilerini içeren Excel dosyası.
- `zsd0500.xlsx`: Sevkiyat hareketlerine ait bilgileri içeren Excel dosyası.
- `stok.xlsx`: Stok bilgilerinin yer aldığı Excel dosyası.
- `atıl_stok_cıktı.xlsx`: İşlemler sonucunda oluşturulan ve sonuçları içeren yeni Excel dosyası.
- `Atıl Stok Hareketleri.py`: Python kodu.

## Kurulum

1. **Gereksinimler**:
   - Python 3.6 veya üstü
   - pandas kütüphanesi

2. **Kütüphanelerin Yüklenmesi**:
   Aşağıdaki komutu kullanarak gerekli kütüphaneleri yükleyin:
   ```bash
   pip install pandas

## Kavramsal Açıklama

Bu Python kodu, belirli dosya yollarından üç Excel dosyasını okur ve belirli koşullara göre bu dosyalardan veri çekerek yeni bir Excel dosyası oluşturur. İşlemlerin detaylı açıklamaları şu şekildedir:

1. **Excel Dosyalarının Okunması:**
    - `atıl_stok.xlsx`, `zsd0500.xlsx` ve `stok.xlsx` dosyaları okunur ve veri çerçevelerine (DataFrame) dönüştürülür. `Malzeme` sütunu metin (string) formatında okunur.

2. **Tarih Formatına Dönüştürme:**
    - `zsd0500.xlsx` ve `stok.xlsx` dosyalarındaki tarih sütunları (`Fiili mal hrkt.trh.` ve `MG tarihi`) datetime formatına dönüştürülür.

3. **Çıktı DataFrame'inin Hazırlanması:**
    - `atıl_stok.xlsx` dosyasındaki verilerle kopyalanarak yeni bir DataFrame oluşturulur. Bu DataFrame'e ek sütunlar eklenir: `Fiili mal hrkt.trh.`, `Sipariş veren`, `Siparişi Veren Adı`, `En Yakın MG Tarihi`, ve `En Uzak MG Tarihi`.

4. **Satır Satır İşleme:**
    - `atıl_stok.xlsx` dosyasındaki her bir satır için aşağıdaki işlemler yapılır:
        - `zsd0500.xlsx` dosyasında, malzeme koduna karşılık gelen satırlar bulunur. Eğer bu satırlar boş değilse, en yakın tarihli hareket satırı bulunur ve ilgili bilgiler (tarih, sipariş veren, siparişi veren adı) çıktı DataFrame'ine eklenir. Eğer satırlar boşsa, bu alanlara 'satış yok' yazılır.
        - `stok.xlsx` dosyasında, malzeme koduna karşılık gelen satırlar bulunur. Eğer bu satırlar boş değilse ve `MG tarihi` sütununda geçerli tarihler varsa, en yakın ve en uzak tarihli hareket satırları bulunur ve ilgili bilgiler çıktı DataFrame'ine eklenir. Eğer satırlar boşsa veya geçerli tarihler yoksa, bu alanlara 'stok yok' yazılır.

5. **Çıktının Excel Dosyasına Kaydedilmesi:**
    - Çıktı DataFrame'i yeni bir Excel dosyasına (`atıl_stok_cıktı.xlsx`) kaydedilir.

## Kullanım

1. `Atıl Stok Hareketleri.py` dosyasını düzenleyerek dosya yollarını kendi sisteminize uygun hale getirin.
2. Python betiğini çalıştırın:
3. İşlem tamamlandığında, çıktı `atıl_stok_cıktı.xlsx` dosyasına kaydedilecektir.

## Açıklamalar

Bu betik, üç farklı Excel dosyasından veri okuyarak belirli koşullara göre işleme yapar ve sonuçları yeni bir Excel dosyasına yazar. Bu işlemleri yapabilmesi için dosyaların exe dosyasının bulunduğu klasörde olması gerekmektedir. Bu işlemler şunları içerir:

- Atıl stok verilerini `atıl_stok.xlsx` dosyasından okur.
- Her malzeme kodu için `zsd0500.xlsx` dosyasındaki en yakın tarihli hareketi ve `stok.xlsx` dosyasındaki en yakın ve en uzak MG tarihlerini bulur.
- Bu bilgileri kullanarak yeni bir Excel dosyası oluşturur.

Herhangi bir sorunuz veya geri bildiriminiz için iletişime geçebilirsiniz.

## Lisans

Bu proje, açık kaynak MIT Lisansı altında lisanslanmıştır, SalihED tarafından yazılmıştır.
