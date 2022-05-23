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

links = [link.strip() for link in open("onion_list.txt", "r")]
limit = int(input("Limit: "))
i_depth = input("Depth: ")
i_pause = input("Pause: ")

for x in range(limit):
    link = links[x]
    success = False
    attempt = 1

    website = urlcanon(link)
    outpath = folder(extract_domain(website))
    depth = 1
    pause = 5
    crawler(website, depth, pause, outpath, cookie, concat=True)

    while not success:
        print(f"Attempt number {attempt}")
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
        print("Register failed")
    else:
        print("Register success")

    success = False
    attempt = 1
    while not success:
        print(f"Attempt number {attempt}")
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

        data = {
            "username": "tugasakhir",
            "password": "tugasakhir",
            "captcha": captcha
        }

        # melakukan request untuk halaman login dan mengisi dengan data
        temp = session.get(f"{link}/login.php")
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
    else:
        print("Login success")
        print(cookie)

    website = urlcanon(link)
    outpath = folder(extract_domain(website))
    crawler(website, i_depth, i_pause, outpath, cookie, concat=True)
