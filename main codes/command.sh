python3 1.py > result1.txt
python3 2.py > result2.txt
python3 3.py > result3.txt
python3 4.py > result4.txt
python3 5.py > result5.txt
python3 6.py > result6.txt
python3 7.py > result7.txt
cat result1.txt | grep -B 1 buy | grep -v buy > buy.txt
cat result2.txt | grep -B 1 buy | grep -v buy >> buy.txt
cat result3.txt | grep -B 1 buy | grep -v buy >> buy.txt
cat result4.txt | grep -B 1 buy | grep -v buy >> buy.txt
cat result5.txt | grep -B 1 buy | grep -v buy >> buy.txt
cat result6.txt | grep -B 1 buy | grep -v buy >> buy.txt
cat result7.txt | grep -B 1 buy | grep -v buy >> buy.txt
cat result1.txt | grep -B 1 sell | grep -v sell > sell.txt
cat result2.txt | grep -B 1 sell | grep -v sell >> sell.txt
cat result3.txt | grep -B 1 sell | grep -v sell >> sell.txt
cat result4.txt | grep -B 1 sell | grep -v sell >> sell.txt
cat result5.txt | grep -B 1 sell | grep -v sell >> sell.txt
cat result6.txt | grep -B 1 sell | grep -v sell >> sell.txt
cat result7.txt | grep -B 1 sell | grep -v sell >> sell.txt
cat buy.txt | grep -v -- -- > buy-signals.txt
cat sell.txt | grep -v -- -- > sell-signals.txt
cat buy-signals.txt | awk -F ".csv" '{print $1}' > buy.txt
cat sell-signals.txt | awk -F ".csv" '{print $1}' > sell.txt
sed -i -e 's/^/http:\/\/www.tsetmc.com\/Loader.aspx?ParTree=151311\&i=/' buy.txt
sed -i -e 's/^/http:\/\/www.tsetmc.com\/Loader.aspx?ParTree=151311\&i=/' sell.txt
cat buy.txt | sort | uniq -c | sort -nk1,1 | tac > buy-signals.txt
cat sell.txt | sort | uniq -c | sort -nk1,1 | tac > sell-signals.txt
rm result1.txt result2.txt result3.txt result4.txt result5.txt result6.txt result7.txt buy.txt sell.txt
