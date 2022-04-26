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

# untuk membuka file link list dan membaca isi file tersebut
with open("link_list.txt", "r") as file:
    links = [link for link in file]

limit = 5
cookies = []

for x in range(limit):
    # untuk bikin request ke link onion dan mengambil gambar captcha
    # stream true itu biar gambar kebaca
    r = session.get(f"{links[x]}/captcha.php", stream=True, headers=headers)
    # untuk mengecek apakah gambar berhasil di ambil
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
        "username": "tugasakhir",
        "password": "tugasakhir",
        "captcha": captcha
    }
    res = session.post(f"{links[x]}/login.php", data=data, headers=headers)
    cookie = session.cookies.get_dict()
    for val in cookie.values():
        cookies.append(val)

with open("cookies_list.txt", "w") as file:
    for cookie in cookies:
        file.writelines(cookie)
