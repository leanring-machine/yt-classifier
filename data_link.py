import csv
import time
import re
from selenium import webdriver
from urllib.parse import quote


def get_video_links(query):
    driver = webdriver.Chrome()
    # 유튜브 검색 페이지 URL 생성
    query_encoded = quote(query.encode("utf-8"))
    search_url = f"https://www.youtube.com/results?search_query={query_encoded}"
    # 검색 페이지 열기
    driver.get(search_url)
    # 스크롤을 위한 페이지 높이 계산
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    for _ in range(100):
        # 현재 스크롤 위치에서 다음 위치로 스크롤
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        # 스크롤이 더 이상 되지 않을 때까지 기다림
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    html = driver.page_source
    driver.quit()
    return list(set(re.findall(r"watch\?v=(\S{11})", html)))[:1000]


def save_to_csv(filename, links):
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for link in links:
            writer.writerow([link])


with open("data/search_query.csv", "r") as query_file:
    reader = csv.reader(query_file)
    for query in reader:
        links = get_video_links(query[0])
        save_to_csv("data/yt_id.csv", links)
