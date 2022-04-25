from fake_useragent import UserAgent
import shutil
import pytesseract
import cv2
import requests

ua = UserAgent()

proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}

user_agent = ua.random
headers = {'User-Agent': user_agent}

# untuk membuat session
session = requests.Session()
# untuk masang proxie ke sessionnya
session.proxies = proxies

# untuk bikin request ke link onion
r = session.get("http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/captcha.php",
                stream=True, headers=headers)  # stream true itu biar gambar kebaca
# untu mengecek apakah
if r.status_code == 200:
    with open("/image.jpg", 'wb') as f:  # menyimpan gambar captcha
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

# membuka file tesseract untuk libary pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

img = cv2.imread("../image.jpg")
ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

captcha = pytesseract.image_to_string(th1)
captcha = captcha.strip()

data = {
    "username": "tugasakhir",
    "password": "tugasakhir",
    "captcha": captcha
}

res = session.post(
    "http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/login.php", data=data, headers=headers)

cookies = session.cookies.get_dict()
with open("cookies_list.txt", "w") as file:
    for cookie in cookies.values:
        file.write(cookie)


