from flask import Flask, url_for, session, redirect, request
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = "rkjalnfncion"
app.config['SESSION_COOKIE_NAME'] = "Drew Cookie"
TOKEN_KEY = "token_info"

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

@app.route('/getTopArtists')
def getTopArtists():
    return "Top Artists"

def createSpotifyOAuth():
    return SpotifyOAuth(client_id="CLIENT_ID", client_secret="CLIENT_SECRET",
                        redirect_uri=url_for('redirectPage', _external=True), scope="user-library-read")

#TODO: Create refresh token
#TODO: Create a playlist
#TODO: Add songs to a playlist
#TODO: Figure out how to pull similar artists based on the users most listened to songs and artists
#TODO: Use JavaScript to make webpage look nice


if __name__ == '__main__':
	app.run(debug=True)