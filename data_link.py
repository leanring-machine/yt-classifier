import csv
import os
import time
import re
from selenium import webdriver
from urllib.parse import quote

def get_video_links(query):
    # 크롬 드라이버 경로 설정
    driver = webdriver.Chrome('C:/Users/User/chromedriver.exe')
    # 유튜브 검색 페이지 URL 생성
    query_encoded = quote(query.encode("utf-8"))
    search_url = f"https://www.youtube.com/results?search_query={query_encoded}"
    # 검색 페이지 열기
    driver.get(search_url)
    # 스크롤을 위한 페이지 높이 계산
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    # 링크를 저장할 set 객체 생성
    video_links = set()
    while len(video_links) <= 2000:
        # 현재 페이지의 HTML 코드 가져오기
        html = driver.page_source
        # 정규표현식을 사용하여 동영상 ID 추출
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        # 동영상 ID를 링크로 변환하여 set 객체에 추가
        video_links.update({"https://www.youtube.com/watch?v=" + id for id in video_ids})
        # 현재 스크롤 위치에서 다음 위치로 스크롤
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        # 스크롤이 더 이상 되지 않을 때까지 기다림
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    driver.quit()
    return list(video_links)[:1000]

def save_to_csv(filename, links):
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Video Links"])
        for link in links:
            writer.writerow([link])

# 검색어 리스트
queries = [("자동차"),#2
           ("영화 및 애니메이션"),#1
           ("음악"),#10
           ("애완동물"),#15
           ("단편영화"),#18
           ("여행"),#19
           ("게임"),#20
           ("Vlog"),#21
           ("사람 및 블로그"),#22
           ("유머"),#23
           ("예능"),#24
           ("뉴스"),#25
           ("패션"),#26
           ("교육"),#27
           ("과학 기술"),#28
           ("비영리 및 사회운동"),#29
           ("영화"),#30
           ("애니메이션"),#31
           ("액션"),#32
           ("클래식"),#33
           ("코미디"),#34
           ("다큐"),#35
           ("드라마"),#36
           ("가족"),#37
           ("외국"),#38
           ("공포"),#39
           ("공상과학"),#40
           ("스릴러"),#41
           ("쇼츠"),#42
           ("TV 프로그램"),#43
           ("예고편")]#44


# 링크를 저장할 폴더 생성
if not os.path.exists("link"):
    os.mkdir("link")

for query in queries:
    links = get_video_links(query)
    save_to_csv("yt_link.csv", links)