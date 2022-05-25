import re

import requests
import shutil
import pytesseract
import cv2
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from checker import urlcanon, folder, extract_domain
from crawler import crawler

def proxy_session():
    default_proxies = {
        'http': 'socks5h://localhost:9050',
        "https": 'socks5h://localhost:9050'
    }
    session = requests.Session()
    session.proxies = default_proxies
    return session

def random_header():
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    return headers

def save_to_file(link, depth=2, pause=5, concat=True, cookie=None):
    if not cookie:
        cookie = {}
    website = urlcanon(link)
    outpath = folder(extract_domain(website))
    crawler(website, depth, pause, outpath, cookie, concat=concat)

def get_captcha(link, session, headers=None):
    if not headers:
        headers = random_header()

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
    return captcha

def register(limit, link):
    attempt = 1
    success = False
    while not success:
        if attempt == limit:
            break
        print(f"Attempt number {attempt}")
        # for link in onion_links:
        session = proxy_session()
        headers = random_header()

        captcha = get_captcha(link, session, headers)

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
                print(warning.text)
        else:
            success = True
        attempt += 1

    if not success:
        print("Register failed. Maximum attempt reached")
    else:
        print("Register success")

def get_cookie(limit, link):
    attempt = 1
    success = False
    cookie = {}
    while not success:
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
        print(cookie)
        return cookie

def remove_multiple(file):
    links = [x.strip() for x in open('links.txt', 'r+')]

    temp = []
    res = []
    current = links[0]

    for x in links:
        if x[:15] == current[:15]:
            temp.append(x)
        else:
            current = x
            res.extend(list(set(temp)))
            temp = []
    res.extend(list(set(temp)))

    with open('links.txt', 'r+') as file:
        file.truncate(0)
        for x in res:
            file.writelines(f"{x}\n")

def is_contain_keyword(link, keyword, session, cookie):
    headers = random_header()
    response = session.get(link, headers=headers, cookies=cookie)
    soup = BeautifulSoup(response.content, 'html.parser')
    result = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
    return len(result) > 0

