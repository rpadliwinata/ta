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
    k_word = input("Keyword: ")

    for x in range(limit):
        link = links[x]
        # crawling URL sebelum login
        save_to_file(link, depth=i_depth, pause=i_pause)
        register(10, link)  # 10 jumlah max attempt
        # login -> nama cookie karena mau ambil cookie
        cookie = get_cookie(10, link)
        save_to_file(link, depth=i_depth, pause=i_pause,
                     cookie=cookie)  # crawling setelah login
        # menghapus link yang sama sebelum dan setelah login
        remove_multiple('links.txt')

    link_contain_keyword = []
    crawled_links = [link.strip() for link in open('links.txt', 'r')]
    if len(crawled_links) != 0:  # proses crawling sebelumnya berhasil berarti jalanin
        print("Keyword checking...")
        for x in range(limit):
            link = links[x]
            session = proxy_session()
            headers = random_header()
            cookie = get_cookie(10, link)  # pengecekan konten dengan cookie
            for y in crawled_links:
                if y[:60] == link[:60]:  # ngecek base URL biar pake cookie yang sama
                    if is_contain_keyword(y, k_word, session, cookie):
                        print(f"{y} is contain '{k_word}'")
                        link_contain_keyword.append(y)

        with open(f'{k_word}.txt', 'w+') as file:
            for x in link_contain_keyword:
                file.writelines(f"{x}\n")
    else:
        print('Empty')
