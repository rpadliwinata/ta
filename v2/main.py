from utils import *

default_proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}

if __name__ == "__main__":
    # input parameter crawl link
    cookie = {}
    # links = [link.strip() for link in open("onion_list.txt", "r")]
    link = input("Link: ")
    i_depth = input("Depth: ")
    i_pause = input("Pause: ")
'''
    for x in range(limit):
        link = links[x]
'''
# crawling URL tanpa login
save_to_file(link, depth=i_depth, pause=i_pause)
register(10, link)  # 10 jumlah max attempt
# login -> nama cookie karena mau ambil cookie
cookie = get_cookie(10, link)
save_to_file(link, depth=i_depth, pause=i_pause,
             cookie=cookie)  # crawling setelah login
# menghapus link yang sama sebelum dan setelah login
remove_multiple('links.txt')
