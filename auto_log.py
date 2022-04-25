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
    def __init__(self, username=None, password=None, limit=None, user_agent=None, proxies=None, tesseract=None, links=None, result=None):
        self.username = username or "tugasakhir"
        self.password = password or "tugasakhir"
        self.limit = limit or 5
        self.user_agent = user_agent or ua.random
        self.proxies = proxies or default_proxies
        self.tesseract = tesseract or 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
        self.links = links or [link.strip() for link in open("link_list.txt", "r")]
        self.result = result or "/cookie_list.txt"

    def register(self):
        success = []
        for x in range(self.limit):
            session = requests.Session()
            session.proxies = self.proxies
            headers = {'User-Agent': self.user_agent}

            r = session.get(f"{self.links[x]}/captcha.php", stream=True, headers=headers)

            if r.status_code == 200:
                with open("/image.jpg", "wb") as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

            pytesseract.pytesseract.tesseract_cmd = self.tesseract

            img = cv2.imread("/image.jpg")
            ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

            captcha = pytesseract.image_to_string(th1)
            captcha = captcha.strip()

            data = {
                "username": self.username,
                "password1": self.password,
                "password2": self.password,
                "captcha": captcha
            }

            res = session.post(f"{self.links[x]}/register.php", data=data, headers=headers)
            if res.status_code == 200:
                success.append((self.links[x], True))
            else:
                success.append((self.links[x], False))
        return success

    def login(self):
        cookie_list = []
        for x in range(self.limit):
            session = requests.Session()
            session.proxies = self.proxies
            headers = {'User-Agent': self.user_agent}

            r = session.get(f"{self.links[x]}/captcha.php", stream=True, headers=headers)  # stream true itu biar gambar kebaca
            # untuk mengecek apakah
            if r.status_code == 200:
                with open("/image.jpg", 'wb') as f:  # menyimpan gambar captcha
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

            # membuka file tesseract untuk libary pytesseract
            pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

            img = cv2.imread("/image.jpg")
            ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

            captcha = pytesseract.image_to_string(th1)
            captcha = captcha.strip()

            data = {
                "username": self.username,
                "password": self.password,
                "captcha": captcha
            }

            res = session.post(f"{self.links[x]}/login.php", data=data, headers=headers)
            if res.status_code == 200:
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
        for cookie in cookies:
            file.writelines(cookie)



