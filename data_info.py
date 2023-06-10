import csv
import requests
import os

import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

# 유튜브 API 클라이언트를 생성
youtube = build('youtube', 'v3', developerKey=os.environ["GOOGLE_DEV_KEY"])
category_info = pd.read_csv('data/video_category.csv').set_index('id')['name'].to_dict()


def get_video_id(id_csv, resume_path = None):
    """
    Get Video ID list that crawl video info. id can add after resume_id by read resume_path file
    :param id_csv: path that save id list csv
    :param resume_path: path that save resume id. default is `None`
    :return: List of video id
    """
    result = []
    resume_id = None
    if os.path.isfile(resume_path):
        with open(resume_path, 'r', encoding='utf-8') as resume_file:
            resume_id = resume_file.readline()
            if (not resume_id) or len(resume_id) != 11:
                resume_id = None

    is_append = not resume_id
    with open(id_csv, newline='', encoding='utf-8') as id_csv_file:
        reader = csv.reader(id_csv_file)
        for row in reader:
            video_id = row[0]
            if (not is_append) and resume_id == video_id:
                is_append = True
            if is_append:
                result.append(video_id)
    return result


def api_youtube_info(video_id, info_writer):
    try:
        # 비디오에 대한 정보를 요청
        video_info = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        # 제목, 카테고리, 설명, 비디오 ID추출
        if len(video_info['items']) == 0:
            return None
        snippet = video_info['items'][0]['snippet']
        title = snippet['title']
        category = category_info.get(int(snippet['categoryId']))
        if not category:
            return None
        # description = snippet['description']

        # CSV 파일에 기록할 데이터를 작성
        data = [video_id, title, category]

        # CSV 파일을 쓰기 모드로 열고 데이터 기록
        info_writer.writerow(data)
        return category
    except HttpError as error:
        raise error
    except Exception as e:
        print('-'*10)
        print(e)
        print()
        print(video_info)
        print()
        print(f'video_id : {video_id}')
        print('-' * 10)


def crawl_youtube_csv(video_ids, resume_path):
    with open('data/video_info.csv', mode='a', encoding='utf-8', newline='') as info_file:
        info_writer = csv.writer(info_file)
        if not os.path.isfile(resume_path):
            info_writer.writerow(['video_id', 'title', 'category'])
        for idx, vid in enumerate(video_ids):
            try:
                category = api_youtube_info(vid, info_writer)
                if not category:
                    continue
                thumbnail_url = f'https://img.youtube.com/vi/{vid}/mqdefault.jpg'
                response = requests.get(thumbnail_url)
                with open(f'thumbnail/{category}/{vid}.jpg', 'wb') as f:
                    f.write(response.content)
                print(f'{vid} complete : {idx + 1} of {len(video_ids)}')
            except HttpError:
                print(f'API exceed!! Next time it will download info start at ${vid}')
                with open(resume_path, mode='w', encoding='utf-8') as resume_file:
                    resume_file.write(vid)
                break


ids = get_video_id('data/yt_id.csv', 'data/resume_id')
if not os.path.exists("thumbnail"):
    os.makedirs("thumbnail")
    for c in category_info.values():
        os.makedirs(f"thumbnail/{c}")
crawl_youtube_csv(ids, 'data/resume_id')
