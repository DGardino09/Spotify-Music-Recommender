import requests

class Spotify_API_Call():
    response = requests.get("https://api.spotify.com")
    print(response.status_code)

if __name__ == "__main__":
    SpotifyAPI = Spotify_API_Call();