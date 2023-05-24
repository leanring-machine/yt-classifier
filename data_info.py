import csv
import requests
import re
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# DEVELOPER_KEY = ''
YOUTUBE_API_VERSION = 'v3'

# 유튜브 API 클라이언트를 생성
youtube = build('youtube', YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


def extract_youtube_links(text):
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/watch\?v=([^\s]+)'
    links = re.findall(youtube_regex, text)
    return ['https://www.youtube.com/watch?v=' + link[3] for link in links]

def api_youtube_info(video_id):

    try:
        # 비디오에 대한 정보를 요청
        video_info = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        # 제목, 카테고리, 설명, 비디오 ID추출
        title = video_info['items'][0]['snippet']['title']
        category = video_info['items'][0]['snippet']['categoryId']
        description = video_info['items'][0]['snippet']['description']
        video_id = video_info['items'][0]['id']

        # 출력
        print('제목: {}'.format(title))
        print('카테고리: {}'.format(category))
        print('설명: {}'.format(description))
        print('비디오 ID: {}'.format(video_id))

        # CSV 파일에 기록할 데이터를 작성
        data = [title, category, description, video_id]

        # CSV 파일을 쓰기 모드로 열고 데이터 기록
        with open('data/video_info.csv', mode='a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            print('CSV 파일에 저장되었습니다.')

    except HttpError as error:
        print('An HTTP error {} occurred:\n{}'.format(error.resp.status, error.content))


def crawl_youtube_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            video_id = row[0]

            api_youtube_info(video_id)

            thumbnail_url = f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
            print(video_id)
            response = requests.get(thumbnail_url)


            if not os.path.exists("thumbnail"):
                os.makedirs("thumbnail")

            with open(f'{"thumbnail"}/{video_id}.jpg', 'wb') as f:
                f.write(response.content)


crawl_youtube_csv('data/yt_id.csv')