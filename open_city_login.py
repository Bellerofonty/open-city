import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup


session = requests.Session()
params = {'username': '#####', 'password': '#####',
          'returnUrl': '/lichnyij-kabinet/',
          'service': 'login',
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
          'Accept':'text/html,application/xhtml+xml,application/xml;'\
          'q=0.9,image/webp,*/*;q=0.8'}
##url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/kategorii-ekskursij/peshexodnyie-ekskursii/'
##osob_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/ekskursii/osobnyak-d.b.-nejdgarta.html?date=2018-10-21%2010:30:00'
event_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/kvestyi/kvest-shedevryi-skulpturyi-i-arxitekturyi.html?date=2018-11-10%2012:00:00'
lk_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/lichnyij-kabinet/'
vhod_url = 'https://открытыйгород.рф/vxod.html'
##headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
s = session.post(vhod_url, params)
print(s.cookies.get_dict())
r = session.get(event_url)

##r = requests.get(url, headers = headers)
##r = requests.get(url, auth=HTTPBasicAuth('login', 'password'), headers = headers)

with open('pedestrian.html', 'wb') as output_file:
    output_file.write(r.text.encode('utf-8'))




