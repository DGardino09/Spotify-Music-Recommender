from flask import Flask, url_for, session, redirect, request
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import time

#TODO: Create a playlist
#TODO: Add songs to a playlist
#TODO: Figure out how to pull similar artists based on the users most listened to songs and artists
#TODO: Use JavaScript to make webpage look nice

app = Flask(__name__)
app.secret_key = "rkjalnfncion"
app.config['SESSION_COOKIE_NAME'] = "Drew Cookie"
TOKEN_KEY = "token_info"

clientID = "ClientID"
clientSecret = "ClientSecret"

clientCredentials = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)

def createSpotifyOAuth():
    return SpotifyOAuth(client_id=clientID, client_secret=clientSecret,
                        redirect_uri=url_for('redirectPage', _external=True), scope="user-read-recently-played")


def getToken():
    validToken = False
    tokenInfo = session.get("token_info", {})

    if not (session.get("token_info", False)):
        validToken = False
        return tokenInfo, validToken

    currentTime = int(time.time())
    tokenExpired = session.get("token_info").get("expires_at") - currentTime < 60

    if (tokenExpired):
        spOAuth = createSpotifyOAuth()
        tokenInfo = spOAuth.refresh_access_token(session.get("token_info").get("refresh_token"))

    validToken = True
    return tokenInfo, validToken


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
    return redirect(url_for('getRecentlyPlayed', _external=True))

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect(url_for('login', _external=False))

@app.route('/getRecentlyPlayed')
def getRecentlyPlayed():
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    while True:
        currentUserRecentlyPlayed = sp.current_user_recently_played(limit=50, before=None, after=None)["items"]
        for idx, item in enumerate(currentUserRecentlyPlayed):
            track = item["track"]
            trackValue = track["name"] + " : " + track["artists"][0]["name"]
            results.append(trackValue)
        if (idx < 50):
            break
    dataframe = pd.DataFrame(results, columns=['Track Names'])
    dataframe.to_csv('recentlyPlayed.csv', index=True)
    return "done"

def getUserTopArtists():
    return "some artists"

def getUserTopTracks():
    return "some songs"

def getRelatedArtists():
    return "some related artists"

def getArtistTopTracks():
    return "some songs"

def createPlaylist():
    return "blank playlist"

def modifyPlaylist():
    return "recommended playlist"


if __name__ == '__main__':
	app.run(debug=True)