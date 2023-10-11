from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import google_auth_oauthlib.flow
import random
from pytube import YouTube
from moviepy.editor import *
import shutil
from dotenv import load_dotenv
load_dotenv()

API_KEY1 = os.getenv('API_KEY1')
API_KEY2 = os.getenv('API_KEY2')
API_KEY3 = os.getenv('API_KEY3')

scopes = ["https://www.googleapis.com/auth/youtube.upload", 'https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/youtubepartner', 'https://www.googleapis.com/auth/youtube.force-ssl']

client_secrets_file = "./client_secret"
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_local_server(port=3000)


YOUTUBE = build('youtube', 'v3', developerKey=API_KEY1, credentials=credentials)


class Search:
    """includes all api functionality"""

    def __init__(self):
        self.formats = ["img", "avi", "mov", "gopr"]
        self.format = ''
        # self.searches = self.query()
        self.number = 0
        self.max_results = 50
        self.order = 'relevance'
        self.video_def = 'any'
        self.title_chars = 18
        self.embed = 'any'
        self.video_duration = 'short'
        self.type = 'video'
        self.video_limit = 10
        self.output_path = '/Volumes/graphic_balance/'
        self.file_size = 1e8
        self.random = 'yes'
        # self.published_before = current_time()
    #     self.api_key = ["AIzaSyBesfjYTtAk5vOqCA549-3zr4d4GlCbMvA", "AIzaSyBLwGPRTTLqwPu36ArhTCe9wfaASMaFP7g", "AIzaSyBbjPfpogUhfCptQKixNdKI445O_XFP3hs", "AIzaSyBMOq2KUZg7xFc29bGF9VKQgRHYMEX7tpQ", "AIzaSyBBFpmVkJLy-5iy-4nMGjlzEZWoAfziuuU", "AIzaSyDBxVN6Jb3pYqPfsOM9NdgzItzivNX27QI"
    # ]
        self.download_list = []
        # self.search = self.query()
        self.published_after = '2015-04-23T00:00:00Z'
        # self.location = ''
        # self.location_radius = ''

    def query(self):
        """Outputs 4-digit number formatted with randomly chosen file type from file type list. takes number as input"""
        self.number = str(random.randint(1, 10 ** 4)).zfill(4)
        self.format = random.choice(self.formats)
        if self.format == "gopr":
            return f"{self.format}{self.number}"
        elif self.format == "mov" or self.format == "img":
            return f"{self.format} {self.number}"
        else:
            return f"{self.number}.{self.format}"

    def api_request(self):
        """Conducts search as per search criteria. A list of video ID's are compiled in a list, chosen at random"""
        # API search criteria
        content_details = []
        while True:
            videos = []
            query = self.query()
            request_snippet = YOUTUBE.search().list(
                part='snippet',
                q=query,
                order=self.order,
                type=self.type,
                maxResults=self.max_results,
                videoDefinition=self.video_def,
                videoEmbeddable=self.embed,
                videoDuration=self.video_duration,
                # publishedBefore=self.published_before,
                publishedAfter=self.published_after,
                # location=self.location,
                # locationRadius=self.location_radius,
            )
            response_snippet = request_snippet.execute()
            files_snippet = response_snippet["items"]
            for v_id in files_snippet:
                # title of video as a string
                title = str(v_id["snippet"]["title"]).lower()
                # check if search query is in video title before appending to video ID list
                if str(self.number) in title and self.format in title:
                    if len(title) <= self.title_chars:
                        videos.append(v_id["id"]["videoId"])
                    else:
                        pass
                if len(videos) < 1:
                    continue
            request_content_details = YOUTUBE.videos().list(
                part='contentDetails',
                id=videos
            )
            response_content_details = request_content_details.execute()
            files_content_details = response_content_details["items"]
            print(files_content_details)
            for v_duration in files_content_details:
                time = v_duration['contentDetails']['duration']

                if time <= 'PT1M0S':
                    content_details.append(v_duration['id'])
                    print(time)
            if len(content_details) < 3:
                continue
            else:
                self.download_list = content_details
                print(content_details)
                self.pytube_download()
                self.concatenate()
                self.upload()
                shutil.rmtree('/Users/austingreen/desktop/gb_download')
                os.remove('/Users/austingreen/desktop/gb_edit.mp4')
                return




# ADD DOWNLOAD PROGRESS BAR
    def pytube_download(self):
        directory = 'gb_download'
        parent_dir = '/Users/austingreen/desktop'
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        x = 1
        for video in self.download_list:
            yt = YouTube(f"https://www.youtube.com/watch?v={video}",
                         use_oauth=True,
                         allow_oauth_cache=True)
            yt = yt.streams.get_highest_resolution()
            yt.download(output_path=path, filename_prefix=str(x))
            x += 1
            if x > 10:
                return

    def concatenate(self):
        all_videos = []
        directory = '/Users/austingreen/desktop/gb_download'
        for file_name in os.listdir(directory):
            if file_name.endswith(".mp4"):
                file_path = os.path.join(directory, file_name)
                clip = VideoFileClip(file_path)

                # duration = clip.duration
                width = clip.w
                if width < 1280:
                    continue
                else:
                    all_videos.append(clip)
        random.shuffle(all_videos)
        final_clip = concatenate_videoclips(all_videos, method='compose')
        final_clip.resize(width=1280).write_videofile('/users/austingreen/desktop/gb_edit.mp4', audio_codec="aac")

    def upload(self):
        request_body = {
            'snippet': {
                'categoryId': 22,
                'title': '',
                'description': '',
                'tags': ['people']
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False,
            },
            'notifySubscribers': False
        }

        media_file = MediaFileUpload('/users/austingreen/desktop/gb_edit.mp4', chunksize=-1)
        response_upload = YOUTUBE.videos().insert(
            part='snippet, status',
            body=request_body,
            media_body=media_file
        ).execute()











