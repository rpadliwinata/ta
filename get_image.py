from fake_useragent import UserAgent
import requests
import shutil

ua = UserAgent()

proxies = {
    'http': 'socks5h://localhost:9050',
    "https":'socks5h://localhost:9050'
}

headers = {'User-Agent': ua.random}

session = requests.session()
session.proxies = proxies

r = session.get("http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/captcha.php", stream=True, headers=headers)
if r.status_code == 200:
    with open("/image.jpg", 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)