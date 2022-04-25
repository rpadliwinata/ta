import requests
import cv2
import pytesseract
import shutil
from fake_useragent import UserAgent

ua = UserAgent()

proxies = {
    'http': 'socks5h://localhost:9050',
    "https":'socks5h://localhost:9050'
}

user_agent = ua.random
headers = {'User-Agent': user_agent}

session = requests.Session()
session.proxies = proxies
# res = session.get("http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/captcha.php", headers=headers)

# res = requests.get("http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/login.php")
# soup = BS(res.content, 'html.parser')
# image = soup.find('img')
# print(res)

r = session.get("http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/captcha.php", stream=True, headers=headers)
if r.status_code == 200:
    with open("/image.jpg", 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)


pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

img = cv2.imread("../image.jpg")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_NONE)

im2 = img.copy()

x, y, w, h = cv2.boundingRect(contours[0])

rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

cropped = im2[y:y + h, x:x + w]

captcha = pytesseract.image_to_string(cropped)
captcha = captcha.strip()

data = {
    "username": "tugasakhir",
    "password": "tugasakhir",
    "captcha": captcha
}

res = session.post("http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/login.php", data=data, headers=headers)

print(res.text)
print(captcha)
