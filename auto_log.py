from fake_useragent import UserAgent
import shutil
import pytesseract
import cv2
from modules.crawler import crawler
from modules.checker import *
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


ua = UserAgent()
default_proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}

def read_cookie(path):
    return [x for x in open(path, "r")]


def save_rename(raw, pagefolder, session, url, tag, inner):
    if not os.path.exists(pagefolder):  # create only once
        os.mkdir(pagefolder)
    for result in raw.findAll(tag):  # images, css, etc..
        if result.has_attr(inner):  # check inner tag (file object) MUST exists
            try:
                filename, ext = os.path.splitext(os.path.basename(result[inner]))  # get name and extension
                filename = re.sub('\W+', '', filename) + ext  # clean special chars from name
                fileurl = urljoin(url, result.get(inner))
                filepath = os.path.join(pagefolder, filename)
                # rename html ref so can move html and folder of files anywhere
                result[inner] = os.path.join(os.path.basename(pagefolder), filename)
                if not os.path.isfile(filepath):  # was not downloaded
                    with open(filepath, 'wb') as file:
                        filebin = session.get(fileurl)
                        file.write(filebin.content)
            except Exception as exc:
                print(exc, file=sys.stderr)


def download_home(url, pagepath, proxies, user_agent, cookie):
    session = requests.Session()
    session.proxies = proxies
    headers = {'User-Agent': user_agent}
    response = session.get(url, headers=headers, cookies=cookie)
    raw = BeautifulSoup(response.text, "html.parser")
    path, _ = os.path.splitext(pagepath)
    pagefolder = pagepath + "/" + path + '_files'  # page contents folder
    tags_inner = {'img': 'src', 'link': 'href', 'script': 'src'}  # tag&inner tags to grab
    for tag, inner in tags_inner.items():  # saves resource files and rename refs
        save_rename(raw, pagefolder, session, url, tag, inner)
    with open(pagepath + '/index.html', 'wb') as file:  # saves modified html doc
        file.write(raw.prettify('utf-8'))
    return True


class AutoLog:
    # input untuk link onion seperti login/register serta kebutuhan akses link onion
    def __init__(self, username=None, password=None, limit=None, user_agent=None, proxies=None, tesseract=None, links=None, result=None, cdepth=None, cpause=None):
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
            for x in success:
                if x[1]:
                    print(f"Berhasil register web {x[0]}")

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

        if _print:
            for x in range(self.limit):
                print(f"Cookie web {self.links[x]}: {cookie_list[x]}")

        return cookie_list

    def crawl(self, cookie_list=None):
        cookie_list = cookie_list or "cookie_list.txt"
        cookies = [cookie for cookie in open(cookie_list, "r")]

        for x in range(self.limit):
            website = urlcanon(self.links[x])
            outpath = folder(extract_domain(website))
            crawler(website, self.cdepth, self.cpause,
                    outpath, eval(cookies[x]))
            print(f"{self.links[x]} berhasil di-crawl")

    def download(self):
        existing_cookies = read_cookie("cookie_list.txt")
        for x in range(self.limit):
            outpath = folder(extract_domain(self.links[x]))
            if download_home(self.links[x], outpath, self.proxies, self.user_agent, eval(existing_cookies[x])):
                print(f"{outpath} downloaded")


if __name__ == "__main__":
    al = AutoLog(limit=1)
    registered = al.register(_print=True)
    cookies = al.login(_write=True, _print=True)
    al.crawl()
    al.download()
