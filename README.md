# Bourse-buySell
Scarping and analyzing the data needed for buying and selling signals for bource<br/>

## how-to-use
you only have to run the following command:<br/>
bash get-signal.sh<br/>
or you can do it step by step:<br/>
git clone https://github.com/PSS1998/Bourse-buySell.git<br/>
cd Bourse-buySell<br/>
mkdir bourse_price<br/>
wget -E http://www.tsetmc.com/Loader.aspx?ParTree=111C1417<br/>
gzip -d Loader.aspx\?ParTree\=111C1417.html.gz<br/>
mv Loader.aspx\?ParTree\=111C1417.html bourse-page.html<br/>
python3 get_bourse_address.py<br/>
python3 get-bourse-price.py<br/>
ls bourse_price > index.txt<br/>
cd main\ codes<br/>
bash command.sh<br/>
