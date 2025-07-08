from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# https://developers.google.com/youtube/v3/quickstart/python
# https://developers.google.com/youtube/v3/guides/authentication
# https://developers.google.com/youtube/v3/docs/playlists/insert    
# https://developers.google.com/youtube/v3/docs/playlistItems/insert
# https://developers.google.com/youtube/v3/docs/playlistItems#properties
# https://developers.google.com/youtube/v3/docs/playlistItems#snippet.resourceId
# https://developers.google.com/youtube/v3/docs/playlistItems#snippet.playlistId
# https://developers.google.com/youtube/v3/docs/playlistItems#snippet.position
# https://developers.google.com/youtube/v3/docs/playlistItems#snippet.resourceId.videoId

SCOPES = ["https://www.googleapis.com/auth/youtube"]
url_secret_json = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\secrets\client_secret_770415459794-hkq1qof2195526cshj55utag7v12rt3m.apps.googleusercontent.com.json"
flow = InstalledAppFlow.from_client_secrets_file(url_secret_json, SCOPES)
creds = flow.run_local_server(port=0)
youtube = build("youtube", "v3", credentials=creds)

# ----- playlist data -----
playlist_title = "Techno Peak Time"
urls = [
    "https://www.youtube.com/watch?v=2hsoXTZbhBo",
    "https://www.youtube.com/watch?v=RweK5W3iKxA",
    "https://www.youtube.com/watch?v=j8fOdfNe3xQ",
    "https://www.youtube.com/watch?v=Wo59lWWHVxY",
    "https://www.youtube.com/watch?v=mlzsx1IZd3c",
    "https://www.youtube.com/watch?v=6ohdhNWp7Z4",
    "https://www.youtube.com/watch?v=tH3YN50HyK0",
    "https://www.youtube.com/watch?v=fCf7BRTv4q4",
    "https://www.youtube.com/watch?v=v20Dk7tWKM8",
    "https://www.youtube.com/watch?v=BExPHnKeLjM",
    "https://www.youtube.com/watch?v=Q0okDAhWKH8",
    "https://www.youtube.com/watch?v=OGX36Qm2jwM",
    "https://www.youtube.com/watch?v=u815LRIAFew",
    "https://www.youtube.com/watch?v=40vmSRzKIxA",
    "https://www.youtube.com/watch?v=1bb2viIlDSg",
    "https://www.youtube.com/watch?v=XTxD31PPAh4",
    "https://www.youtube.com/watch?v=dwp7HMHqq2o",
    "https://www.youtube.com/watch?v=y4m5tm0_S5I",
    "https://www.youtube.com/watch?v=TiqAGN70NzI",
    "https://www.youtube.com/watch?v=rfcQlM7YJhA",
    "https://www.youtube.com/watch?v=3y2SWNtb8Lo",
    "https://www.youtube.com/watch?v=dvLwMzo8c70",
    "https://www.youtube.com/watch?v=PgxAz3kzEb0",
    "https://www.youtube.com/watch?v=jNgvlFvST4c",
    "https://www.youtube.com/watch?v=u8jSL0K7nOQ",
    "https://www.youtube.com/watch?v=CX_ZouyKDy0",
    "https://www.youtube.com/watch?v=Z-m3ux8WqEM",
    "https://www.youtube.com/watch?v=6fgWGP-UiPM",
    "https://www.youtube.com/watch?v=7hsMP03cX18",
    "https://www.youtube.com/watch?v=wpUibqj73RM",
    "https://www.youtube.com/watch?v=gtVsjlzkbBw",
    "https://www.youtube.com/watch?v=QWPVuREi8Q4",
    "https://www.youtube.com/watch?v=_emDGhtyYkw",
]

# ----- create playlist -----
pl_request = youtube.playlists().insert(
    part="snippet,status",
    body={"snippet": {"title": playlist_title}, "status": {"privacyStatus": "private"}},
)
playlist_id = pl_request.execute()["id"]

# ----- add items -----
for link in urls:
    if "watch?v=" in link:
        video_id = link.split("watch?v=")[1].split("&")[0]
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        ).execute()

print(f"Playlist ready: https://www.youtube.com/playlist?list={playlist_id}")
