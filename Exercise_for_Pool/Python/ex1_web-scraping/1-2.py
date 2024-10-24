from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
import pandas as pd
import time

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

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

try:
    cService = ChromeService(executable_path=R"C:\Users\akiyoshi\OneDrive\デスクトップ\Exercise_for_Pool\Python\ex1_web-scraping\chromedriver.exe")
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
        # divide_address関数を使って住所を分割
        address_components = divide_address(addres_list[i])

        data_dict = {
            "店舗名": shop_list[i],
            "電話番号": phone_number_list[i],
            "メールアドレス": "",
            "都道府県": address_components["都道府県"],
            "市区町村": address_components["市区町村"],
            "番地": address_components["番地"],
            "建物名": "",  # divide_addressでは建物名は取得しないため空にする
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
