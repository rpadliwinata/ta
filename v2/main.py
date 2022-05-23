import requests
import pytesseract
import cv2
import shutil

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from checker import urlcanon, extract_domain, folder
from crawler import crawler

ua = UserAgent()
default_proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}
cookie = {}

# with open("onion_list.txt", "r") as file:
#     onion_links = [x.strip() for x in file]

# link = onion_links[0]
link = 'http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/'
success = False
attempt = 0

while not success or attempt != 10:
    # for link in onion_links:
    session = requests.Session()
    session.proxies = default_proxies
    headers = {'User-Agent': ua.random}

    r = session.get(f"{link}/captcha.php", stream=True, headers=headers)

    if r.status_code == 200:  # memeriksa apakah captcha dapat terakses
        with open("/image.jpg", "wb") as f:  # penyimpanan gambar captcha
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    # membuka file tesseract untuk libary pytesseract
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

    # preprocessing gambar captcha
    img = cv2.imread("/image.jpg")
    ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # melakukan OCR captcha
    captcha = pytesseract.image_to_string(th1)
    captcha = captcha.strip()

    # data untuk register
    data = {
        "username": "tugasakhir",
        "password1": "tugasakhir",
        "password2": "tugasakhir",
        "captcha": captcha
    }
    res = session.post(f"{link}/register.php", data=data, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    warning = soup.find('span', id='warning')
    if warning:
        if warning.text == "Error: Username already exists":
            success = True
    else:
        success = True
    attempt += 1

if not success:
    print("Register failed")

success = False
attempt = 0
while not success or attempt != 10:
    session = requests.Session()
    session.proxies = default_proxies
    headers = {'User-Agent': ua.random}

    r = session.get(f"{link}/captcha.php", stream=True, headers=headers)

    if r.status_code == 200:  # memeriksa apakah captcha dapat terakses
        with open("/image.jpg", "wb") as f:  # penyimpanan gambar captcha
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    # membuka file tesseract untuk libary pytesseract
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

    # preprocessing gambar captcha
    img = cv2.imread("/image.jpg")
    ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # melakukan OCR captcha
    captcha = pytesseract.image_to_string(th1)
    captcha = captcha.strip()

    # data untuk login
    data = {
        "username": "tugasakhir",
        "password": "tugasakhir",
        "captcha": captcha
    }

    # melakukan request untuk halaman login dan mengisi dengan data
    res = session.post(f"{link}/login.php", data=data, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    warning = soup.find('span', id='warning')
    if not warning:
        success = True
        cookie = session.cookies.get_dict()
    attempt += 1


website = urlcanon(link)
outpath = folder(extract_domain(website))
depth = input("Depth: ")
pause = input("Pause: ")
crawler(website, depth, pause, outpath, cookie=cookie, concat=True)

print(cookie)
