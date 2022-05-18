from os import system
from pickle import NONE
import sys
import re
import requests
import time
from bs4 import BeautifulSoup

proxies = {
    'http': 'socks5h://localhost:9050',
    "https": 'socks5h://localhost:9050'
}

# Menghapus bagian yang yang tidak digunakan


def excludes(link, website, outpath):
    if link is None:
        return True
    # URI fragment
    elif '#' in link:
        return True
    # Link Eksternal
    elif link.startswith('http') and not link.startswith(website):
        lstfile = open(outpath + '/extlinks.txt', 'w+')
        lstfile.write(str(link) + '\n')
        lstfile.close()
        return True
    # Nomor Telefon
    elif link.startswith('tel:'):
        lstfile = open(outpath + '/telephones.txt', 'w+')
        lstfile.write(str(link) + '\n')
        lstfile.close()
        return True
    # email
    elif link.startswith('mailto:'):
        lstfile = open(outpath + '/mails.txt', 'w+')
        lstfile.write(str(link) + '\n')
        lstfile.close()
        return True
    # tipe file
    elif re.search('^.*\.(pdf|jpg|jpeg|png|gif|doc)$', link, re.IGNORECASE):
        return True


# Pengecekan dan/ Perbaikan link yang didapatkan
def canonical(link, website):
    # Sudah Sesuai
    if link.startswith(website):
        return link
    # Jika merupakan jalur relatif dengan tanda / didepannya
    elif link.startswith('/'):
        if website[-1] == '/':
            finalLink = website[:-1] + link
        else:
            finalLink = website + link
        return finalLink
    # Jika merupakan jalur relatif tanpa tanda /
    elif re.search('^.*\.(html|htm|aspx|php|doc|css|js|less)$', link, re.IGNORECASE):
        if website[-1] == '/':
            finalLink = website + link
        else:
            finalLink = website + "/" + link
        return finalLink

# Proses Crawling


def crawler(website, cdepth, cpause, outpath, cookie=None, concat=False):
    lst = set()
    ordlst = []
    ordlst.insert(0, website)
    ordlstind = 0
    ttlweb = 0

    print((
        "## Crawling dimulai dari " + website +
        ", dengan " +
        str(cdepth) + " kedalaman crawl, dan pause time selama " +
        str(cpause) + " detik"
    ))

    # Loop Berdasarkan Kedalaman
    for x in range(0, int(cdepth)):

        # Pengulangan untuk tiap tiap item yang ada di ordlst
        for item in ordlst:
            response = None
            global html_page
            # Pengecekan apakah ini merupakan pengulangan pertama ( website input )
            if ordlstind > 0:
                if item is not None:
                    if cookie:
                        response = requests.get(
                            item, proxies=proxies, cookies=cookie)
                    else:
                        response = requests.get(item, proxies=proxies)
            else:
                if cookie:
                    response = requests.get(
                        website, proxies=proxies, cookies=cookie)
                else:
                    response = requests.get(website, proxies=proxies)
                ordlstind += 1

            html_page = response.text
            #soup = BeautifulSoup(html_page, "lxml")
            soup = BeautifulSoup(html_page, "html.parser")

            # Pengulangan  untuk setiap tanda <a href="">
            for link in soup.findAll('a'):
                link = link.get('href')

                if excludes(link, website, outpath):
                    continue

                verlink = canonical(link, website)
                if verlink is not None:
                    lst.add(verlink)

            #  Pengulangan  untuk setiap tanda <area>
            for link in soup.findAll('area'):
                link = link.get('href')

                if excludes(link, website, outpath):
                    continue

                verlink = canonical(link, website)
                if verlink is not None:
                    lst.add(verlink)

            # Masukkan link yang baru ditemukan kedalam ordlst, kemudian melakukan set lagi untuk menghapus jika ada link yang duplikat
            ordlst = ordlst + list(set(lst))
            ordlst = list(set(ordlst))

            # Total Website yang telah di crawling
            ttlweb = ttlweb + 1

            sys.stdout.flush()
            sys.stdout.write("-- Jumlah web yng telah di crawl di kedalamaman " +
                             str(x+1) + " adalah: " + str(ttlweb) + "\r")
            sys.stdout.flush()

            # Jumlah Website yang ditemukan
            sys.stdout.write(
                "\n-- Total link yang ditemukan saat ini : " + str(len(ordlst)) + "\r")
            sys.stdout.flush()

            if x > 0:
                if (ordlst.index(item) != len(ordlst) - 1) and float(cpause) > 0:
                    print("\n-- Proses crawling pause selama " +
                          str(cpause) + " detik\n")
                    time.sleep(float(cpause))

            if concat:
                lstfile = open('links.txt', 'a+')
            else:
                lstfile = open(outpath + '/links.txt', 'w+')

            for item in ordlst:
                lstfile.write("%s\n" % item)
            lstfile.close()

            with open(f"{outpath}/cookie.txt", "w") as file:
                file.write(str(cookie))

        print(("\n## Kedalaman Ke-" + str(x + 1) +
              " selesai dengan jumlah link yang di dapat sebanyak : " + str(len(ordlst))))
        ttlweb = 0
