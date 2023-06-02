import csv
import time
import re
import requests

from selenium import webdriver
from urllib.parse import quote


def is_shorts(vid):
    return requests.head(f'https://www.youtube.com/shorts/{vid}', allow_redirects=False).status_code == 200


def get_video_ids_from_link(search_url):
    driver = webdriver.Chrome()
    # 검색 페이지 열기
    driver.get(search_url)
    # 스크롤을 위한 페이지 높이 계산
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    for _ in range(50):
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
    return set(re.findall(r"watch\?v=(\S{11})", html))


def save_to_csv(filename, links):
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for link in links:
            writer.writerow([link])


with open("data/search_query.csv", "r") as query_file:
    reader = csv.reader(query_file)
    result_ids = set()
    for query in reader:
        query_encoded = quote(query[0].encode("utf-8"))
        search_url = f"https://www.youtube.com/results?search_query={query_encoded}"
        ids = get_video_ids_from_link(search_url)
        result_ids.update(ids)
    trending_ids = filter(
        lambda id: not is_shorts(id),
        get_video_ids_from_link('https://www.youtube.com/feed/trending')
    )
    result_ids.update(trending_ids)
    for tid in trending_ids:
        ids = get_video_ids_from_link(f'https://www.youtube.com/watch?v=${tid}')
        result_ids.update(ids)
    save_to_csv("data/yt_id.csv", filter(lambda id: not is_shorts(id), result_ids))
