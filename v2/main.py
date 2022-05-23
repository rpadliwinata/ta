from utils import *

default_proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}

if __name__ == "__main__":
    # input parameter crawl link
    cookie = {}
    links = [link.strip() for link in open("onion_list.txt", "r")]
    limit = int(input("Limit: "))
    i_depth = input("Depth: ")
    i_pause = input("Pause: ")

    for x in range(limit):
        link = links[x]
        save_to_file(link)
        register(10, link)
        cookie = get_cookie(10, link)
        save_to_file(link, depth=i_depth, pause=i_pause, cookie=cookie)
        remove_multiple('links.txt')
