import re
import requests
import shutil
import pytesseract
import cv2
import time
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from checker import urlcanon, folder, extract_domain
from crawler import crawler

# Membuat session yang ada proxie


def proxy_session():
    default_proxies = {
        'http': 'socks5h://localhost:9050',
        "https": 'socks5h://localhost:9050'
    }
    session = requests.Session()
    session.proxies = default_proxies
    return session

# Membuat header yang terdapat user agent


def random_header():
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    return headers

# membuat folder hasil crawling yang berisi cookie.txt
# concat=True untuk membuat isi digabung pada file lnks.txt


# parameter yang dibutuhkan
def save_to_file(link, depth, pause, concat=True, cookie=None):
    if not cookie:
        cookie = {}  # agar dapat melakukan crawling dengan cookies
    website = urlcanon(link)
    outpath = folder(extract_domain(website))  # membuat folder dan return path
    crawler(website, depth, pause, outpath, cookie, concat=concat)

# mendapatkan captcha


def get_captcha(link, session, headers=None):
    if not headers:
        headers = random_header()
    # request session captcha
    # stream=True agar gambar dapat terbaca
    r = session.get(f"{link}/captcha.php", stream=True, headers=headers)

    if r.status_code == 200:  # memeriksa apakah captcha dapat terakses
        with open("/image.jpg", "wb") as f:  # penyimpanan gambar captcha
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    # membuka file tesseract untuk libary pytesseract
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

    # preprocessing gambar captcha
    img = cv2.imread("/image.jpg")
    # menghilangkan noise pada captcha
    ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # melakukan OCR captcha
    captcha = pytesseract.image_to_string(th1)
    captcha = captcha.strip()
    return captcha

# melakukan register pada halaman web


def register(limit, link):
    attempt = 1
    success = False
    while not success:
        if attempt == limit:  # mencoba terus sampe limit register
            break
        print(f"Attempt number {attempt}")  # percobaan keberapa

        # pemasangan proxy dan headers untuk link pada onion_links:
        session = proxy_session()
        headers = random_header()
        captcha = get_captcha(link, session, headers)
        # input untuk register
        data = {
            "username": "tugasakhir",
            "password1": "tugasakhir",
            "password2": "tugasakhir",
            "captcha": captcha
        }

        # melakukan register dengan data & header yang dibuat
        res = session.post(f"{link}/register.php", data=data, headers=headers)
        # parse isi dari konten html agar dapat di proses
        soup = BeautifulSoup(res.content, 'html.parser')
        warning = soup.find('span', id='warning')
        if warning:
            if warning.text == "Error: Username already exists":
                success = True
            else:
                print(warning.text)
        else:
            success = True
        attempt += 1

    if not success:
        print("Register failed. Maximum attempt reached")
    else:
        print("Register success")

# login pada halaman web


def get_cookie(limit, link):
    attempt = 1
    success = False
    cookie = {}
    while not success:
        start = time.time()
        if attempt == limit:
            break
        print(f"Attempt number {attempt}")
        session = proxy_session()
        headers = random_header()
        captcha = get_captcha(link, session, headers)

        data = {
            "username": "tugasakhir",
            "password": "tugasakhir",
            "captcha": captcha
        }

        # melakukan request untuk halaman login dan mengisi dengan data
        session.get(f"{link}/login.php")
        res = session.post(f"{link}/login.php", data=data, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        warning = soup.find('span', id='warning')
        if not warning:
            success = True
            cookie = session.cookies.get_dict()
        else:
            print(warning.text)
        attempt += 1

    if not success:
        print("Login failed")
        return {}
    else:
        print("Login success")
        return cookie
