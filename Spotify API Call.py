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
                        redirect_uri=url_for('redirectPage', _external=True), scope="user-top-read user-read-recently-played")

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
    return redirect(url_for('getUserTopArtists', _external=True))

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
    return "Recently Played songs compiled"

@app.route('/getUserTopArtists')
def getUserTopArtists():
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    limit = 20
    while True:
        topArtists = sp.current_user_top_artists(limit=20, offset=0, time_range="medium_term")["items"]
        for idx, item in enumerate(topArtists):
            artist = item["name"]
            artistID = item["uri"]
            relatedArtists = getRelatedArtists(artist, artistID)
            getArtistTopTracks(artistID)
            results.append(artist)
        if (idx < 50):
            break
    dataframe = pd.DataFrame(results, columns=["Top " + str(limit) + " Artists"])
    dataframe.to_csv('Top Artists.csv', index=True)
    return "Top Artists Complied"

@app.route('/getUserTopTracks')
def getUserTopTracks():
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    count = 0
    while True:
        offset = count * 50
        count = count + 1
        topTracks = sp.current_user_top_tracks(limit=50, offset=offset, time_range="medium_term")["items"]
        for idx, item in enumerate(topTracks):
            track = item["name"]
            artist = item["album"]
            trackValue = track + " : " + artist["artists"][0]["name"]
            results.append(trackValue)
        if (len(topTracks) < 50):
            break
    dataframe = pd.DataFrame(results, columns=['Track Names'])
    dataframe.to_csv('TopTracks.csv', index=True)
    return "Top Played Songs compiled"


def getRelatedArtists(artistName, artistID):
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    while True:
        relatedArtists = sp.artist_related_artists(artist_id=artistID)["artists"]
        for idx, item in enumerate(relatedArtists):
            artist = item["name"]
            relatedArtistID = item["uri"]
            getArtistTopTracks(relatedArtistID)
            results.append(artist)
        if (idx < 50):
            break
    dataframe = pd.DataFrame(results, columns=["Related Artists"])
    dataframe.to_csv("Artists Related to " + artistName + ".csv", index=True)
    return dataframe

def getArtistTopTracks(artistID):
    return "some songs"

def createPlaylist():
    return "blank playlist"

def modifyPlaylist():
    return "recommended playlist"

if __name__ == '__main__':
	app.run(debug=True)