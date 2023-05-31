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


def api_youtube_info(video_id, info_writer):
    try:
        # 비디오에 대한 정보를 요청
        video_info = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        # 제목, 카테고리, 설명, 비디오 ID추출
        snippet = video_info['items'][0]['snippet']
        title = snippet['title']
        category = category_info.get(int(snippet['categoryId']), "others")
        # description = snippet['description']
        video_id = video_info['items'][0]['id']

        # CSV 파일에 기록할 데이터를 작성
        data = [video_id, title, category]

        # CSV 파일을 쓰기 모드로 열고 데이터 기록
        info_writer.writerow(data)
        print(f'{video_id} complete')
        return category


    except HttpError as error:
        print(error.content)
        print('An HTTP error {} occurred:\n{}'.format(error.resp.status, error.content))
    except Exception as e:
        print('-'*10)
        print(video_info)
        print(f'video_id : {video_id}')
        print('-' * 10)
        print(e)



def crawl_youtube_csv(file_path):
    if not os.path.exists("thumbnail"):
        os.makedirs("thumbnail")

    with open('data/video_info.csv', mode='a', encoding='utf-8', newline='') as info_file:
        info_writer = csv.writer(info_file)
        info_writer.writerow(['video_id', 'title', 'category'])
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                video_id = row[0]

                category = api_youtube_info(video_id, info_writer)

                thumbnail_url = f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
                response = requests.get(thumbnail_url)

                if not os.path.exists(f"thumbnail/{category}"):
                    os.makedirs(f"thumbnail/{category}")
                with open(f'thumbnail/{category}/{video_id}.jpg', 'wb') as f:
                    f.write(response.content)

# ids = crawl_youtube_csv('data/yt_id.csv')

crawl_youtube_csv('data/yt_id.csv')
