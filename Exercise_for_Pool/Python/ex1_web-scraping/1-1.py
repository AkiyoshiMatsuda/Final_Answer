import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time

def divide_address(address):
    matches = re.match(r'(...??[都道府県])(.+?[市区町村])(.+)', address)
    if matches:
        city_town_village = matches[2]
        address_tail = matches[3].strip()
        detailed_address = re.match(r'([^\d]+)(\d.+)', address_tail)
        if detailed_address:
            return {
                "都道府県": matches[1],
                "市区町村": city_town_village + detailed_address[1].strip(),
                "番地": detailed_address[2].strip()
            }
        else:
            return {
                "都道府県": matches[1],
                "市区町村": city_town_village.strip(),
                "番地": address_tail.strip()
            }
    else:
        return {
            "都道府県": "",
            "市区町村": "",
            "番地": ""
        }

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}

base_url = 'https://r.gnavi.co.jp/area/kyoto/rs/?cuisine=CHINESE%2CNOODLE%2CROASTMEAT'
next_page = base_url
shop_list = []
shop_url_list = []
tel_list = []
addres_list = []
ssl_list = []
data_list = []

while next_page:
    res = requests.get(next_page)
    soup = BeautifulSoup(res.text, "html.parser")
    
    # 店舗名を取得
    elems = soup.find_all("h2")
    for elem in elems:
        if "PR" in elem.contents[0]:
            continue
        else:
            shop_list.append(elem.contents[0])
    
    # クローリングのための店舗ごとのurl取得
    Elems = soup.find_all("a", href=True)
    for Elem in Elems:
        shop_url = Elem['href']
        if "PR" in Elem.text:
            continue
        if not shop_url.startswith("http"):
            shop_url = f'https://r.gnavi.co.jp{shop_url}'
        if re.match(r'^https://r.gnavi.co.jp/[\w-]+/$', shop_url):
            shop_url_list.append(shop_url)
    
    # 次のページリンクを探す
    next_elem = soup.find("a", {"class": "next"})  # '次へ'ボタンのリンクを取得
    if next_elem and "href" in next_elem.attrs:
        next_page = f'https://r.gnavi.co.jp{next_elem["href"]}'
    else:
        next_page = None
    
    time.sleep(3) 
# 店舗ごとの住所取得とSSL確認
for shop_link in shop_url_list:
    res = requests.get(shop_link, headers=headers)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")
    
    # 電話番号取得
    shop_elem = soup.find("span", class_="number")
    if shop_elem:
        tel_list.append(shop_elem.contents[0])
    else:
        tel_list.append("電話番号なし")
    
    # 住所取得
    elem = soup.find("span", class_="region")
    if elem:
        address = elem.contents[0]
        address_components = divide_address(address)
        addres_list.append(address_components)
    else:
        # 住所が取得できなかった場合に空のデータを追加
        print(f"住所が取得できませんでした: {shop_link}")
        addres_list.append({"都道府県": "", "市区町村": "", "番地": ""})
    
    # SSL確認
    ssl_list.append(shop_link.startswith('https'))
    
    time.sleep(3)

# データをCSVに書き込む
for i in range(len(shop_list)):
    data_dict = {
        "店舗名": shop_list[i],
        "電話番号": tel_list[i],
        "メールアドレス": "",
        "都道府県": addres_list[i]["都道府県"],
        "市区町村": addres_list[i]["市区町村"],
        "番地": addres_list[i]["番地"],
        "建物名": addres_list[i].get("建物名", ""),
        "URL": "",
        "SSL": ssl_list[i]
    }
    data_list.append(data_dict)

df = pd.DataFrame(data_list)
df.to_csv('1-1.csv', index=False, encoding='utf-8-sig')