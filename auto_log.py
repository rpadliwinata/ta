import requests
from fake_useragent import UserAgent
import shutil
import pytesseract
import cv2
import requests


ua = UserAgent()
default_proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}


class AutoLog:
    # input untuk link onion seperti login/register serta kebutuhan akses link onion
    def __init__(self, username=None, password=None, limit=None, user_agent=None, proxies=None, tesseract=None, links=None, result=None):
        self.username = username or "tugasakhir"
        self.password = password or "tugasakhir"
        self.limit = limit or 5
        self.user_agent = user_agent or ua.random
        self.proxies = proxies or default_proxies
        self.tesseract = tesseract or 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
        self.links = links or [link.strip()
                               for link in open("link_list.txt", "r")]
        self.result = result or "cookie_list.txt"

    # metode untuk registrasi
    def register(self):
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
        return success

    # metode untuk login
    def login(self):
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
                for val in cookie.values():
                    cookie_list.append(val)

        return cookie_list


if __name__ == "__main__":
    al = AutoLog()
    registered = al.register()

    print("Register status")
    for x in registered:
        print(x)

    cookies = al.login()

    print("Cookies")
    for x in cookies:
        print(x)
    with open(al.result, "w") as file:
        file.writelines(x + "\n" for x in file)
