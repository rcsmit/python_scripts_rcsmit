import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubedownloader import download_tracklist
import csv
from keys import *
import tidalapi
import json
import os
import win32clipboard  # part of pywin32

def process_playlist_and_save(tracks, playlist_id, platform, start_idx, end_idx):
    """Process tracks from start_idx to end_idx and save to CSV, return trackstring."""
    playlist_data = []
    trackstring_lines = []

    # Adjust indices to 0-based and ensure they are within bounds
    start_idx = max(1, start_idx) - 1  # Convert to 0-based index
    end_idx = min(len(tracks), end_idx) - 1  # Ensure end_idx doesn't exceed track count

    for idx, track in enumerate(tracks[start_idx:end_idx + 1], start=start_idx + 1):
        if platform == "spotify":
            title = track["track"]["name"]
            artists = ", ".join([artist["name"] for artist in track["track"]["artists"]])
        else:  # tidal
            title = track.name
            artists = ", ".join([artist.name for artist in track.artists])
        
        playlist_data.append([idx, title, artists])
        trackstring_lines.append(f"{idx}. {title} — {artists}")

    trackstring = "\n".join(trackstring_lines)
    output_file = f"{platform}_playlist_{playlist_id}.csv"

    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#", "Title", "Artists"])
        writer.writerows(playlist_data)

    print(f"Exported {len(playlist_data)} tracks to {output_file}")
    print("\n--- Trackstring ---\n")
    print(trackstring)
    return trackstring

def main_spotify(playlist_url, start_idx, end_idx):
    # Authenticate
    auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Extract playlist ID
    playlist_id = playlist_url.split("/")[-1].split("?")[0]

    # Fetch playlist tracks
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]

    # If playlist has more than 100 tracks, fetch more
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    return process_playlist_and_save(tracks, playlist_id, "spotify", start_idx, end_idx)

def main_tidal(playlist_url, start_idx, end_idx):
    # Extract playlist ID
    playlist_id = playlist_url.split("/")[-1].split("?")[0]

    TOKEN_FILE = "tidal_token.json"

    def save_token(session):
        """Save current session tokens to file."""
        data = {
            "token_type": session.token_type,
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }
        tmp_file = TOKEN_FILE + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp_file, TOKEN_FILE)

    def load_session():
        s = tidalapi.Session()
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                s.load_oauth_session(
                    d["token_type"],
                    d["access_token"],
                    d["refresh_token"],
                )
                print("✅ Logged in using saved token")
                return s
        except Exception as e:
            print(f"⚠️ Token load failed: {e}")

        # First time or failed load
        print("🔑 First-time login...")
        s.login_oauth_simple()
        save_token(s)
        print("✅ Logged in and token saved")
        return s

    # Usage
    session = load_session()
    playlist = session.playlist(playlist_id)
    tracks = playlist.tracks()

    return process_playlist_and_save(tracks, playlist_id, "tidal", start_idx, end_idx)

def main():
    win32clipboard.OpenClipboard()
    playlist_url = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    mix_title = playlist_url
    mix_url = playlist_url
    timestamp_regex = r"\d{1,2}\. "  # 1 or 2 digits, followed by a dot and a space

    # Define track range (modify these values as needed)
    start_idx = 1  # Starting track number (1-based)
    end_idx = 21   # Ending track number (1-based)

    if "spotify" in playlist_url:
        print("Fetching Spotify playlist...")
        try:
            trackstring = main_spotify(playlist_url, start_idx, end_idx)
        except:
            print("Error retrieving Spotify playlist")
    elif "tidal" in playlist_url:
        print("Fetching Tidal playlist...")
        try:
            trackstring = main_tidal(playlist_url, start_idx, end_idx)
        except:
            print("Error retrieving Tidal playlist")
    else:
        print(f"Unsupported playlist URL. [{playlist_url}] Please provide a Spotify or Tidal playlist URL.")
        return
    try:
        download_tracklist(trackstring, timestamp_regex, mix_title, mix_url)
    except Exception as e:
        print(f"Error downloading tracklist: {e}")
        return
    
if __name__ == "__main__":
    main()