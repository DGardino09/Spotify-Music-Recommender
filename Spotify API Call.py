# All necessary imports
from flask import Flask, url_for, session, redirect, request
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import time

# Creating flask app, key, and cookie
app = Flask(__name__)
app.secret_key = "rkjalnfncion"
app.config['SESSION_COOKIE_NAME'] = "Cookie"
TOKEN_KEY = "token_info"

# Client ID and Cliet Sceret for the Project so it is linked to my Spotify Account
clientID = "ClientID"
clientSecret = "ClientSecret"

# Putting Client ID and Secret into one variable
clientCredentials = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)

# Creating the OAuth to pass through Spotify API's security
def createSpotifyOAuth():
    return SpotifyOAuth(client_id=clientID, client_secret=clientSecret,
                        redirect_uri=url_for('redirectPage', _external=True), scope="user-top-read user-read-recently-played playlist-modify-public playlist-read-private")

# Creating Access Token and getting refresh token if token expires
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

# Login page that calls the OAuth method and goes to the redirect page
@app.route('/')
def login():
    spotifyAuth = createSpotifyOAuth()
    auth_url = SpotifyOAuth.get_authorize_url(spotifyAuth)
    return redirect(auth_url)

# Redirect page that the app will always be the default page
@app.route('/redirect')
def redirectPage():
    spotifyAuth = createSpotifyOAuth()
    session.clear()
    code = request.args.get("code")
    token_info = spotifyAuth.get_access_token(code)
    session[TOKEN_KEY] = token_info
    return redirect(url_for('homePage', _external=True))

# Logout for the user
@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect(url_for('login', _external=False))

# Gets all recently played songs of the current user
@app.route('/getRecentlyPlayed')
def getRecentlyPlayed():
    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    # Pulls users recently played songs and iterates through to get the 50 most recently listened to songs
    results = []
    while True:
        currentUserRecentlyPlayed = sp.current_user_recently_played(limit=50, before=None, after=None)["items"]
        for idx, item in enumerate(currentUserRecentlyPlayed):
            track = item["track"]
            trackValue = track["name"] + " : " + track["artists"][0]["name"]
            results.append(trackValue)
        if (idx < 50):
            break
    return results

# Pulls users Most listened to artists
@app.route('/getUserTopArtists')
def getUserTopArtists():
    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    # Creating lists for what will be returned and setting the limit for how many artists will be pulled
    results = []
    artistIDList = []
    limit = 20
    # Iterates through pulling top 20 artists and gets their names and uri
    while True:
        # time range can be short_range, medium_range, or long_range
        # short_range: last 4 weeks
        # medium_range: last 6 monthes
        # long_range: last few years
        topArtists = sp.current_user_top_artists(limit=limit, offset=0, time_range="medium_term")["items"]
        for idx, item in enumerate(topArtists):
            artist = item["name"]
            artistID = item["uri"]
            artistTopTracks = getArtistTopTracks(artistID)
            results.append(artist)
            artistIDList.append(artistID)
        if (idx < 50):
            break
    return results, artistTopTracks, artistIDList

# Pulling users most listened to tracks
@app.route('/getUserTopTracks')
def getUserTopTracks():
    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    count = 0
    # Iterates through pulling top 50 tracks and gets the names of the song and artist(s) who sing it and uri for the track
    while True:
        offset = count * 50
        count = count + 1
        # time range can be short_range, medium_range, or long_range
        # short_range: last 4 weeks
        # medium_range: last 6 monthes
        # long_range: last few years
        topTracks = sp.current_user_top_tracks(limit=50, offset=offset, time_range="medium_term")["items"]
        for idx, item in enumerate(topTracks):
            track = item["uri"]
            artist = item["album"]
            trackValue = track + " : " + artist["artists"][0]["name"]
            results.append(track)
        if (len(topTracks) < 50):
            break
    return results

# Pulls all related artist for any artist URI that is passed through as a parameter
def getRelatedArtists(artistID):
    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    # Iterating through to pull all related artists for the artist URI that was passed through and puts each
    # related artist URI in a list to be returned
    while True:
        relatedArtists = sp.artist_related_artists(artist_id=artistID)["artists"]
        for idx, item in enumerate(relatedArtists):
            artist = item["name"]
            relatedArtistID = item["uri"]
            results.append(relatedArtistID)
        if (idx < 50):
            break
    return results

# Getting an Artists' top tracks based on the Artist URI that was passed through as a parameter
@app.route("/getArtistTopTracks")
def getArtistTopTracks(artistID):
    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    # Iterates through pulling the top 10 tracks for an artist and gets the names of the song and the URI for the track
    while True:
        artistsTopTracks = sp.artist_top_tracks(artist_id=artistID)["tracks"]
        for idx, item in enumerate(artistsTopTracks):
            track = item["uri"]
            artist = item["artists"][0]["name"]
            trackValue = track + " : " + artist
            results.append(track)
        if (idx < 50):
            break
    return results

# Creating a playlist based on the Playlist name that was prompted to be entered by the program
def createPlaylist(name):
    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    # Creating playlist for specified user with the playlist name given by the user and a short description.
    playlist = sp.user_playlist_create(user="dgardino-us", name=name, description="This is a playlist generated by my Spotify recommendation algorithm.")
    return playlist

# Modifies Playlist based on the Playlist URI
def modifyPlaylist(name, playlist):
    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    # Adding tracks to the Playlist with the URI that was passed through as a parameter
    sp.playlist_add_items(playlist_id=name, items=playlist)
    return "playlist done being modified."

# Gets Playlist info
@app.route("/playlistInfo")
def playlistInfo():
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    #Pulling first playlists' URI
    playlist = sp.current_user_playlists()["items"][0]["id"]
    return playlist

# Method that returns a random integer
def randomizer(listLength):
    low = 0
    high = listLength - 1
    randomPos = random.randint(a=low, b=high)
    return randomPos

# Gets the current user
def getUser():
    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    user = sp.current_user()
    return user

@app.route('/home')
def homePage():
    # Prompts user for the name of their playlist
    playlistName = input("What do you want to name this playlist? ")
    # Creates Playlist with the given playlist name
    createPlaylist(playlistName)

    #All needed variables for the driver function
    recommendedPlaylist = []
    unsortedPlaylist = []
    topTracks = getUserTopTracks()
    userTopArtists = getUserTopArtists()
    artistIDList = userTopArtists[2]
    topArtistsTopTracks = userTopArtists[2]
    relatedArtistLimit = 50
    topTracksLimit = 20
    topArtistsLimit = 30

    # Makes sure that the access token is valid, if not it redirects to the login page
    session['token_info'], authorized = getToken()
    session.modified = True
    if not authorized:
        return url_for('login', _external=False)
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    # Iterating through all top artists and getting all related artists
    for i in range(len(artistIDList)):
        artistID = artistIDList[i]
        relatedArtists = getRelatedArtists(artistID)
        # Randomly pulling two related artist for all 20 top artists
        for i in range(2):
            randInt = randomizer(len(relatedArtists))
            relatedArtistID = relatedArtists[randInt]
            # Getting each related artists top 10 tracks
            relatedArtistsTopTracks = getArtistTopTracks(relatedArtistID)
            relatedArtistsTopTracksLength = len(relatedArtistsTopTracks)
            # Iterating through the related artists top tracks and putting each song into an unsorted playlist
            for i in range(relatedArtistsTopTracksLength):
                temp = relatedArtistsTopTracks.pop()
                unsortedPlaylist.append(temp)
    # Iterating through getting 50 random songs based off of all songs for the randomly selected related artist
    # that were pulled and putting them into the final playlist
    for i in range(relatedArtistLimit):
        randInt = randomizer(len(unsortedPlaylist))
        track = unsortedPlaylist[randInt]
        recommendedPlaylist.append(track)
    # Clearing unsorted playlist
    unsortedPlaylist.clear()
    # Putting users top tracks in the unsorted playlist
    for i in range(len(topTracks)):
        temp = topTracks.pop()
        unsortedPlaylist.append(temp)
    # Randomly putting 20 of the users top tracks in the final playlist
    for i in range(topTracksLimit):
        randInt = randomizer(len(unsortedPlaylist))
        track = unsortedPlaylist[randInt]
        recommendedPlaylist.append(track)
    # Clearing unsorted playlist
    unsortedPlaylist.clear()
    # Putting all of the top tracks for the users top artists in the unsorted playlist
    for i in range(len(topArtistsTopTracks)):
        temp = topArtistsTopTracks.pop()
        tempTopTracks = getArtistTopTracks(temp)
        for i in range(len(tempTopTracks)):
            track = tempTopTracks.pop()
            unsortedPlaylist.append(track)
    # Randomly putting 30 of the top tracks for the top artists into the final playlist
    for i in range(topArtistsLimit):
        randInt = randomizer(len(unsortedPlaylist))
        track = unsortedPlaylist[randInt]
        recommendedPlaylist.append(track)
    # Clearing unsorted playlist
    unsortedPlaylist.clear()
    # Getting Playlist URI for Recommended Playlist
    playlistID = playlistInfo()
    # Adding Recommended Playlist to the playlist created
    modifyPlaylist(playlistID, recommendedPlaylist)
    # Returning this string when it is done compiling playlist
    return "Recommended Playlist has been created!"

# Runs the flask app
if __name__ == '__main__':
	app.run(debug=True)