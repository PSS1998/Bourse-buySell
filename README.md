# Bourse-buySell
Scarping and analyzing the data needed for buying and selling signals for boirce<br/>

## how-to-use
first run wget -E http://www.tsetmc.com/Loader.aspx?ParTree=111C1417<br/>
second run gzip -d Loader.aspx\?ParTree\=111C1417.html.gz and mv Loader.aspx\?ParTree\=111C1417.html bourse-page.html<br/>
third run get-bourse-address to get complete bourse list<br/>
fourth run get-bourse-price python code in root directory to get bourse prices  
fifth copy each file you want from main code folder to bourse_price folder<br/>
sixth run each file in bourse_price folder and get results<br/>
