echo "area,distance,first_registration,fuel,price,search,title,url,year" > drawer/vestland.CSV;
cat *.csv | \
    grep 'finn.no' | \
    grep -E '(5257 Kokstad| Blomsterdalen | Bønes| Sandsli| Rådal)' | \
    sort -u -r >> drawer/vestland.CSV;
