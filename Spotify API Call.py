from flask import Flask, url_for, session, redirect, request
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
app.secret_key = "rkjalnfncion"
app.config['SESSION_COOKIE_NAME'] = "Drew Cookie"
TOKEN_KEY = "token_info"
clientID = "ClientID"
clientSecret = "ClientSecret"

clientCredentials = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)

@app.route('/')
def login():
    spotifyAuth = createSpotifyOAuth()
    auth_url = SpotifyOAuth.get_authorize_url(spotifyAuth)
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    spotifyAuth = createSpotifyOAuth()
    session.clear()
    code = request.args.get("code")
    token_info = spotifyAuth.get_access_token(code)
    session[TOKEN_KEY] = token_info
    return redirect(url_for('getTopArtists', _external=True))

@app.route('/getRecentlyPlayed')
def getRecentlyPlayed():
    sp = spotipy.Spotify(client_credentials_manager=clientCredentials)
    currentUserRecentlyPlayed = sp.current_user_recently_played(limit=50, after=None, before=None)
    return currentUserRecentlyPlayed

def createSpotifyOAuth():
    return SpotifyOAuth(client_id=clientID, client_secret=clientSecret,
                        redirect_uri=url_for('redirectPage', _external=True), scope="user-read-recently-played")

#TODO: Create refresh token
#TODO: Create a playlist
#TODO: Add songs to a playlist
#TODO: Figure out how to pull similar artists based on the users most listened to songs and artists
#TODO: Use JavaScript to make webpage look nice


if __name__ == '__main__':
	app.run(debug=True)