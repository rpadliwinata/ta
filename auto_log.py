import os
import sys
import re
from fake_useragent import UserAgent
import shutil
import pytesseract
import cv2
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from modules.crawler import crawler
from modules.checker import *

ua = UserAgent()
default_proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}


def read_cookie(path):  # baca cookie yang ada di file
    return [x for x in open(path, "r")]

# untuk save directory yang di download agar format sama


def save_rename(raw, pagefolder, session, url, tag, inner):
    if not os.path.exists(pagefolder):  # create only once
        os.mkdir(pagefolder)
    # ini untuk cek halaman html images, css, etc..
    for result in raw.findAll(tag):
        if result.has_attr(inner):  # check inner tag (file object) MUST exists
            try:
                filename, ext = os.path.splitext(os.path.basename(
                    result[inner]))  # get name and extension
                # clean special chars from name
                filename = re.sub('\W+', '', filename) + ext
                fileurl = urljoin(url, result.get(inner))
                # bikin file baru jadi path
                filepath = os.path.join(pagefolder, filename)
                # rename html ref so can move html and folder of files anywhere
                result[inner] = os.path.join(
                    os.path.basename(pagefolder), filename)
                if not os.path.isfile(filepath):  # was not downloaded
                    with open(filepath, 'wb') as file:
                        filebin = session.get(fileurl)
                        file.write(filebin.content)
            except Exception as exc:
                print(exc, file=sys.stderr)


# ini untuk mendownload isi semua file html
def download_home(url, pagepath, proxies, user_agent, cookie):
    session = requests.Session()
    session.proxies = proxies
    headers = {'User-Agent': user_agent}
    response = session.get(url, headers=headers, cookies=cookie)
    raw = BeautifulSoup(response.text, "html.parser")
    path, _ = os.path.splitext(pagepath)
    pagefolder = pagepath + "/" + path + '_files'  # page contents folder
    tags_inner = {'img': 'src', 'link': 'href',
                  'script': 'src'}  # tag&inner tags to grab
    for tag, inner in tags_inner.items():  # saves resource files and rename refs
        save_rename(raw, pagefolder, session, url, tag, inner)
    with open(pagepath + '/index.html', 'wb') as file:  # saves modified html doc
        file.write(raw.prettify('utf-8'))
    return True


class AutoLog:
    # input untuk link onion seperti login/register serta kebutuhan akses link onion
    def __init__(self, username=None, password=None, limit=None, user_agent=None, proxies=None, tesseract=None, links=None, result=None, cdepth=None, cpause=None):  # konstruktor
        self.username = username or "tugasakhir"
        self.password = password or "tugasakhir"
        self.limit = limit or 5
        self.user_agent = user_agent or ua.random
        self.proxies = proxies or default_proxies
        self.tesseract = tesseract or 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
        self.links = links or [link.strip()
                               for link in open("link_list.txt", "r")]
        self.result = result or "cookie_list.txt"
        self.cdepth = cdepth or 1
        self.cpause = cpause or 5

    # metode untuk registrasi
    def register(self, _print=None):
        success = []  # menyimpan array link apakah berhasil diakses
        for x in range(self.limit):
            session = requests.Session()
            session.proxies = self.proxies
            headers = {'User-Agent': self.user_agent}

            # request untuk akses captcha
            r = session.get(
                f"{self.links[x]}/captcha.php", stream=True, headers=headers)

            if r.status_code == 200:  # memeriksa apakah captcha dapat terakses
                with open("/image.jpg", "wb") as f:  # penyimpanan gambar captcha
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

            # membuka file tesseract untuk libary pytesseract
            pytesseract.pytesseract.tesseract_cmd = self.tesseract

            # preprocessing gambar captcha
            img = cv2.imread("/image.jpg")
            ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

            # melakukan OCR captcha
            captcha = pytesseract.image_to_string(th1)
            captcha = captcha.strip()

            data = {
                "username": self.username,
                "password1": self.password,
                "password2": self.password,
                "captcha": captcha
            }

            # request link register dan mengisinya dengan data
            res = session.post(
                f"{self.links[x]}/register.php", data=data, headers=headers)
            if res.status_code == 200:  # mengecek status link apakah dapat terakses
                success.append((self.links[x], True))
            else:
                success.append((self.links[x], False))

        if _print:
            counter = 1
            for x in success:
                if x[1]:
                    print(f"{counter}. Berhasil register web {x[0]}")
                    counter += 1

        return success

    # metode untuk login
    def login(self, _write=None, _print=None):
        cookie_list = []  # penyimpanan array cookie yang didapatkan
        for x in range(self.limit):
            session = requests.Session()
            session.proxies = self.proxies
            headers = {'User-Agent': self.user_agent}

            r = session.get(
                f"{self.links[x]}/captcha.php", stream=True, headers=headers)  # stream true itu biar gambar kebaca
            # untuk mengecek apakah gambar terakses
            if r.status_code == 200:
                with open("/image.jpg", 'wb') as f:  # menyimpan gambar captcha
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

            # membuka file tesseract untuk libary pytesseract
            pytesseract.pytesseract.tesseract_cmd = self.tesseract

            # preprocessing image untuk menghilangkan noise
            img = cv2.imread("/image.jpg")
            ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

            # melakukan OCR pada gambar captcha
            captcha = pytesseract.image_to_string(th1)
            captcha = captcha.strip()

            data = {
                "username": self.username,
                "password": self.password,
                "captcha": captcha
            }

            # melakukan request untuk halaman login dan mengisi dengan data
            res = session.post(
                f"{self.links[x]}/login.php", data=data, headers=headers)
            if res.status_code == 200:  # mengecek apakah link dapat terakses
                cookie = session.cookies.get_dict()
                cookie_list.append(cookie)

        if _write:  # menyimpan cookie di file cookie_list
            with open(self.result, "w") as file:
                file.writelines(str(x) + "\n" for x in cookie_list)

        if _print:  # menampilkan cookie web dari link yang didapatkan
            counter = 1
            for x in range(self.limit):
                print(
                    f"{counter}. Cookie web {self.links[x]}: {cookie_list[x]}")
                counter += 1

        return cookie_list

    def crawl(self, cookie_list=None, concat=False):
        cookie_list = cookie_list or "cookie_list.txt"
        # membaca cookie dari file
        cookies = [cookie for cookie in open(cookie_list, "r")]

        for x in range(self.limit):
            website = urlcanon(self.links[x])
            outpath = folder(extract_domain(website))
            crawler(website, self.cdepth, self.cpause,
                    outpath, eval(cookies[x]), concat=concat)
            print(f"{self.links[x]} berhasil di-crawl\n")

        with open("links.txt", "w+") as file:
            links = [x for x in file]
            links = set(links)
            _ = [file.writelines(x) for x in links]

    def download(self):  # untuk save link html
        existing_cookies = read_cookie("cookie_list.txt")
        for x in range(self.limit):
            outpath = folder(extract_domain(self.links[x]))
            if download_home(self.links[x], outpath, self.proxies, self.user_agent, eval(existing_cookies[x])):
                print(f"{outpath} downloaded")


if __name__ == "__main__":
    al = AutoLog(limit=2, cdepth=2)
    registered = al.register(_print=True)
    cookies = al.login(_write=True, _print=True)
    al.crawl(concat=True)
    # al.download()
