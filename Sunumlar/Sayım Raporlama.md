## Yıl Sonu Sayım ve Sayım Karşılaştırma Raporlama Kurgusu

### 1. Amaç ve Kapsam

**Amaç:**
Yıl sonu fiziksel sayım sücrecinin tutarlılığını, doğruluğunu ve şeffaflığını artırmak; sayım sonuçlarının sistem kayıtlarıyla karşılaştırılmasına yönelik raporlama altyapısını tanımlamak.

**Kapsam:**

* Tüm Lojistik Merkezleri, STD Depoları, Yurtdışı Depolar
* Fiziksel sayım uzlaşma ve raporlama adımları
* SAP/EWM içi sayım kayıt süreçleri ve Z-tanımlı sayım karşılaştırma raporları


### 2. Mevcut Durum Analizi

Mevcut envanter sayım süreci, EWM (Extended Warehouse Management) sistemi üzerinde aşağıdaki adımlar doğrultusunda yürütülmektedir:

1. **Sayım Envanter Belgesi ve Depo Siparişi Oluşturma:**  
   Her sayım turu için sistemde **/SCWM/S_PI_ITEM** tablosu üzerinden bir “Sayım Envanter Belgesi” oluşturulur. Belge oluşturulduğunda, sayımı bekleyen tüm satırlar başlangıçta `ACTI` (aktif) statüsünde yer alır.  
   Oluşturulan sayım belgesi kapsamında, **her bir depo adresi (LGPLA)** için ayrı **depo siparişleri** oluşturulur. Bu siparişlerin içerisinde, fiziksel olarak sayımı yapılması gereken **taşıma birimleri (HU - Handling Units)** tanımlanır. Sayım işlemi, bu birimlerin adres bazlı kontrolü üzerinden yürütülür.

2. **Sayımın Gerçekleştirilmesi:**  
   Sayım işlemleri, **sayım moduna alınmış EWM el terminalleri** aracılığıyla sahada gerçekleştirilir. Sayımı tamamlanan satırlar otomatik olarak `COUN` (sayım yapıldı) statüsüne geçer. Sayımda sapma gözlemlenen kalemler, saha lideri tarafından tekrar kontrol edilerek gerekli düzeltmeler yapılır ve prosedüre uygun şekilde sisteme kayıt edilir.

3. **Statü Yönetimi ve Kayıt:**  
   Belge satırları `ACTI` statüsündeyken sayım yapılır. Sayım tamamlandığında satırlar `COUN` statüsüne geçer. Kontrol edilen ve onaylanan satırlar, `POST` işlemiyle sistem stoklarına işlenir.

4. **Sistem Kayıtları ve ERP Entegrasyonu:**  
   Tüm satırların `POST` işlemiyle tamamlanmasının ardından, EWM sistemi üzerinden SAP ERP sistemine **otomatik stok hareket kayıtları** iletilir. Bu kayıtlar, **711 (eksik stok)** ve **712 (fazla stok)** hareket türleriyle oluşturulur ve SAP MM sisteminde malzeme hareketleri olarak izlenebilir hale gelir.

5. **Raporlama ve Fark Analizi:**  
   Oluşan farklar hem EWM tarafındaki sayım sonuçları hem de ERP tarafındaki hareket belgeleri (711-712) dikkate alınarak analiz edilir.  
   - Sayım sonuçları içeren liste ve MB51 hareket raporu (özellikle 711 ve 712 hareket türleri) Excel ortamına aktarılır.  
   - Bu iki kaynak manuel olarak birleştirilir, sapmalar değerlendirilir.

6. **Yönetim Özeti Hazırlığı:**  
   Sayım ve sistem hareketleri karşılaştırılarak farklara dair analiz tamamlanır. Bu analiz sonucunda, yönetime sunulmak üzere **Yönetim Özeti Raporu** oluşturulur.


### 3. Hedeflenen Durum

Mevcut sayım süreci dijital ortamda (EWM el terminalleri ile) başarıyla gerçekleştirilmektedir. Ancak raporlama ve analiz aşamasındaki manuel işlemler süreçte gecikmelere, hata risklerine ve verimsizliğe neden olmaktadır.  

Hedeflenen durumda:

- Sayım verileri sistemden otomatik olarak çekilerek, raporlama ve analiz süreçleri tamamen dijital hale getirilir.  
- EWM ve SAP ERP arasındaki entegrasyon sonrası farklar anlık ve doğru olarak izlenir.  
- Manuel veri işleme ve Excel bazlı analiz ihtiyacı ortadan kalkar.  
- Yönetim özeti ve fark raporları, kullanıcı müdahalesine gerek kalmadan otomatik üretilir ve sunulur.

---

### İyileştirme Önerileri

1. **Otomatik Raporlama ve Fark Analizi:**  
   Sayım sonuçları ile ERP hareket verileri (711-712) sistemsel olarak entegre edilerek, fark raporları otomatik ve standart formatta oluşturulmalıdır.

2. **Merkezi Yönetim Raporlama Arayüzü:**  
   Fark analizleri, EWM ve ERP verilerinin birleştiği, kullanıcıların kolayca filtreleme ve detay incelemesi yapabileceği bir raporlama ekranı tasarlanmalıdır.

3. **Veri İşleme Hatalarının Azaltılması:**  
   Manuel Excel işlemleri kaldırılarak, veri bütünlüğü ve doğruluğu artırılmalı, hatalar minimize edilmelidir.

4. **Süreç İzlenebilirliği ve Denetim:**  
   Tüm sayım ve entegrasyon süreçleri sistemde otomatik olarak loglanmalı, denetim ve kontrol mekanizmaları güçlendirilmelidir.


### 4. Kavramsal Tasarım

#### 4.1 SAP’de Raporlama Altyapısının Hazırlanması

* **Otomatik Veri Toplama:**

  * EWM sayım sonuçları ile SAP ERP sistemindeki 711 ve 712 hareket türlerine ait defter kayıtları, manuel müdahaleye gerek kalmadan otomatik olarak merkezi bir Z-tabloda birleştirilmelidir.

#### 4.1.1 Yönetim Özet Raporu:

#### Amaç
Yönetim Özet Raporu, envanter sayım sonuçlarının sistemde kayıtlı defter verileri ile karşılaştırılarak stok doğruluğunu üst düzeyde analiz etmeyi amaçlar. Bu rapor, yönetimin hızlıca genel durumu görebilmesi ve stok farklarının türlerine göre sınıflandırılması için kritik veriler sunar.

#### Raporlamada Kullanılacak Alanlar
  * Rapor; Kategori, Miktar (Adet), Ağırlık (KG), Ağırlık (%) ve Finansal (TL) başlıklarını içermelidir.
  * Bu başlıklara ait detaylı açıklamalar ve örnek tablo, sonraki bölümde yer almaktadır.

  ### Örnek Rapor Tablosu

| Kategori           | Miktar (Adet) | Ağırlık (KG) | Ağırlık % | Finansal      |
|--------------------|---------------|--------------|-----------|---------------|
| Defter             | 60.045.652    | 763.213      | -         |               |
| Sayım              | 60.191.906    | 763.070      | 100,0%    |               |
| Doğrulanan         | 59.802.372    | 762.113      | 99,9%     |               |
| Birebir Doğrulanan | 59.802.372    | 762.113      | 100,0%    |               |
| Lot Değişen        | 0             | 0            | 0,0%      |               |
| Mutlak Sayım Farkı | 389.534       | 957          | 0,1%      | ₺693.974      |
| Yönlü Sayım Farkı  | 146.254       | -143         | 0,0%      | ₺135.715      |
| Defter > Sayım     | -121.640      | -550         | -57,5%    | -₺279.130     |
| Sayım > Defter     | 267.894       | 407          | 42,5%     | ₺414.845      |

**Kategori Sütunu Açıklamaları:**

* **Defter:** Sistem üzerinde kayıtlı miktarı ifade eder. SAP EWM içinde /SCWM/S_PI_ITEM tablosundaki QUAN_BOOK alanındaki verileri temsil eder.
* **Sayım:** Fiziksel olarak sahada yapılan sayım sonucu oluşan miktarı gösterir. SAP EWM içinde /SCWM/S_PI_ITEM tablosundaki QUAN_COUNT alanındaki verilerdir.
* **Doğrulanan:** Birebir Doğrulanan ve Lot Değişen toplamını ifade eder. Sayım sonucu, defter miktarıyla aynı olan ve fark içermeyen satırları kapsar. Bu kategori, kayıt bazında herhangi bir miktar farkı olmasa da lot farkı içeren kayıtları da içerir.Sayım ile defter kayıtlarının birebir örtüştüğü satırlar. Herhangi bir fark bulunmamaktadır
* **Birebir Doğrulanan:** Doğrulanan satırların alt kümesidir. Malzeme (MATNR), parti (CHARG) ve sayım miktarı (QUAN_COUNT) bilgisinin defter miktarındaki (QUAN_BOOK) bilgi ile tamamen eşleştiği durumu ifade eder.Hem miktar hem de lot bilgisinin eşleştiği doğrulama türüdür.
* **Lot Değişen:** Doğrulanan satırların alt kümesidir. Fiziksel sayım sırasında, sistemde kayıtlı olan bir malzemenin (MATNR) sayım miktarı (QUAN_COUNT) ile defter miktarı (QUAN_BOOK) arasında net bir fark olmasa da (yani malzeme bazında toplam fark (QUAN_DIFF toplamı) sıfır olsa da), sayılan parti bilgisinin sistemdeki parti bilgisinden (CHARG) farklı olduğu durumları ifade eder.
Bu durum, /SCWM/S_PI_ITEM tablosunda aynı malzeme (MATNR) için, defter miktarı fazla olan bir parti (CHARG) kaydının (QUAN_DIFF negatif) ve sayım miktarı fazla olan farklı bir parti (CHARG) kaydının (QUAN_DIFF pozitif) bulunması ve bu iki veya daha fazla kaydın QUAN_DIFF değerlerinin malzeme bazında birbirini dengelemesi şeklinde ortaya çıkmasıdır. Kalite izlenebilirliği açısından önemlidir.
* **Mutlak Sayım Farkı:** "Sayım > Defter" (pozitif farklar) ile "Defter > Sayım" (negatif farklar) kategorilerinin cebirsel mutlak toplamıdır.
* **Yönlü Sayım Farkı:** "Sayım > Defter" (pozitif farklar) ile "Defter > Sayım" (negatif farklar) kategorilerinin cebirsel toplamıdır.
* **Defter > Sayım:** Yönlü sayım farkının alt kümesidir. Bu kategori, fiziksel sayım sonuçlarına göre, sistemde kayıtlı olan defter miktarının (QUAN_BOOK) sahada sayılan miktardan (QUAN_COUNT) fazla olduğu durumları ifade eder. Başka bir deyişle, /SCWM/S_PI_ITEM tablosundaki bir sayım kalemine ait QUAN_BOOK değerinin QUAN_COUNT değerinden büyük olduğu durumlar bu kategoriye girer. Raporda yer alması talep edilen Defter > Sayım satırında aşağıdaki şartların dikkate alınması talep edilmektedir:
1- Fiziksel sayım farkları EWM'den SAP'ye POST edildiğinde, SAP tarafında malzeme belgeleri oluşur. Defter > Sayım durumu (sistem > sayım, yani eksiklik), SAP'de 712 hareket tipi ile kaydedilen malzeme belgelerine karşılık gelir. Konsolide Z-tablo bu ilişkiyi içermeli; böylece "Defter > Sayım" olarak sınıflandırılan kalemlerin hangi 712 hareketine neden olduğunu ve bu hareketin finansal etkisi (TL) görülebilmelidir.
2-Bir sayım kaleminin (malzeme/parti kombinasyonu bazında) "Defter > Sayım" kategorisine girmesi için teknik koşul QUAN_BOOK > QUAN_COUNT durumudur. Bu, sayım sonucunda ilgili kalemde sistemde bir eksiklik olduğunu gösterir (fiziksel stok deftere göre eksik).
4)Çok önemli bir not olarak, "Lot Değişen" kategorisine giren kalemler (yani malzeme bazında toplam defter ve sayım miktarı eşit olmasına rağmen, aynı malzeme içinde farklı lotlar arasında pozitif ve negatif farkların birbirini götürdüğü durumlar, bireysel olarak QUAN_BOOK > QUAN_COUNT koşulunu sağlasalar bile bu "Defter > Sayım" toplamına dahil edilmemelidir. "Lot Değişen" durumu ayrı bir mantıkla tespit edilip ayrı kategoride raporlanır.
* **Sayım > Defter:** Yönlü sayım farkının alt kümesidir. Defter > Sayım da açıklanan kuralları içerecek olup fiziksel sayım sonuçlarına göre, sahada sayılan miktarın (QUAN_COUNT) sistemde kayıtlı olan defter miktarından (QUAN_BOOK) fazla olduğu durumları ifade eder.

**Diğer Sütun Açıklamaları:**

* **Miktar (Adet):** Bu sütun, ilgili kategoriye ait stok miktarını adet cinsinden toplamını gösterir. Örneğin, "Defter" kategorisi için sistemde kayıtlı olan adet miktarını, "Sayım" kategorisi için fiziksel olarak sayılan adet miktarını veya farklılıkların (Mutlak Sayım Farkı, Yönlü Sayım Farkı, Defter > Sayım, Sayım > Defter) adet cinsinden büyüklüğünü ifade eder. 
* **Ağırlık (KG):** Bu sütun, ilgili kategoriye ait stok miktarının kilogram (KG) cinsinden toplam net ağırlığını gösterir. Tıpkı miktar gibi, defterdeki ağırlığı, sayılan ağırlığı veya aradaki ağırlık farklarını (KG cinsinden) ifade eder.
* **Ağırlık (%):** Bu sütun, her kategori için ağırlık verisinin ilgili ağırlığa göre yüzde karşılığını sunar. Hesaplamalar aşağıdaki formüllerle yapılmaktadır:
- Sayım = Sayım Ağırlığı (KG) / Defter Ağırlığı (KG)
- Doğrulanan = Doğrulanan Ağırlık (KG) / Defter Ağırlığı (KG)
- Birebir Doğrulanan = Birebir Doğrulanan Ağırlık (KG) / Doğrulanan Ağırlık (KG)
- Lot Değişen = Lot Değişen Ağırlık (KG) / Doğrulanan Ağırlık (KG)
- Mutlak Sayım Farkı = Mutlak Sayım Farkı Ağırlığı (KG) / Defter Ağırlığı (KG)
- Yönlü Sayım Farkı = Yönlü Sayım Farkı Ağırlığı (KG) / Defter Ağırlığı (KG)
- Defter > Sayım = Defter > Sayım Ağırlığı (KG) / Mutlak Sayım Farkı Ağırlığı (KG)
- Sayım > Defter = Sayım > Defter Ağırlığı (KG) / Mutlak Sayım Farkı Ağırlığı (KG)
* **Finansal (TL):** Bu sütun, Mutlak Sayım Farkı ve Yönlü Sayım Farkı satırlarında yer alan malzemelerin TL cinsinden finansal değerlerini içerir. Değerler FI modulünden alınmalıdır.


#### 4.1.2 Detay Analiz Raporu:

## 1. Amaç

Sayım sonuçları ile sistemde kayıtlı defter miktarlarının karşılaştırılması yoluyla, envanter doğruluğunun artırılması ve fark analizlerinin detaylandırılması hedeflenmektedir. Bu kapsamda, **Yönetim Özeti** ekranında yer alacak raporda, **Defter > Sayım** ve **Sayım > Defter** yönlü kontroller sağlanacaktır.

#### Raporlamada Kullanılacak Alanlar

Sayım verilerinin temel kaynağı **/SCWM/S_PI_ITEM** tablosudur. İlgili tabloda yer alan ve aşağıda detaylandırılan alanlar üzerinden analiz yapılacaktır. Ürün bazlı net ağırlık bilgisi ise **/SAPAPO/MATIO → NTGEW_TC** alanı üzerinden hesaplanacaktır.

### Belge ve Depo Bilgileri

| Alan Adı         | Açıklama                           |
|------------------|------------------------------------|
| OWNER            | Sahip                              |
| DOC_YEAR         | Belge Yılı                         |
| DOC_NUMBER       | Fiziksel Envanter Belgesi          |
| LGPLA            | Depo Adresi                        |
| HUIDENT_PARENT   | Taşıma Birimi                      |

### Ürün Bilgileri

| Alan Adı | Açıklama           |
|----------|--------------------|
| MATNR   | Ürün                |
| CHARG   | Parti               |
| MAKTX   | Ürün Kısa Tanımı    |

### Miktar Bilgileri

| Alan Adı        | Açıklama                                  |
|------------------|------------------------------------------|
| QUAN_BOOK        | Defter Miktarı                           |
| QUAN_COUNT       | Sayım Miktarı                            |
| QUAN_DIFF        | Fark Miktarı                             |
| QUAN_DIFF_ABS    | Mutlak Fark Miktarı                      |

### Sayım Zamanı ve Kullanıcı Bilgileri

| Alan Adı     | Açıklama                          |
|--------------|-----------------------------------|
| COUNT_DATE   | Sayım Tarihi                      |
| COUNT_TIME   | Sayım Saati                       |
| COUNT_USER   | Sayımı Yapan Kullanıcı (Sayaç)    |

### Net Ağırlık Üzerinden Hesaplanan Miktarlar

> Ürün ağırlığı **/SAPAPO/MATIO → NTGEW_TC** üzerinden alınarak hesaplamalar yapılacaktır.

| Hesaplama Alanı                  | Açıklama                          |
|----------------------------------|-----------------------------------|
| QUAN_BOOK * NTGEW_TC            | Defter Miktarı Net Ağırlık        |
| QUAN_COUNT * NTGEW_TC           | Sayım Miktarı Net Ağırlık         |
| QUAN_DIFF * NTGEW_TC            | Fark Miktarı Net Ağırlık          |
| QUAN_DIFF_ABS * NTGEW_TC        | Mutlak Fark Miktarı Net Ağırlık   |

## 4. Kullanım Senaryosu

Hazırlanacak rapor, hem sistemsel hem de fiziksel olarak envanter verilerinin tutarlılığını izlemek, sapmaların tespitini kolaylaştırmak ve gerektiğinde düzeltici faaliyetleri başlatmak amacıyla kullanılacaktır. Fark analizi, hem miktar hem de ağırlık bazlı olarak incelenecektir.




#### 4.4 Uzlaşma (Reconciliation)

* Sayım "COUNT" statüsüne geçtikten sonra, defter ile sayım arasındaki farklar sistem tarafından tespit edilmeli ve raporlanmalıdır.
* Bu farklar: Doğrulanan, Defter > Sayım, Sayım > Defter olarak sınıflandırılmalıdır.
* Tüm farklar detaylı tablolar ve grafiklerle raporlanmalıdır.


### 5. Roller ve Sorumluluklar

| Rol             | Sorumluluk                                    |
| --------------- | --------------------------------------------- |
| Depo Yöneticisi | Süreç planlama, ekip koordinasyonu, eğitim    |
| Saha Lideri     | Sayım hatalarının yeniden kontrolü            |
| Sayım Elemanı   | Fiziksel sayım yapan personel                 |
| Ofis Personeli  | Sayım ekran süreçlerini yürüten personel      |
| EWM Danışmanı   | Sayım belgesi oluşturma ve kayıt atma desteği |

---

### 6. Ekler ve Referanslar

* Örnek Sayım Talimat Dokümanları
* Mutabakat Formu Şablonları
* Literatür: Sensiba “Year-End Inventory Counts Best Practices”; NetSuite “Physical Inventory Tips”


Bunu başka bir talep değerlendirilecek dikkate alma: Sistemsel İş Kuralları ve Kontroller

* Mevcut sistemde sayım belgeleri depo siparişi ve raf bazlıdır. Tüm TB’lerin eksiksiz okutulması gerekir. Bu da başa dönme, yavaşlama, kopma sorunlarına yol açar.
* Bu nedenle TB bazlı sayım kaydı oluşturulması ve “ACTI → COUNT → POST” sürecinin her TB için ayrı ayrı işletilmesi talep edilmektedir.
* Not: Bu modele geçişle birlikte rafta okutulmayan TB kalması durumunda sistem uyarı veremeyecektir. Bu nedenle ayrı bir uyarı kontrol mekanizması geliştirilmesi istenmektedir.