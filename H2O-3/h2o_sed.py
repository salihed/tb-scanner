import h2o
h2o.init(port=54922)  # Farklı bir port numarası deneyin

# H2O-3 başlatma
h2o.init()

# Veri setini yükle
data = h2o.import_file(r"C:\Users\salih.dogrubak\Documents\SAP\SAP GUI\export.XLSX")

# Başlangıçta H2O'un başarılı bir şekilde başlatıldığını kontrol et
print(h2o.cluster_info())