import sys



text_file = open("list-bourse-csv.txt", "r")
lines = text_file.read().split()
text_file.close()




from os.path import basename
import os
from urllib.parse import urlsplit
import urllib.request

def url2name(url):
    return basename(urlsplit(url)[2])

def download(url, out_path):
    localName = url2name(url)
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req)

    localName = url.split("=")[-1]+".csv"
    localName = os.path.join(out_path, localName)
    f = open(localName, 'wb+')
    f.write(r.read())
    f.close()

fn = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bourse_price')
for line in lines:
    try:
        download(line, fn)
    except KeyboardInterrupt:
        print("Bye")
        sys.exit()
    except:
        print("Failed "+line)
