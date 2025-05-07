import investpy

# Türkiye'deki bir fonun verilerini çekme
df = investpy.get_fund_historical_data(fund='Fon Adı', country='Turkey', from_date='01/01/2020', to_date='01/01/2025')
print(df)
