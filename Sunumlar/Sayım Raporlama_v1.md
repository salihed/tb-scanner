# Yıl Sonu Sayım ve Sayım Karşılaştırma Raporlama Kurgusu

Bu doküman, Lojistik Merkezleri ve Mamul Depolarındaki yıl sonu fiziksel envanter sayımı sürecinin raporlama yapısını detaylandırmaktadır. 

## 1. Amaç ve Kapsam

### Amaç:
Yıl sonu fiziksel sayım sürecinin tutarlılığını, doğruluğunu ve şeffaflığını artırmak; sayım sonuçlarının sistem kayıtlarıyla karşılaştırılmasına yönelik raporlama altyapısını tanımlamak.

### Kapsam:
- Tüm Lojistik Merkezleri, STD Depoları, Yurtdışı Depolar  
- Fiziksel sayım uzlaşma ve raporlama adımları  
- SAP/EWM içi sayım kayıt süreçleri ve Z-tanımlı sayım karşılaştırma raporları  

---

## 2. Mevcut Durum Analizi

Mevcut envanter sayım süreci, EWM sistemi üzerinde aşağıdaki adımlar doğrultusunda yürütülmektedir:

1. **Sayım Envanter Belgesi ve Depo Siparişi Oluşturma:**  
   Her sayım turu için sistemde **/SCWM/S_PI_ITEM** tablosu üzerinden bir “Sayım Envanter Belgesi” oluşturulur. Belge oluşturulduğunda, sayımı bekleyen tüm satırlar başlangıçta `ACTI` (aktif) statüsünde yer alır.  
   Oluşturulan sayım belgesi kapsamında, **her bir depo adresi (LGPLA)** için ayrı **depo siparişleri** oluşturulur. Bu siparişlerin içerisinde, fiziksel olarak sayımı yapılması gereken **taşıma birimleri (HU - Handling Units)** tanımlanır. Sayım işlemi, bu birimlerin adres bazlı kontrolü üzerinden yürütülür.

2. **Sayımın Gerçekleştirilmesi:**  
   Sayım işlemleri, **sayım moduna alınmış EWM el terminalleri** aracılığıyla sahada gerçekleştirilir. Sayımı tamamlanan satırlar otomatik olarak `COUN` (sayım yapıldı) statüsüne geçer. Sayımda sapma gözlemlenen kalemler, saha/takım lideri tarafından tekrar kontrol edilerek gerekli düzeltmeler yapılır ve sayım talimatına uygun şekilde sisteme kayıt edilir.

3. **Statü Yönetimi:**  
   Belge satırları `ACTI` statüsündeyken sayım yapılır. Sayım tamamlandığında satırlar `COUN` statüsüne geçer. Kontrol edilen ve onaylanan satırlar SAP EWM de Fiziksel Envanter Belgesine kaydet işlemi yapıldığında `POST` statüsüne geçer.

4. **Sistem Kayıtları ve ERP Entegrasyonu:**  
   Tüm satırların `POST` statüsüne alınmasının ardından, Difference Analyzer (/SCWM/DIFF_ANALYZER) ekranından sayım farkı olan satırların kaydı yapılır. Ardından SAP ERP sistemine **otomatik stok hareket kayıtları** iletilir. Bu kayıtlar, **711 (eksik stok)** ve **712 (fazla stok)** hareket türleriyle oluşturulur ve SAP MM sisteminde malzeme hareketleri olarak izlenebilir hale gelir.

5. **Raporlama ve Fark Analizi:**  
   Oluşan farklar hem EWM tarafındaki sayım sonuçları hem de ERP tarafındaki hareket belgeleri (711-712) dikkate alınarak analiz edilir.  
   - Sayım sonuçları içeren liste ve MB51 hareket raporu (711 ve 712 hareket türleri) Excel ortamına aktarılır.  
   - Bu iki kaynak manuel olarak birleştirilir, sapmalar değerlendirilir.

6. **Yönetim Özeti Hazırlığı:**  
   Sayım ve sistem hareketleri karşılaştırılarak farklara dair analiz tamamlanır. Bu analiz sonucunda, yönetime sunulmak üzere **Yönetim Özeti Raporu** oluşturulur. Ayrıca **Detay Analiz Tablosu** hazırlanarak fark oluşan satırların nedenleri gözden geçirilir.

---

## 3. Hedeflenen Durum

Mevcut sayım süreci dijital ortamda (EWM el terminalleri ile) başarıyla gerçekleştirilmektedir. Ancak raporlama ve analiz aşamasındaki manuel işlemler süreçte gecikmelere, hata risklerine ve verimsizliğe neden olmaktadır.  

Hedeflenen durumda:

- Sayım verileri sistemden otomatik olarak çekilerek, raporlama ve analiz süreçleri tamamen dijital hale getirilir.  
- EWM ve SAP ERP arasındaki entegrasyon sonrası farklar anlık ve doğru olarak izlenir.  
- Manuel veri işleme ve Excel bazlı analiz ihtiyacı ortadan kalkar.  
- Yönetim özeti ve detay fark raporları, kullanıcı müdahalesine gerek kalmadan otomatik üretilir ve sunulur.

---

### 3.1 İyileştirme Önerileri

1. **Otomatik Raporlama ve Fark Analizi:**  
   Sayım sonuçları ile ERP hareket verileri (711-712) sistemsel olarak entegre edilerek, fark raporları otomatik ve standart formatta oluşturulmalıdır.

2. **Merkezi Yönetim Raporlama Arayüzü:**  
   Fark analizleri, EWM ve ERP verilerinin birleştiği, kullanıcıların kolayca filtreleme ve detay incelemesi yapabileceği bir raporlama ekranı tasarlanmalıdır.

3. **Veri İşleme Hatalarının Azaltılması:**  
   Manuel Excel işlemleri kaldırılarak, veri bütünlüğü ve doğruluğu artırılmalı, hatalar minimize edilmelidir.

4. **Süreç İzlenebilirliği ve Denetim:**  
   Tüm sayım ve entegrasyon süreçleri sistemde otomatik olarak loglanmalı, denetim ve kontrol mekanizmaları güçlendirilmelidir.

---

## 4. Kavramsal Tasarım

### 4.1 SAP’de Raporlama Altyapısının Hazırlanması

#### Otomatik Veri Toplama:

- EWM sayım sonuçları ile SAP ERP sistemindeki 711 ve 712 hareket türlerine ait defter kayıtları, manuel müdahaleye gerek kalmadan otomatik olarak merkezi bir Z-tabloda birleştirilmelidir. Birleştirilen Tablolarda Üretim Yeri ve Depo Yeri bazında raporlara ulaşılabilmelidir. Bunun için rapor araması yapılabilecek bir arama ekranı tasarlanır. Giriş ekranında Üretim Yeri, Depo Yeri, Kayıt Tarihi, Düzen bilgileri yer alır. Tüm alanlar zorunlu alan olarak belirlenmelidir. * ile de çalışabilmelidir. **Yönetim Özet Raporu** ve  **Detay Analiz Tablosu** na tek bir ekrandan arama yapılarak ancak 2 rapor için seçim imkanı (radio buton) sunularak erişim sağlanabilir. 2 rapor da çalıştığında Hesap Çizelgesinden excel dosyası olarak alınabilmelidir.

---

### 4.1.1 Yönetim Özet Raporu:

#### Amaç
Yönetim Özet Raporu, envanter sayım sonuçlarının sistemde kayıtlı defter verileri ile karşılaştırılarak stok doğruluğunu üst düzeyde analiz etmeyi amaçlar. Bu rapor, yönetimin hızlıca genel durumu görebilmesi ve stok farklarının türlerine göre sınıflandırılması için kritik veriler sunar.

#### Raporlamada Kullanılacak Alanlar
- Kategori, Miktar (Adet), Ağırlık (KG), Ağırlık (%) ve Finansal (TL)

#### Örnek Rapor Tablosu

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

#### Kategori Sütunu Açıklamaları:
- **Defter:** Sayım yapılmadan önce sistemde kayıtlı olan ürün bilgilerini içerir. 
(/SCWM/S_PI_ITEM >> QUAN_BOOK)  

- **Sayım:** Fiziksel sayım sırasında gerçekte bulunan ürün bilgilerini içerir. 
(/SCWM/S_PI_ITEM >> QUAN_COUNT)

- **Doğrulanan:** Sayım sonucu, defter miktarıyla aynı olan ve fark içermeyen satırları kapsar. Bu kategori, kayıt bazında herhangi bir miktar farkı olmasa da lot farkı içeren kayıtları da içerir. 
(Birebir Doğrulanan + Lot Değişen)  

- **Birebir Doğrulanan:** Doğrulanan satırların alt kümesidir. Malzeme (MATNR), parti (CHARG) ve sayım miktarı (QUAN_COUNT) bilgisinin defter miktarındaki (QUAN_BOOK) bilgi ile tamamen eşleştiği durumu ifade eder.Hem miktar hem de lot bilgisinin eşleştiği doğrulama türüdür.  

- **Lot Değişen:**  Doğrulanan satırların alt kümesidir. Fiziksel sayım sırasında bir malzemenin (`MATNR`) toplam sayım miktarı (`QUAN_COUNT`) ile defterde kayıtlı miktarı (`QUAN_BOOK`) birebir uyuşsa bile, parti numaraları (`CHARG`) farklı olabilir. Bu durum aşağıdaki şekilde ortaya çıkar:  
- Aynı malzeme için:  
  * Sistem kaydında fazla görünen bir parti vardır (`QUAN_DIFF` negatif)  
  * Sayımda ise fazla bulunan farklı bir parti vardır (`QUAN_DIFF` pozitif)  
- Bu iki kayıt, miktar bazında birbirini dengeler ve malzeme seviyesinde fark sıfır görünür.  
- Ancak partiler farklı olduğu için kalite ve izlenebilirlik açısından kritik bir fark oluşur.  

Bu durum, `/SCWM/S_PI_ITEM` tablosu üzerinden analiz edilebilir. Aynı `MATNR` (malzeme numarası) için birden fazla satır oluşur; bu satırlarda farklı `CHARG` (parti) bilgileri ile birlikte birbirini dengeleyen pozitif ve negatif `QUAN_DIFF` değerleri yer alır.  

Sistem, bu tür farkları **malzeme hareketi** olarak değerlendirir ve her bir parti farkı için otomatik olarak **711 / 712** hareket türleriyle kayıt oluşturur.  

Bu nedenle sadece toplam miktar değil, **parti bilgileri** ve **hareket türleri** de dikkate alınarak rapora yansımalıdır.

- **Mutlak Sayım Farkı:** Sayım > Defter ve Defter > Sayım farklarının toplam mutlak değeridir.

- **Yönlü Sayım Farkı:** Sayım > Defter ve Defter > Sayım farklarının cebirsel toplamıdır.

- **Defter > Sayım:**  Yönlü sayım farklarının bir alt kümesidir. Bu kategori, fiziksel sayım sonuçlarına göre sistemde kayıtlı olan defter miktarının (`QUAN_BOOK`), sahada sayılan miktardan (`QUAN_COUNT`) fazla olduğu durumları ifade eder. Bu fark, sistemde fazla gözüken ancak sahada bulunamayan miktarları temsil eder.  

Raporda yer alması beklenen "Defter > Sayım" kalemleri için aşağıdaki şartların dikkate alınması gerekir:  
1. Fiziksel sayım farkları EWM'den SAP'ye kayıt atıldığında, SAP tarafında malzeme belgeleri oluşur. "Defter > Sayım" farkları, SAP'de **712 hareket tipi** ile kaydedilen belgelerle eşleştirilir. Konsolide Z-tablo bu ilişkiyi içermeli, böylece bu kategoriye giren kalemlerin hangi **712** hareketine neden olduğu ve bu hareketin **finansal etkisi (TL)** izlenebilmelidir.  

2. Bir sayım kaleminin (malzeme/parti bazında) "Defter > Sayım" kategorisine alınabilmesi için teknik koşul:  
   **`QUAN_BOOK > QUAN_COUNT`**  

3. **"Lot Değişen"** kategorisine giren kalemler — yani aynı malzeme için farklı partilerde pozitif ve negatif farkların toplamda birbirini götürdüğü, ancak bireysel satırlarda `QUAN_BOOK > QUAN_COUNT` koşulunun sağlandığı durumlar — bu kategoriye **dahil edilmemelidir**. Bu tür kalemler, farklı bir mantıkla tespit edilerek **Lot Değişen:** altında raporlanmalıdır.

- **Sayım > Defter:** Yönlü sayım farkının alt kümesidir. Defter > Sayım da açıklanan kuralları içerecek olup fiziksel sayım sonuçlarına göre, sahada sayılan miktarın (QUAN_COUNT) sistemde kayıtlı olan defter miktarından (QUAN_BOOK) fazla olduğu durumları ifade eder.

#### Diğer Sütun Açıklamaları:
- **Miktar (Adet):** Bu sütun, ilgili kategoriye ait stok miktarını adet cinsinden toplamını gösterir. Örneğin, "Defter" kategorisi için sistemde kayıtlı olan adet miktarını, "Sayım" kategorisi için fiziksel olarak sayılan adet miktarını veya farklılıkların (Mutlak Sayım Farkı, Yönlü Sayım Farkı, Defter > Sayım, Sayım > Defter) adet cinsinden büyüklüğünü ifade eder. 
- **Ağırlık (KG):** Bu sütun, ilgili kategoriye ait stok miktarının kilogram (KG) cinsinden toplam net ağırlığını gösterir. Tıpkı miktar gibi, defterdeki ağırlığı, sayılan ağırlığı veya aradaki ağırlık farklarını (KG cinsinden) ifade eder.  
- **Ağırlık (%):** Bu sütun, her kategori için ağırlık verisinin ilgili ağırlığa göre yüzde karşılığını sunar. Hesaplamalar aşağıdaki formüllerle yapılmaktadır:
- Sayım = Sayım Ağırlığı (KG) / Defter Ağırlığı (KG)
- Doğrulanan = Doğrulanan Ağırlık (KG) / Defter Ağırlığı (KG)
- Birebir Doğrulanan = Birebir Doğrulanan Ağırlık (KG) / Doğrulanan Ağırlık (KG)
- Lot Değişen = Lot Değişen Ağırlık (KG) / Doğrulanan Ağırlık (KG)
- Mutlak Sayım Farkı = Mutlak Sayım Farkı Ağırlığı (KG) / Defter Ağırlığı (KG)
- Yönlü Sayım Farkı = Yönlü Sayım Farkı Ağırlığı (KG) / Defter Ağırlığı (KG)
- Defter > Sayım = Defter > Sayım Ağırlığı (KG) / Mutlak Sayım Farkı Ağırlığı (KG)
- Sayım > Defter = Sayım > Defter Ağırlığı (KG) / Mutlak Sayım Farkı Ağırlığı (KG)
- **Finansal (TL):** Bu sütun, Mutlak Sayım Farkı ve Yönlü Sayım Farkı satırlarında yer alan malzemelerin TL cinsinden finansal değerlerini içerir. Değerler FI modulünden alınmalıdır.

---

### 4.1.2 Detay Analiz Tablosu

#### Amaç
EWM sayım kalemi detaylarını (/SCWM/S_PI_ITEM) ve bu sayım kalemlerinin SAP ERP sisteminde tetiklediği malzeme hareketi (711/712) bilgilerini otomatik olarak birleştiren ve saklayan aşağıdaki başlıkları içeren bir Z-tablo tasarlanması ve fark analizlerinin detaylandırılması hedeflenmektedir. Bu kapsamda 711-712 hareket türleri ile kayıtlara yansıyan, **Defter > Sayım**, **Sayım > Defter** ve **Lot Değişen:**  verileri özetlenip bu raporda satır bazında detaylar görülecektir.

#### Raporlamada Kullanılacak Alanlar
Sayım verilerinin temel kaynağı **/SCWM/S_PI_ITEM** ve 711-712 hareket türlerinin detaylarının yer aldığı **MSEG** tablolarıdır. İlgili tablolarda yer alan ve aşağıda detaylandırılan alanların yer aldığı tabloların hazırlanması hedeflenmektedir.

##### Belge ve Depo Bilgileri (/SCWM/S_PI_ITEM)

| Alan Adı         | Açıklama                           |
|------------------|------------------------------------|
| OWNER            | Sahip                              |
| DOC_YEAR         | Belge Yılı                         |
| DOC_NUMBER       | Fiziksel Envanter Belgesi          |
| LGPLA            | Depo Adresi                        |
| HUIDENT_PARENT   | Taşıma Birimi                      |

##### Malzeme ve Parti Bilgileri (/SCWM/S_PI_ITEM)

| Alan Adı | Açıklama           |
|----------|--------------------|
| MATNR   | Ürün                |
| CHARG   | Parti               |
| MAKTX   | Ürün Kısa Tanımı    |

##### Miktar ve Birim Bilgileri (/SCWM/S_PI_ITEM)

| Alan Adı        | Açıklama                                  |
|------------------|------------------------------------------|
| QUAN_BOOK        | Defter Miktarı                           |
| QUAN_COUNT       | Sayım Miktarı                            |
| QUAN_DIFF        | Fark Miktarı                             |
| QUAN_DIFF_ABS    | Mutlak Fark Miktarı                      |

##### Net Ağırlık Üzerinden Hesaplanan Miktarlar (/SCWM/S_PI_ITEM)

> Ürün ağırlığı **/SAPAPO/MATIO → NTGEW_TC** üzerinden alınarak hesaplamalar yapılacaktır.

| Hesaplama Alanı                  | Açıklama                          |
|----------------------------------|-----------------------------------|
| QUAN_BOOK * NTGEW_TC            | Defter Miktarı Net Ağırlık         |
| QUAN_COUNT * NTGEW_TC           | Sayım Miktarı Net Ağırlık          |
| QUAN_DIFF * NTGEW_TC            | Fark Miktarı Net Ağırlık           |
| QUAN_DIFF_ABS * NTGEW_TC        | Mutlak Fark Miktarı Net Ağırlık    |

##### Diğer Bilgiler (/SCWM/S_PI_ITEM)

| Alan Adı     | Açıklama                          |
|--------------|-----------------------------------|
| COUNT_DATE   | Sayım Tarihi                      |
| COUNT_TIME   | Sayım Saati                       |
| COUNT_USER   | Sayımı Yapan Kullanıcı (Sayaç)    |

##### MM Tablo Bilgileri (MKPF)

| Alan Adı     | Açıklama                          |
|--------------|-----------------------------------|
| SPE_MDNUM_EWM| EWM içinde malzeme belge numarası |

##### Kategori Açıklaması

| Alan Adı     | Açıklama                          |
|--------------|-----------------------------------|
| Fark Türü    | Defter > Sayım, Sayım > Defter,Lot Değişen |

#### Kullanım Senaryosu

Hazırlanacak rapor, hem sistemsel hem de fiziksel olarak envanter verilerinin tutarlılığını izlemek, sapmaların tespitini kolaylaştırmak ve gerektiğinde düzeltici faaliyetleri başlatmak amacıyla kullanılacaktır. Fark analizi, hem miktar hem de ağırlık bazlı olarak incelenecektir.

---

## 5. Özet

- Sayım süreci SAP EWM sistemiyle etkin olarak yürütülmektedir.
- Sayım sonuçları ile sistem kayıtları arasında farkların manuel raporlama ve analiz süreci yürütülmektedir.  
- SAP EWM ile ERP MB51 711-712 kayıtlarının birleştirilerek sistem entegrasyonu ile raporlama süreçlerinin hızlandırılması ve doğruluğun artırılması hedeflenmektedir.
- **Yönetici Özeti** ve **Detay Analiz Tablosu** isimleriyle yukarıda detayları açıklanan içerikte 2 farklı raporun oluşturulması hedeflenmektedir.

---

## 6. Ekler

-  SAP EWM Depo Sayım Talimatı

---

*Rapor sonu.*

