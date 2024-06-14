from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import urllib.request
import urllib
import time
import os
from datetime import datetime

path = "chromedriver(123).exe"
service = Service(executable_path=path)

print("="*70,"\npixabay 사이트에서 이미지를검색하여 수집하는 크롤러 입니다.\n","="*70)
keyWord = input("크롤링할 이미지의 키워드는 무엇입니까?:")
cnt = int(input("크롤링 할 건수는 몇건입니까?:"))
savePath = input("결과를 저장할 디렉터리 경로를 입력하시오:(ex:C:\\Users\\popoj\\Desktop\\test)")

driver = webdriver.Chrome(service=service)
driver.get("https://pixabay.com/ko/")
time.sleep(2) 

search_input = driver.find_element(By.NAME, "search")
search_input.send_keys(keyWord)
search_input.submit()
time.sleep(2)

def scroll_down(driver):
    total_height = driver.execute_script("return document.body.scrollHeight")
    scroll_unit = 200
    current_position = 0
    
    while True:
        next_position = current_position + scroll_unit
        if next_position >= total_height:
            driver.execute_script(f"window.scrollTo({current_position}, {total_height});")
            break
        driver.execute_script(f"window.scrollTo({current_position}, {next_position});")
        current_position = next_position
        time.sleep(0.2)

image_sources = []
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}

# 
image_counts = [] 

while len(image_sources) < cnt:
    scroll_down(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    image_elements = soup.find_all(class_="cell--B7yKd")
    
    # 
    image_counts.append(len(image_elements))
    for img_element in image_elements:
        img_tag = img_element.find("img")
        if img_tag is not None:
            # 성인 세이프 가드 오류 처리
            img_url = img_tag["src"]
            if img_url not in image_sources:
                image_sources.append(img_url)
            if len(image_sources) >= cnt:
                break

    if len(image_sources) >= cnt:
        break
    try:
        more_button = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div[4]/div[2]/a/span')
        more_button.click()
        time.sleep(2)
    except:
        break

now = datetime.now()
folder_name = f"{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}-{now.minute:02d}-{now.second:02d}-{keyWord}"
savePath = os.path.join(savePath, folder_name)
if not os.path.exists(savePath):
    os.makedirs(savePath)

# 이미지 다운 파트
for i, img_url in enumerate(image_sources[:cnt]):
    file_name = f"{i+1}.{img_url.split('.')[-1]}"
    req = urllib.request.Request(img_url, headers=headers)
    with urllib.request.urlopen(req) as response, open(os.path.join(savePath, file_name), 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print(f"현재 {i+1}/{cnt} 이미지를 다운로드중입니다\n주소:{img_url}")


print("파싱된 이미지 소스 개수:", image_counts)  
print("이미지 다운로드가 완료되었습니다.")
driver.quit()