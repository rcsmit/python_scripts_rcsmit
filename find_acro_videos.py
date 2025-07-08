
def find_first_youtube_video(search ):
    """
    Finds the first YouTube video for a given search query.

    This function uses the YouTube Data API to search for videos based on the provided 
    search query. It retrieves the first video result and returns its YouTube URL.


    To set up the YouTube API, follow these steps:

    1. **Go to the Google Cloud Console**:
    - Visit: [Google Cloud Console](https://console.cloud.google.com/)

    2. **Create a Project**:
    - In the Google Cloud Console, click on the project dropdown and select **New Project**. Provide a name for your project and click **Create**.

    3. **Enable the YouTube Data API**:
    - Navigate to the YouTube API page: [YouTube API](https://console.cloud.google.com/apis/api/youtube.googleapis.com/)
    - Click **Enable** to enable the API for your project.

    4. **Create Credentials**:
    - Go to the **Credentials** page: [Credentials](https://console.cloud.google.com/auth/clients)
    - Click **Create Credentials** and select **API Key** or **OAuth 2.0 Client ID** (depending on your needs). If you're using OAuth, follow the steps to set up consent screens and redirect URIs.

    5. **Obtain API Key/Client ID**:
    - After creating your credentials, you'll be able to download or copy your **API Key** or **Client ID**, which you'll use to authenticate API requests.
    - the key is in keys.py as api_key_youtube. Don't forget to add it to the .gitignore file if you are using git. 

    6. **API Metrics**:
    - To view API usage metrics, visit: [API Metrics](https://console.cloud.google.com/apis/api/youtube.googleapis.com/metrics?project=project_name)

    7. ** Usage**:
    https://developers.google.com/youtube/v3/determine_quota_cost
    A search costs 100 credits. The quota is normally 10_000 credits per day. (so 100 searches)
    
    - Make sure to read the API documentation to understand how to use the API effectively and what quota limits apply to your project.
    - You can find the API documentation here: [YouTube Data API v3](https://developers.google.com/youtube/v3/docs) 

    Once you have completed these steps, you can start making requests to the YouTube Data API using the provided credentials.
    Setup API:
    https://console.cloud.google.com/
    https://console.cloud.google.com/auth/clients
    https://console.cloud.google.com/apis/api/youtube.googleapis.com/ - ["Credentials"]

    Metrics: [Click the tab "quota & system limits"]
    https://console.cloud.google.com/apis/api/youtube.googleapis.com/metrics?project=gpxanalyzer-454406
    
    Args:
        search (str): The search query string to look for on YouTube.

    Returns:
        str: The URL of the first YouTube video matching the search query.

    Raises:
        Exception: If the API request fails (e.g., invalid API key, network issues).
        KeyError: If no video is found for the given search query.

    Notes:
        - The function requires a valid YouTube Data API key, which should be stored 
          in the `api_key_youtube` variable.
        - Ensure that the API key has sufficient quota and access to the YouTube Data API.

    Example:
        >>> find_first_youtube_video("Taylor Swift - Love Story")
        'https://www.youtube.com/watch?v=8xg3vE8Ie_E'
    """
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": search,
        "type": "video",
        "maxResults": 1,
        "key": api_key_youtube
    }
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        if response.status_code == 403:
            print("API request failed with status code 403: Forbidden. Check your API key and quota.")
        else:
            print(f"API request failed with status code {response.status_code}")
        return None, None
    else:
        data = response.json()
    
        if "items" not in data or not data["items"]:
            raise KeyError("No video found")
        
        video_id = data["items"][0]["id"]["videoId"]

        video_title = data["items"][0]["snippet"]["title"]
        

        link = f"https://www.youtube.com/watch?v={video_id}"
        return link, video_title


data = {
  nodes: [
   {
      "id": "PljVGr8iR2YL2gw-_0Ea-7" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "",
      "x": 1150,
      "y": 1110
    },
    {
      "id": "Jq25LovILjKADiAHG79u-108" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "",
      "x": 34,
      "y": 1058
    },
    {
      "id": "Jq25LovILjKADiAHG79u-104" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "",
      "x": 189,
      "y": 1080
    },
    {
      "id": "Jq25LovILjKADiAHG79u-101" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "<b><font style=\"font-size: 14px;\">LEGENDA</font></b>",
      "x": 1496,
      "y": 780
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-1" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "front plank",
      "x": 36,
      "y": 550
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-2" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "front bird",
      "x": 350,
      "y": 550
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-5" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "folded leaf",
      "x": 650,
      "y": 550
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-7" ,
      "info":"loremp ipsum",
      "video":"3ZU_kP1pu5Y",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "straddle throne",
      "x": 530,
      "y": 640
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-8" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "chair",
      "x": 530,
      "y": 750
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-9" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "foot to shin",
      "x": 350,
      "y": 750
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-17" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "couch",
      "x": 720,
      "y": 640
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-21" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse straddle throne",
      "x": 890,
      "y": 715
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-24" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "shin to foot",
      "x": 36,
      "y": 848
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-26" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "flamingo",
      "x": 36,
      "y": 758
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-29" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "maria pose",
      "x": 36,
      "y": 948
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-31" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "high flying whale",
      "x": 530,
      "y": 850
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-33" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "candle stick / shoulder stand",
      "x": 345,
      "y": 370
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-35" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "free shoulder stand",
      "x": 553,
      "y": 370
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-40" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "side star",
      "x": 36,
      "y": 655
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-42" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "straddle bat",
      "x": 1201,
      "y": 550
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-44" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "inside side star <br> ",
      "x": 1201,
      "y": 410
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-46" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "inside side star <br> ",
      "x": 1348,
      "y": 490
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-48" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse bird <br> ",
      "x": 1488,
      "y": 490
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-51" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "floating paschi",
      "x": 1348,
      "y": 680
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-55" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "backbird",
      "x": 1302,
      "y": 880
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-57" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "back leaf",
      "x": 1202,
      "y": 970
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-59" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "boat",
      "x": 1342,
      "y": 970
    },
    {
      "id": "ylEB-xLuXJku9rSygnK5-63" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "star",
      "x": 900,
      "y": 290
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-5" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "handstand in/out (head side) ",
      "x": 1152,
      "y": 870
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-8" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "four step",
      "x": 900,
      "y": 190
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-15" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "cartwheel in",
      "x": 1201,
      "y": 290
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-17" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "low barrel rol",
      "x": 809,
      "y": 480
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-23" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "helicopter",
      "x": 720,
      "y": 370
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-27" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "catherinas wheel",
      "x": 433,
      "y": 460
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-30" ,
      "info":"loremp ipsum",
      "video":"aO9-OqnAeDk",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "monkey frog",
      "x": 980,
      "y": 850
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-33" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "corkscrew",
      "x": 719,
      "y": 290
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-37" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "ACROYOGA L-BASING",
      "x": 367,
      "y": 55
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-39" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "entry / exit",
      "x": 1510,
      "y": 820
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-40" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "pose",
      "x": 1510,
      "y": 913
    },
    {
      "id": "YD3dz-Rjah6Hvqrfjd0_-41" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "washing machine",
      "x": 1510,
      "y": 1080
    },
    {
      "id": "Jq25LovILjKADiAHG79u-3" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "bed / couch",
      "x": 396,
      "y": 950
    },
    {
      "id": "Jq25LovILjKADiAHG79u-8" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse foot to hand",
      "x": 265,
      "y": 950
    },
    {
      "id": "Jq25LovILjKADiAHG79u-10" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse star",
      "x": 659,
      "y": 950
    },
    {
      "id": "Jq25LovILjKADiAHG79u-11" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "bird on hand",
      "x": 940,
      "y": 950
    },
    {
      "id": "Jq25LovILjKADiAHG79u-17" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse shoulderstand",
      "x": 839,
      "y": 850
    },
    {
      "id": "Jq25LovILjKADiAHG79u-19" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "thinker",
      "x": 700,
      "y": 850
    },
    {
      "id": "Jq25LovILjKADiAHG79u-28" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "around the world",
      "x": 721,
      "y": 720
    },
    {
      "id": "Jq25LovILjKADiAHG79u-36" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "biceps stand",
      "x": 552,
      "y": 260
    },
    {
      "id": "Jq25LovILjKADiAHG79u-37" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "crocodile",
      "x": 552,
      "y": 170
    },
    {
      "id": "Jq25LovILjKADiAHG79u-38" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "foot to hand",
      "x": 720,
      "y": 170
    },
    {
      "id": "Jq25LovILjKADiAHG79u-45" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "bow",
      "x": 390,
      "y": 640
    },
    {
      "id": "Jq25LovILjKADiAHG79u-49" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "foot to hand",
      "x": 1020,
      "y": 680
    },
    {
      "id": "Jq25LovILjKADiAHG79u-50" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse bird",
      "x": 1160,
      "y": 680
    },
    {
      "id": "Jq25LovILjKADiAHG79u-60" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "handstand in/out (legs side)",
      "x": 340,
      "y": 840
    },
    {
      "id": "Jq25LovILjKADiAHG79u-61" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "trapdoor",
      "x": 1252,
      "y": 770
    },
    {
      "id": "Jq25LovILjKADiAHG79u-64" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse foot to shin",
      "x": 527,
      "y": 1090
    },
    {
      "id": "Jq25LovILjKADiAHG79u-66" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "tuck sit",
      "x": 264,
      "y": 1090
    },
    {
      "id": "Jq25LovILjKADiAHG79u-67" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "revese shin to foot",
      "x": 396,
      "y": 1090
    },
    {
      "id": "Jq25LovILjKADiAHG79u-68" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse star",
      "x": 345,
      "y": 260
    },
    {
      "id": "Jq25LovILjKADiAHG79u-69" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "reverse back plank",
      "x": 530,
      "y": 950
    },
    {
      "id": "Jq25LovILjKADiAHG79u-72" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "(reverse) foot to foot ",
      "x": 659,
      "y": 1090
    },
    {
      "id": "Jq25LovILjKADiAHG79u-73" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "(baby) (reverse)&nbsp; hand to hand ",
      "x": 791,
      "y": 1090
    },
    {
      "id": "Jq25LovILjKADiAHG79u-82" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": " waterfall to chair&nbsp;  or  rev. feet to hand ",
      "x": 200,
      "y": 260
    },
    {
      "id": "Jq25LovILjKADiAHG79u-85" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "Rene Smit @rcsmit  CC BY-NC 4.0 ",
      "x": 41,
      "y": 1105
    },
    {
      "id": "Jq25LovILjKADiAHG79u-87" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "koala queen",
      "x": 1060,
      "y": 190
    },
    {
      "id": "Jq25LovILjKADiAHG79u-88" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "spider roll",
      "x": 1040,
      "y": 290
    },
    {
      "id": "Jq25LovILjKADiAHG79u-93" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "START",
      "x": 56,
      "y": 430
    },
    {
      "id": "Jq25LovILjKADiAHG79u-96" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "transition",
      "x": 1510,
      "y": 997
    },
    {
      "id": "Jq25LovILjKADiAHG79u-97" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "Extra poses:",
      "x": 204,
      "y": 1105
    },
    {
      "id": "Jq25LovILjKADiAHG79u-99" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "crunch roll",
      "x": 1111,
      "y": 770
    },
    {
      "id": "Jq25LovILjKADiAHG79u-106" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "rotisserie",
      "x": 1356,
      "y": 380
    },
    {
      "id": "Jq25LovILjKADiAHG79u-110" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "bird on hands",
      "x": 210,
      "y": 460
    },
    {
      "id": "YTtxy9uaqBtlqGOd_hWO-2" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "ballerina",
      "x": 180,
      "y": 611
    },
    {
      "id": "YTtxy9uaqBtlqGOd_hWO-5" ,
      "info":"loremp ipsum",
      "video":"jbtQWzQ3v7g",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "big le moi",
      "x": 174,
      "y": 691
    },
    {
      "id": "Jq25LovILjKADiAHG79u-117" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "mermaid",
      "x": 791,
      "y": 950
    },
    {
      "id": "Jq25LovILjKADiAHG79u-119" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "high barrel roll",
      "x": 1201,
      "y": 190
    },
    {
      "id": "YTtxy9uaqBtlqGOd_hWO-8" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "jump in",
      "x": 345,
      "y": 160
    },
    {
      "id": "Jq25LovILjKADiAHG79u-121" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "barrel roll",
      "x": 1348,
      "y": 570
    },
    {
      "id": "Jq25LovILjKADiAHG79u-123" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "buddha roll",
      "x": 1040,
      "y": 610
    },
    {
      "id": "PljVGr8iR2YL2gw-_0Ea-3" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "table top",
      "x": 952,
      "y": 561
    },
    {
      "id": "YTtxy9uaqBtlqGOd_hWO-1" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "prasarita twist",
      "x": 810,
      "y": 549
    },
    {
      "id": "PljVGr8iR2YL2gw-_0Ea-6" ,
      "info":"loremp ipsum",
      "video":"dQw4w9WgXcQ",
      "photo":"C:\\Users\\rcxsm\\Downloads\\unnamed.jpg",
      "label": "<b>Latest version / PDF / high quality file</b>&nbsp; https://rene-smit.com/acroyoga-flowchart/ ",
      "x": 1175,
      "y": 1119
    }
], 
edges : [
  {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "YD3dz-Rjah6Hvqrfjd0_-33"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-31",
      "target": "Jq25LovILjKADiAHG79u-69"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-1",
      "target": "ylEB-xLuXJku9rSygnK5-2"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "ylEB-xLuXJku9rSygnK5-5"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "ylEB-xLuXJku9rSygnK5-7"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "ylEB-xLuXJku9rSygnK5-33"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "ylEB-xLuXJku9rSygnK5-33"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "ylEB-xLuXJku9rSygnK5-33"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "ylEB-xLuXJku9rSygnK5-33"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-1",
      "target": "ylEB-xLuXJku9rSygnK5-40"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "YD3dz-Rjah6Hvqrfjd0_-17"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-2",
      "target": "Jq25LovILjKADiAHG79u-110"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-7",
      "target": "ylEB-xLuXJku9rSygnK5-8"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-7",
      "target": "ylEB-xLuXJku9rSygnK5-17"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-7",
      "target": "ylEB-xLuXJku9rSygnK5-17"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-7",
      "target": "Jq25LovILjKADiAHG79u-28"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-8",
      "target": "ylEB-xLuXJku9rSygnK5-9"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-8",
      "target": "ylEB-xLuXJku9rSygnK5-31"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-9",
      "target": "ylEB-xLuXJku9rSygnK5-24"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-21",
      "target": "YD3dz-Rjah6Hvqrfjd0_-30"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-21",
      "target": "Jq25LovILjKADiAHG79u-17"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-21",
      "target": "Jq25LovILjKADiAHG79u-19"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-21",
      "target": "Jq25LovILjKADiAHG79u-49"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-21",
      "target": "Jq25LovILjKADiAHG79u-123"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-24",
      "target": "ylEB-xLuXJku9rSygnK5-26"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-24",
      "target": "ylEB-xLuXJku9rSygnK5-26"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-24",
      "target": "ylEB-xLuXJku9rSygnK5-29"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-31",
      "target": "Jq25LovILjKADiAHG79u-3"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-31",
      "target": "Jq25LovILjKADiAHG79u-8"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-31",
      "target": "Jq25LovILjKADiAHG79u-10"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-33",
      "target": "ylEB-xLuXJku9rSygnK5-35"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-35",
      "target": "YD3dz-Rjah6Hvqrfjd0_-23"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-35",
      "target": "Jq25LovILjKADiAHG79u-36"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-44",
      "target": "ylEB-xLuXJku9rSygnK5-42"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-42",
      "target": "ylEB-xLuXJku9rSygnK5-46"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-42",
      "target": "ylEB-xLuXJku9rSygnK5-51"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-123",
      "target": "ylEB-xLuXJku9rSygnK5-42"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-63",
      "target": "ylEB-xLuXJku9rSygnK5-42"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-42",
      "target": "Jq25LovILjKADiAHG79u-121"
    },
    {
      "source": "YD3dz-Rjah6Hvqrfjd0_-15",
      "target": "ylEB-xLuXJku9rSygnK5-44"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-44",
      "target": "Jq25LovILjKADiAHG79u-106"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-46",
      "target": "ylEB-xLuXJku9rSygnK5-48"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-48",
      "target": "ylEB-xLuXJku9rSygnK5-44"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-55",
      "target": "ylEB-xLuXJku9rSygnK5-57"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-55",
      "target": "ylEB-xLuXJku9rSygnK5-59"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-55",
      "target": "YD3dz-Rjah6Hvqrfjd0_-5"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-63",
      "target": "YD3dz-Rjah6Hvqrfjd0_-8"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-63",
      "target": "Jq25LovILjKADiAHG79u-87"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-63",
      "target": "Jq25LovILjKADiAHG79u-88"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-63",
      "target": "Jq25LovILjKADiAHG79u-119"
    },
    {
      "source": "YD3dz-Rjah6Hvqrfjd0_-5",
      "target": "ylEB-xLuXJku9rSygnK5-55"
    },
    {
      "source": "YD3dz-Rjah6Hvqrfjd0_-17",
      "target": "ylEB-xLuXJku9rSygnK5-42"
    },
    {
      "source": "YD3dz-Rjah6Hvqrfjd0_-23",
      "target": "ylEB-xLuXJku9rSygnK5-42"
    },
    {
      "source": "YD3dz-Rjah6Hvqrfjd0_-33",
      "target": "ylEB-xLuXJku9rSygnK5-63"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-17",
      "target": "Jq25LovILjKADiAHG79u-50"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-28",
      "target": "ylEB-xLuXJku9rSygnK5-21"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-36",
      "target": "Jq25LovILjKADiAHG79u-37"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-37",
      "target": "Jq25LovILjKADiAHG79u-38"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-38",
      "target": "ylEB-xLuXJku9rSygnK5-63"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-60",
      "target": "ylEB-xLuXJku9rSygnK5-31"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-49",
      "target": "Jq25LovILjKADiAHG79u-50"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-50",
      "target": "Jq25LovILjKADiAHG79u-61"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-61",
      "target": "ylEB-xLuXJku9rSygnK5-55"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-68",
      "target": "ylEB-xLuXJku9rSygnK5-33"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-68",
      "target": "Jq25LovILjKADiAHG79u-36"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-68",
      "target": "Jq25LovILjKADiAHG79u-82"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-93",
      "target": "ylEB-xLuXJku9rSygnK5-1"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-50",
      "target": "Jq25LovILjKADiAHG79u-99"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-42",
      "target": "Jq25LovILjKADiAHG79u-49"
    },
    {
      "source": "Jq25LovILjKADiAHG79u-117",
      "target": "Jq25LovILjKADiAHG79u-11"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-40",
      "target": "YTtxy9uaqBtlqGOd_hWO-5"
    },
    {
      "source": "YTtxy9uaqBtlqGOd_hWO-8",
      "target": "Jq25LovILjKADiAHG79u-68"
    },
    {
      "source": "ylEB-xLuXJku9rSygnK5-21",
      "target": "ylEB-xLuXJku9rSygnK5-63"
    }]
};


import requests
from keys import api_key_youtube

def find_first_youtube_video(search):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": search,
        "type": "video",
        "maxResults": 1,
        "key": api_key_youtube
    }
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")
    data = response.json()
    if not data["items"]:
        raise KeyError(f"No video found for: {search}")
    return data["items"][0]["id"]["videoId"]


for node in data["nodes"]:
    label = node.get("label", "").strip()
    if label and not label.lower().startswith("<b>") and "rene-smit.com" not in label:
        try:
            clean_label = label.replace("<br>", " ").replace("&nbsp;", " ").split("@")[0]
            video_id = find_first_youtube_video(clean_label)
            node["video"] = video_id
            print(f"{clean_label} → {video_id}")
        except Exception as e:
            print(f"Failed for {label}: {e}")

# Optionally, write updated data to file
import json
with open("updated_data.json", "w") as f:
    json.dump(data, f, indent=2)

