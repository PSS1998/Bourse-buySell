from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from os.path import basename
import os


# from selenium import webdriver

# driver = webdriver.Chrome()
# driver.get("http://www.tsetmc.com/Loader.aspx?ParTree=111C1417")
# 
# html = driver.execute_script("return document.documentElement.innerHTML")


# req = Request("http://www.tsetmc.com/Loader.aspx?ParTree=111C1417")
# html_page = urlopen(req)
fn = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bourse-page.html')
soup = BeautifulSoup(open(fn), "html.parser")

# soup = BeautifulSoup(html_page, "html.parser")
# print(soup)

links = []
links2 = []
for link in soup.findAll('a'):
    # print(link)
    links.append(link.get('href'))
for i in range(len(links)):
    if i%2:
        links2.append(links[i])

# print(links2)


links3 = []
for i in range(len(links2)):
	links3.append(links2[i].split("=")[-1])

# print(links3)

f = open("list-bourse-csv.txt", 'w+')
for id in links3:
	f.write("http://www.tsetmc.com/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i={}\n".format(id))