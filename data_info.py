import csv
import requests
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

# 유튜브 API 클라이언트를 생성
youtube = build('youtube', 'v3', developerKey=os.environ["GOOGLE_DEV_KEY"])


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
        category = snippet['categoryId']
        # description = snippet['description']
        video_id = video_info['items'][0]['id']

        # CSV 파일에 기록할 데이터를 작성
        data = [video_id, title, category]

        # CSV 파일을 쓰기 모드로 열고 데이터 기록
        info_writer.writerow(data)
        print(f'{video_id} complete')

    except HttpError as error:
        print('An HTTP error {} occurred:\n{}'.format(error.resp.status, error.content))


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

                api_youtube_info(video_id, info_writer)

                thumbnail_url = f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
                response = requests.get(thumbnail_url)

                with open(f'{"thumbnail"}/{video_id}.jpg', 'wb') as f:
                    f.write(response.content)


crawl_youtube_csv('data/yt_id.csv')