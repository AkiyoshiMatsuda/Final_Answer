import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time

def divide_address(address):
    # 都道府県 + 市区町村 + 番地
    matches = re.match(r'(...??[都道府県])(.+?[市区町村])(.+)', address)
    
    if matches:
        # 市区町村の後ろに数字で始まる番地を切り出すために再度分割
        city_town_village = matches[2]
        address_tail = matches[3].strip()

        # 数字で始まる部分を番地として切り出し
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

url_list = ['https://r.gnavi.co.jp/area/kyoto/rs/?cuisine=CHINESE%2CNOODLE%2CROASTMEAT',
            'https://r.gnavi.co.jp/area/kyoto/rs/?cuisine=CHINESE%2CNOODLE%2CROASTMEAT&p=2',
            'https://r.gnavi.co.jp/area/kyoto/rs/?cuisine=CHINESE%2CNOODLE%2CROASTMEAT&p=3'
            ]
shop_list = []
shop_url_list =[]
tel_list = []
addres_list = []
ssl_list=[]
data_list = []
#店舗名の取得
for url in url_list[:50]:
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"html.parser")
    elems = soup.find_all("h2")
    for elem in elems:
        if "PR" in elem.contents[0]:
                continue
        else :
            shop_list.append(elem.contents[0])
    time.sleep(3)

#クローリングのための店舗ごとのurl取得
for url in url_list:
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"html.parser")
    Elems = soup.find_all("a",href = True)
    for Elem in Elems:
        shop_url = Elem['href']
        #フィルタリング
        if "PR" in Elem.text:
            continue
        #絶対パスに変換
        if not shop_url.startswith("http"):
            shop_url = f'https://r.gnavi.co.jp{shop_url}'
        
        if re.match(r'^https://r.gnavi.co.jp/[\w-]+/$', shop_url):   
            shop_url_list.append(shop_url)
    time.sleep(3)

#店舗ごとの電話番号取得
for shop_link in shop_url_list:
    shop_res = requests.get(shop_link)
    shop_soup = BeautifulSoup(shop_res.text,"html.parser")
    shop_elem = shop_soup.find("span",class_="number")
    tel_list.append(shop_elem.contents[0])
    time.sleep(3)

count = 0
#店舗ごとの住所取得、パース
for shop_link in shop_url_list:
    res = requests.get(shop_link)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text,"html.parser")
    elem = soup.find("span",class_ = "region")
    count += 1
    if count % 2 == 0:
        continue
    else:
        ssl_list.append(shop_url.startswith('https'))
        address = elem.contents[0]
        address_components = divide_address(address)
        addres_list.append(address_components)
    time.sleep(3)


for i in range(len(shop_list[:50])):
    data_dict = {
        "店舗名":shop_list[i],
        "電話番号":tel_list[i],
        "メールアドレス":"",
        "都道府県":addres_list[i]["都道府県"],
        "市区町村":addres_list[i]["市区町村"],
        "番地":addres_list[i]["番地"],
        "建物名":addres_list[i].get("建物名", ""),
        "URL":"",
        "SSL":ssl_list[i]
    }
    data_list.append(data_dict)

df = pd.DataFrame(data_list)
df.to_csv('1-1.csv', index=False, encoding='utf-8-sig')