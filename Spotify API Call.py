import random

from flask import Flask, url_for, session, redirect, request
import json
import pandas as pd
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import time

#TODO: Add songs to a playlist

app = Flask(__name__)
app.secret_key = "rkjalnfncion"
app.config['SESSION_COOKIE_NAME'] = "Cookie"
TOKEN_KEY = "token_info"
clientID = "d3ec161021af4eaf959491dd6757c7e1"
clientSecret = "3a8e0bf588174082bcc2961be2afaba5"
# clientID = "ClientID"
# clientSecret = "ClientSecret"

clientCredentials = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)

def createSpotifyOAuth():
    return SpotifyOAuth(client_id=clientID, client_secret=clientSecret,
                        redirect_uri=url_for('redirectPage', _external=True), scope="user-top-read user-read-recently-played playlist-modify-public playlist-read-private")

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
    return redirect(url_for('homePage', _external=True))

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
    # dataframe = pd.DataFrame(results, columns=['Track Names'])
    # dataframe.to_('recentlyPlayed.csv', index=True)
    return results

@app.route('/getUserTopArtists')
def getUserTopArtists():
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    artistIDList = []
    limit = 20

    # topArtists = sp.current_user_top_artists(limit=limit, offset=0, time_range="medium_term")
    # return topArtists

    while True:
        topArtists = sp.current_user_top_artists(limit=limit, offset=0, time_range="medium_term")["items"]
        for idx, item in enumerate(topArtists):
            artist = item["name"]
            artistID = item["uri"]
            artistTopTracks = getArtistTopTracks(artistID)
            results.append(artist)
            artistIDList.append(artistID)
        if (idx < 50):
            break
    # dataframe = pd.DataFrame(results, columns=["Top " + str(limit) + " Artists"])
    # dataframe.to_csv('Top Artists.csv', index=True)
    return results, artistTopTracks, artistIDList

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
            track = item["uri"]
            artist = item["album"]
            trackValue = track + " : " + artist["artists"][0]["name"]
            results.append(track)
        if (len(topTracks) < 50):
            break
    # dataframe = pd.DataFrame(results, columns=['Track Names'])
    # dataframe.to_csv('TopTracks.csv', index=True)
    return results

def getRelatedArtists(artistID):
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
            #results.append(artist)
            results.append(relatedArtistID)
        if (idx < 50):
            break
    # dataframe = pd.DataFrame(results, columns=["Related Artists"])
    # dataframe.to_csv("Artists Related to " + artistName + ".csv", index=True)
    return results

@app.route("/getArtistTopTracks")
def getArtistTopTracks(artistID):
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []

    # artistTopTracks = sp.artist_top_tracks(artist_id="11gWrKZMBsGQWmobv3oNfW")
    # return artistTopTracks

    while True:
        artistsTopTracks = sp.artist_top_tracks(artist_id=artistID)["tracks"]
        for idx, item in enumerate(artistsTopTracks):
            track = item["uri"]
            artist = item["artists"][0]["name"]
            trackValue = track + " : " + artist
            results.append(track)
        if (idx < 50):
            break
    # dataframe = pd.DataFrame(results, columns=["Related Artists"])
    # dataframe.to_csv("Top Tracks for " + str(artist) + ".csv", index=True)
    return results

def createPlaylist(name):
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    playlist = sp.user_playlist_create(user="dgardino-us", name=name, description="This is a playlist generated by my Spotify recommendation algorithm.")
    return playlist

def modifyPlaylist(name, playlist):
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    sp.playlist_add_items(playlist_id=name, items=playlist)
    return "playlist done being modified."

@app.route("/playlistInfo")
def playlistInfo():
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    playlist = sp.current_user_playlists()["items"][0]["id"]
    return playlist

def randomizer(listLength):
    low = 0
    high = listLength - 1
    randomPos = random.randint(a=low, b=high)
    return randomPos

def getUser():
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    user = sp.current_user()
    return user

@app.route('/home')
def homePage():
    playlistName = input("What do you want to name this playlist? ")
    createPlaylist(playlistName)
    recommendedPlaylist = []
    unsortedPlaylist = []
    topTracks = getUserTopTracks()
    userTopArtists = getUserTopArtists()
    artistIDList = userTopArtists[2]
    topArtistsTopTracks = userTopArtists[2]
    relatedArtistLimit = 50
    topTracksLimit = 20
    topArtistsLimit = 30
    count = 0

    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    for i in range(len(artistIDList)):
        artistID = artistIDList[i]
        relatedArtists = getRelatedArtists(artistID)
        for i in range(2):
            randInt = randomizer(len(relatedArtists))
            relatedArtistID = relatedArtists[randInt]
            relatedArtistsTopTracks = getArtistTopTracks(relatedArtistID)
            relatedArtistsTopTracksLength = len(relatedArtistsTopTracks)
            for i in range(relatedArtistsTopTracksLength):
                temp = relatedArtistsTopTracks.pop()
                unsortedPlaylist.append(temp)
    for i in range(relatedArtistLimit):
        randInt = randomizer(len(unsortedPlaylist))
        track = unsortedPlaylist[randInt]
        recommendedPlaylist.append(track)
    unsortedPlaylist.clear()
    for i in range(len(topTracks)):
        temp = topTracks.pop()
        unsortedPlaylist.append(temp)
    for i in range(topTracksLimit):
        randInt = randomizer(len(unsortedPlaylist))
        track = unsortedPlaylist[randInt]
        recommendedPlaylist.append(track)
    unsortedPlaylist.clear()
    for i in range(len(topArtistsTopTracks)):
        temp = topArtistsTopTracks.pop()
        tempTopTracks = getArtistTopTracks(temp)
        for i in range(len(tempTopTracks)):
            track = tempTopTracks.pop()
            unsortedPlaylist.append(track)
    for i in range(topArtistsLimit):
        randInt = randomizer(len(unsortedPlaylist))
        track = unsortedPlaylist[randInt]
        recommendedPlaylist.append(track)
    unsortedPlaylist.clear()
    playlistID = playlistInfo()
    modifyPlaylist(playlistID, recommendedPlaylist)
    return "Recommended Playlist has been created!"

if __name__ == '__main__':
	app.run(debug=True)