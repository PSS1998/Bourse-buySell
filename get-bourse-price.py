


text_file = open("list-bource download.txt", "r")
lines = text_file.read().split()
# print lines
# print len(lines)
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
    # if r.info().has_key('Content-Disposition'):
    if 'Content-Disposition' in r.info():
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        if localName[0] == '"' or localName[0] == "'":
            localName = localName[1:-1]
    elif r.url != url: 
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)

    localName = os.path.join(out_path, localName)
    f = open(localName, 'wb+')
    f.write(r.read())
    f.close()

# fn = os.path.join(os.path.dirname(__file__), 'bourse-price')
fn = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bourse_price')
for line in lines:
	download(line, fn)
