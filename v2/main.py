import time
from utils import *

default_proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}

def get_input():
    link = input("Link: ")
    i_depth = input("Depth: ")
    return link, i_depth

if __name__ == "__main__":
    # input parameter crawl link
    # links = [link.strip() for link in open("onion_list.txt", "r")]
    link, i_depth = '', ''
    while link == '' and i_depth == '':
        link, i_depth = get_input()
    i_pause = input("Pause: ")
    if i_pause == '':
        i_pause = 0
    else:
        i_pause = int(i_pause)

    start = time.time()
    register(10, link)  # 10 jumlah max attempt
    end = time.time()
    # login -> nama cookie karena mau ambil cookie
    start1 = time.time()
    cookie = get_cookie(10, link)
    end1 = time.time()
    print(f"Time from register : {end-start}")
    print(f"Time from get cookie: {end1-start1}")
    print(f"Time from register to get cookie: {end1-start}")
    save_to_file(link, depth=i_depth, pause=i_pause,
                 cookie=cookie)  # crawling setelah login
