import csv
import time
import re
import requests

from selenium import webdriver
from urllib.parse import quote


def is_shorts(vid):
    return requests.head(f'https://www.youtube.com/shorts/{vid}', allow_redirects=False).status_code == 200


def get_video_ids_from_link(search_url):
    """
    Open url in selenium and crawl all vids in page
    :param search_url: link that crawl all vids
    :return: list of vids
    """

    driver = webdriver.Chrome()
    driver.get(search_url)
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    for _ in range(100):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    html = driver.page_source
    driver.quit()
    return set(re.findall(r"watch\?v=(\S{11})", html))


def save_to_csv(filename, ids):
    """
    saving video ids at csv file
    :param filename: file path where to save
    :param ids: id list
    """
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for vid in ids: writer.writerow([vid])


'''
Get Video ID from Youtube webpage
1. Youtube main page (suggest default video in Korea now)
2. Search Keywords about category (from https://gist.github.com/dgp/1b24bf2961521bd75d6c)
3. Trending videos in Korea (now)
'''

result_ids = get_video_ids_from_link('https://www.youtube.com')
with open("data/search_query.csv", "r") as query_file:
    reader = csv.reader(query_file)
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
