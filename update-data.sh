wget -E http://www.tsetmc.com/Loader.aspx?ParTree=111C1417
gzip -d Loader.aspx?ParTree=111C1417.html.gz
mv Loader.aspx?ParTree=111C1417.html bourse-page.html
python3 get_bourse_address.py
python3 get-bourse-price.py
ls bourse_price > index.txt
