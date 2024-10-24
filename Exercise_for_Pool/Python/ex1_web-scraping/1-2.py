from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
import pandas as pd
import time

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
try:
    cService = ChromeService(executable_path=R"C:\Users\akiyoshi\OneDrive\デスクトップ\インターン\chromedriver.exe")
    driver = webdriver.Chrome(service=cService, options=chrome_options)
    driver.get('https://www.gnavi.co.jp/')
    search_area = driver.find_element(By.NAME, "suggest-area")
    search_kind = driver.find_element(By.NAME, "suggest-number")

    shop_list = []
    url_list = []
    phone_number_list = []
    addres_list = []
    ssl_list = []

    # 検索条件
    search_area.send_keys("京都府")
    search_kind.send_keys("焼肉")
    search_button = driver.find_element(By.XPATH, '//*[@id="top"]/main/form/div/div/div/div/div[4]/button')
    search_button.click()

    # 1ページ目
    for i in range(1, 50):
        for elem_h2 in driver.find_elements(By.XPATH, f'//*[@id="__next"]/div/div[2]/main/div[9]/div[2]/div[{i}]/article/div[1]/a/h2'):
            elem_a = elem_h2.find_element(By.XPATH, '..')
            shop_list.append(elem_h2.text)
            url = elem_a.get_attribute('href')
            url_list.append(url)

    # 2ページ目
    search_button2 = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/main/div[10]/nav/ul/li[10]/a')
    search_button2.click()
    for i in range(1, 50):
        for elem_h2 in driver.find_elements(By.XPATH, f'//*[@id="__next"]/div/div[2]/main/div[9]/div[2]/div[{i}]/article/div[1]/a/h2'):
            elem_a = elem_h2.find_element(By.XPATH, '..')
            shop_list.append(elem_h2.text)
            url = elem_a.get_attribute('href')
            url_list.append(url)
        if len(shop_list) == 50:
            break
    for link in url_list:
        driver.get(link)
        try:
            phone_number = driver.find_element(By.XPATH, '//*[@id="header-wrapper"]/div/div[2]/div[2]/div').text
        except:
            phone_number = "N/A"
        phone_number_list.append(phone_number)

        try:
            # 住所を取得するための複数のXPathを試みる
            try:
                addres = driver.find_element(By.XPATH, '//*[@id="info-table"]/table/tbody/tr[3]/td/p/span').text
            except:
                addres = driver.find_element(By.XPATH, '//*[@id="alternate-address-path"]').text
        except:
            addres = "N/A"
        addres_list.append(addres)

        # SSLチェック
        if link.startswith("https://"):
            ssl_list.append(True)
        else:
            ssl_list.append(False)

    # データの整形
    data_list = []
    for i in range(len(shop_list)):
        address_pattern = re.compile(
            r'(?P<都道府県>[^\s]+?[都道府県])\s*'  # 「都」「道」「府」「県」で終わるパターン
            r'(?P<市区町村>[^\s]+?[市区町村]?[区町村])\s*'  # 「市」「区」「町」「村」で終わるパターン
            r'(?P<番地>[^\s]+(?:\d+[-\d]*)?)\s*'  # 番地（数字とハイフンを含む可能性がある）
            r'(?P<建物名>.*)'
        )
        match = address_pattern.match(addres_list[i])
        if match:
            address_components = match.groupdict()
        else:
            address_components = {
                "都道府県": addres_list[i].split()[0] if addres_list[i] != "N/A" else "不明",
                "市区町村": "不明",
                "番地": "不明",
                "建物名": "不明"
            }

        data_dict = {
            "店舗名": shop_list[i],
            "電話番号": phone_number_list[i],
            "メールアドレス": "",
            "都道府県": address_components["都道府県"],
            "市区町村": address_components["市区町村"],
            "番地": address_components["番地"],
            "建物名": address_components["建物名"],
            "URL": url_list[i],
            "SSL": ssl_list[i]
        }
        data_list.append(data_dict)

    # CSVに書き込み
    df = pd.DataFrame(data_list)
    df.to_csv('1-2.csv', index=False, encoding='utf-8-sig')

except Exception as e:
    print(f"Error occurred: {e}")
    driver.quit()