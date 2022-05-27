from unittest import skip
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
import pandas as pd
from .models import Song



# # Loading dataset (of songs) into database

# import os
# import numpy as np
# import pandas as pd

# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# from collections import defaultdict

# client_id="c9e6a054b87e4506baa93ff43bbbc04e"
# client_secret="323710b395234205b4811e5e2b8cad36"

# # sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ["SPOTIFY_CLIENT_ID"],
# #                                                            client_secret=os.environ["SPOTIFY_CLIENT_SECRET"]))

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
#                                                            client_secret=client_secret))

# df = pd.read_csv(r"C:\Users\HP\Documents\Project\Web Development Project\RecommenderSystem\Algorithm\Music\data.csv")
# print(df)

# # 22307, 40293, 64824
# for i in range(64824, len(df)):
#     try:
#         name = df['name'][i]
#         artists = df['artists'][i][2:-2]
#         artists = artists.split("', '")
#         year = int(df['release_date'][i][:4])
#         popularity = int(df['popularity'][i])
#         song = sp.search(q='track: {} year: {} artist: {}'.format(name, year, artists[0]))
#         preview_url = song['tracks']['items'][0]['preview_url']
#         cover_art = song['tracks']['items'][0]['album']['images'][0]['url']
        
#         if Song.objects.filter(name=name, year=year, artist=artists[0]).first() == None:
#             song_obj = Song.objects.create(
#                 name=name, artist=artists[0], year=year, popularity=popularity,
#                 preview_url=preview_url, cover_art_url=cover_art
#             )

#             song_obj.save()
#             print(i)
#     except Exception as e:
#         print(i, e)
#         continue
    

import os
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist

import warnings
warnings.filterwarnings("ignore")

# from yellowbrick.target import FeatureCorrelation

feature_names = ['acousticness', 'danceability', 'energy', 'instrumentalness',
       'liveness', 'loudness', 'speechiness', 'tempo', 'valence','duration_ms','explicit','key','mode','year']

data = pd.read_csv("Music/data.csv")
genre_data = pd.read_csv('Music/data_by_genres.csv')
year_data = pd.read_csv('Music/data_by_year.csv')

X, y = data[feature_names], data['popularity']


# Clustering Genres with K-Means
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

cluster_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans(n_clusters=10))])

X = genre_data.select_dtypes(np.number)
cluster_pipeline.fit(X)
genre_data['cluster'] = cluster_pipeline.predict(X)


# Clustering Songs with K-Means
song_cluster_pipeline = Pipeline([('scaler', StandardScaler()), 
                                ('kmeans', KMeans(n_clusters=20, 
                                verbose=False))
                                ], verbose=False)

X = data.select_dtypes(np.number)
number_cols = list(X.columns)
song_cluster_pipeline.fit(X)
song_cluster_labels = song_cluster_pipeline.predict(X)
data['cluster_label'] = song_cluster_labels


# Building Recommendation System
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict

# Spotify Client ID, Client Secret
client_id="e9835d48d431425aa0bb7c16ff64e8bb"
client_secret="de945523c9ed46d5865f206df3e89da0"

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Finding song from spotify based on song name and year
def find_song(name, year):
    song_data = defaultdict()
    results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)

    # If song not found, return None
    if results['tracks']['items'] == []:
        return None

    # get song details from spotify data
    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    song_data['name'] = [name]
    song_data['year'] = [year]
    song_data['explicit'] = [int(results['explicit'])]
    song_data['duration_ms'] = [results['duration_ms']]
    song_data['popularity'] = [results['popularity']]

    # create dictionary of song and its audio features
    for key, value in audio_features.items():
        song_data[key] = value

    return pd.DataFrame(song_data)


from collections import defaultdict
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
import difflib

number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']


# get song details from dataset
def get_song_data(song, spotify_data):
    
    try:
        song_data = spotify_data[(spotify_data['name'] == song['name']) 
                                & (spotify_data['year'] == song['year'])].iloc[0]
        return song_data
    
    except IndexError:
        return find_song(song['name'], song['year'])


# calculate mean vector for the given song
def get_mean_vector(song_list, spotify_data):
    
    song_vectors = []
    
    for song in song_list:

        # get song details
        song_data = get_song_data(song, spotify_data)
        if song_data is None:
            print('Warning: {} does not exist in Spotify or in database'.format(song['name']))
            continue

        # store song features
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)  
      
    # converting list of song features to numpy ndarray
    song_matrix = np.array(list(song_vectors))

    # calculates mean of the given data along the columns(song features)
    return np.mean(song_matrix, axis=0)


# converting song name, artist name, year to default dictionary
def flatten_dict_list(dict_list):
    
    # creating empty dictionary with keys as artists, name, year
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []

    # assigning values to keys - artists, name, year
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
    return flattened_dict

# return recommendations for the provided song
def recommend_songs( song_list, spotify_data, n_songs=10):
    
    metadata_cols = ['name', 'year', 'artists']
    song_dict = flatten_dict_list(song_list)

    # get average of features of song
    song_center = get_mean_vector(song_list, spotify_data)

    # Standard Scaler
    scaler = song_cluster_pipeline.steps[0][1]

    # normalize features of songs i.e. each column individually
    scaled_data = scaler.transform(spotify_data[number_cols])

    # normalize features of the provided song
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))

    # compute cosine distance between the song arrays
    distances = cdist(scaled_song_center, scaled_data, 'cosine')

    # get indices of recommendations
    index = list(np.argsort(distances)[:, :n_songs][0])

    # find details of recommendations
    rec_songs = spotify_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]

    # converting pandas dataframe to list and returning result
    return rec_songs[metadata_cols].to_dict(orient='records')


# Get details of given song from the given artist
def get_song(song, artist):
    
    result = {}

    try:

        # search for the given song and artist
        details = sp.search(q='track:{} artist:{}'.format(song, artist), limit=1)

        # store the result as a dictionary
        result['artist'] = artist 
        result['song_name'] = song

        # Replace \ and / for the url
        # set song name(modified) + artist name(modified) as the custom song_id
        # set artist name(modified) and sotify artist id as custom artist_id
        song = song.replace('/', '**')
        artist = artist.replace('/', '~~')
        artist = artist.replace('\\', '@@')
        result['id'] = song + '#' + artist
        result['artist_id'] = artist + '#' + details['tracks']['items'][0]['artists'][0]['id']

        # store other details about the provided song:

        # 1. preview url: a 29 sec preview of the audio if available
        result['preview_url'] = details['tracks']['items'][0]['preview_url']

        # 2. cover_art: cover photo for the song
        result['cover_art'] = details['tracks']['items'][0]['album']['images'][0]['url']

        # 3. year: year of release of song
        result['year'] = int(details['tracks']['items'][0]['album']['release_date'][:4])

        # 4. album: album the song belongs to
        result['album'] = details['tracks']['items'][0]['album']['name']

        # 5. album_type = type of album (single or album)
        result['album_type'] = details['tracks']['items'][0]['album']['album_type']

        # 6. album_id: spotify album id
        result['album_id'] = details['tracks']['items'][0]['album']['id']
    
    except Exception as e:
        # in case of any exception return empty dictionary
        print(e)
        return {}

    return result


# Get details of the given album of the given artist
def get_album(album, artist):

    result = {}

    try:

        # search for the given album using album name and artist
        details = sp.search(q='album: {} artist:{}'.format(album, artist))

        # store details of album in dictionary 'result'
        result['album_name'] = album 
        result['album_image'] = details['tracks']['items'][0]['album']['images'][0]['url']
        result['album_type'] = details['tracks']['items'][0]['album']['type']

        # store the songs in the album
        result['songs'] = []
        for song in details['tracks']['items']:
            song = get_song(song = song['name'], artist = artist)
            if len(song) != 0:
                result['songs'].append(song)

    except Exception as e:
        # return empty dictionary in case of any exception
        print(e)
        return {}

    return result 


# Get details of the given artist
def get_artist(artist):

    result = {}

    try:

        # search for the given artist using artist name
        details = sp.search(q='artist:{}'.format(artist), type='artist', limit=1)

        # store the details of the artist in dictionary result
        result['artist_name'] = artist
        result['image'] = details['artists']['items'][0]['images'][0]['url']

        # replace / or \ for the artist id to be used as a part of the url
        artist = artist.replace('/', '~~')
        artist = artist.replace('\\', '@@')

        # make artist id as modified artist name + spotify artist id
        result['id'] = artist + '#' + details['artists']['items'][0]['id']

        return result

    except Exception as e:
        print(e)
        return {}


# Get top songs of the given artist
def artist_top_songs(artist):

    result = []

    try:

        # search for the given artist using artist name
        details = sp.search(q='artist:{}'.format(artist), limit=1)

        # get artist spotify uri
        artist_uri = details['tracks']['items'][0]['album']['artists'][0]['uri']

        # get top tracks of artist from spotify using artist uri
        top_tracks = sp.artist_top_tracks(artist_uri)

        # store the details of the top songs of the artist
        for song in top_tracks['tracks'][:10]:

            # store songs only if image(cover_art) available
            if(song['album']['images'][0]['url'] != None):
                song_dict = {}
                song_dict = get_song(song = song['name'], artist=artist)
                if len(song_dict) != 0:
                    result.append(song_dict)

    except Exception as e:
        # return empty list in case of any exception
        print(e) 
        return []

    return result


# a dictionary for storing the songs and artists in the explore page
default_explore = {}


# Return the explore.html page
def explore(request, message = ""):

    global default_explore 

    # if explore already called once then return the result searched before
    # instead of searching the same result again
    if len(default_explore) != 0:
        if message == "":
            default_explore["message"] = ""
        return render(request, 'Music/explore.html', default_explore)

    # list of default songs for the 'explore' page
    default_songs = [
        {'name': 'Faded', 'artist': 'Alan Walker'},
        {'name': 'Happy Now', 'artist': 'Kygo'},
        {'name': 'Nightlight', 'artist': 'Illenium'},
        {'name': 'Perfect', 'artist': 'Ed Sheeran'},
        {'name': 'There For You', 'artist': 'Martin Garrix'},
        {'name': 'If the World Was Ending (feat. Julia Michaels)', 'artist': 'JP Saxe'},
        {'name': 'Let Me Down Slowly', 'artist': 'Alec Benjamin'},
        {'name': 'Stargazing', 'artist': 'Kygo'},
        {'name': 'OK', 'artist': 'Alan Walker'},
        {'name': 'Freedom', 'artist': 'Kygo'},
    ]

    # list of default artists for the 'explore' page
    default_artists = [
        'Alan Walker', 'Illenium', 'Kygo', 'Martin Garrix', 'Zedd', 
        'Taylor Swift', 'Imagine Dragons', 'Ed Sheeran', 'Alec Benjamin'
    ]

    # for storing the temporary result of song details
    temp_result = []

    # for storing the final result
    result = {}

    # get details of each song in default_songs
    for song in default_songs:
        song_details = get_song(song['name'], song['artist'])
        if len(song_details) != 0:
            temp_result.append(song_details)

    # store the result as default_songs in the final result
    result['default_songs'] = temp_result 

    temp_result = []

    # get details of each artist in default_artists
    for artist in default_artists:
        artist_details = get_artist(artist)
        if len(artist_details) != 0:
            temp_result.append(artist_details)

    # store the result as default_artists in the final result
    result['default_artists'] = temp_result 

    # set default_explore with the final result
    default_explore = result 

    # set message in case of any error 
    result['message'] = message

    return render(request, 'Music/explore.html', result) 


# Get artists similar to the given artist
def similar_artists(artist_id):

    try:

        # search for similar artists using artist spotify id 
        details = sp.artist_related_artists(artist_id)

        result = []

        # store the details of similar artists in result
        for artist in details['artists']:
            temp_result = get_artist(artist['name'])
            if len(temp_result) != 0:
                result.append(temp_result)
        
        return result 
    
    except Exception as e:
        # return empty list in case of any exception
        print(e) 
        return []


# Return login.html page
def login_view(request):
    return render(request, 'Music/login.html')


# Return register.html page
def register(request):
    return render(request, 'Music/register.html')


# Logout the user and returns index.html page
def logout_view(request):
    logout(request)
    return redirect('index')


# Return index.html page
def index(request):
    return render(request, 'Music/index.html')


# return all songs for the playlist.html
def get_playlist_songs(request):

    # get all the 'favourites' songs of the current user
    fav_songs = Song.objects.filter(user = request.user)

    # for storing the user's favourite songs
    my_songs = []

    # for storing the recommended songs
    recommend = []

    for song in fav_songs:

        # get details of the favourite song and add to my_songs
        d = get_song(song = song.name, artist = song.artist)
        my_songs.append(d) 

        # get recommendation for the favourite song
        temp = get_recommendation(name = song.name, artist = song.artist, year = song.year,n_songs = 3)

        # if recommendation is valid then add to recommend
        if len(temp) != 0:
            recommend.extend(temp)

    # remove duplicates in the recommend list and storing the final result in result
    song_names = {}
    result = []
    for song in recommend:
        if song['song_name'] not in song_names:
            result.append(song)
            song_names[song['song_name']] = 1
    
    return render(request, 'Music/playlist.html', {
        'my_songs': my_songs,
        'recommended': result
    })


# add songs in the favourites and returns the favourite songs and recommendations for the current user
def playlist(request):

    try:
        
        # if user is not authenticated then does not allow user to access playlist
        if request.user.is_authenticated == False:
            return explore(request, message="Login/Sign Up to create a playlist")

        if request.method == 'POST':
            
            # get custom song_id which was submitted
            song = request.POST['song_name']

            # replace all \ and / back in the custom song_id
            song = song.replace('**', '/')
            song = song.replace('~~', '/')
            song = song.replace('@@', '\\')

            # get song name and artist from song id
            song = song.split('#')
            song_name = song[0]
            artist = song[1]

            print(song, artist)
            # if the submitted song is not in tht database then create an instance of it
            if Song.objects.filter(name=song_name, artist=artist).first() == None:

                # get song details
                song = get_song(song = song_name, artist = artist)

                # if song is valid then store it in the database by creating an instance of Song
                if len(song) != 0:
                    song_obj = Song.objects.create(
                        name = song['song_name'], artist = song['artist'],
                        year = song['year'],
                        preview_url = song['preview_url'], 
                        cover_art_url = song['cover_art']
                    )
                    song_obj.save()

                    # add many-to-many relatonship with the current user and save it
                    song_obj.user.add(request.user)
                    song_obj.save()

            # else if song is already in the database
            else:
                
                # find the provided song object
                song_obj = Song.objects.filter(name = song_name, artist = artist).first()

                # add many-to-many relatonship with the current user and save it
                song_obj.user.add(request.user)

        # return favourites and recommendations songs for the playlist.html
        return get_playlist_songs(request)

    except Exception as e:
        print(e) 

        # return explore page with error message in case of any exception
        return explore(request, message="Some Error Occurred. Please Try Later.")


# Returns songs recommended for the provided song
def get_recommendation(name, artist, year, n_songs=10):

    try:

        # get recommended songs for the provided song
        temp = recommend_songs([{'artists': artist, 'name': name, 'year': int(year)}], data, n_songs = n_songs)

        # if recommendations are valid
        if len(temp) != 0:
            recommended_songs = temp

            recommend = []

            for i in range(len(recommended_songs)):

                # get the artist from the list of artists for the recommended song
                artists = recommended_songs[i]['artists']
                artists = artists[2:-2]
                artists = artists.split("', '")

                # get details of the recommended song
                song = get_song(recommended_songs[i]['name'], artists[0])

                # if details are valid store in final result
                if(len(song) >= 1): recommend.append(song)

            return recommend

    except Exception as e:
        print(e)
    
    return []

# get song details, artist details, album songs, recommended songs and similar artists
def get_all(song, artist):

    try:

        # get details of the provided song
        song = get_song(song = song, artist = artist)
        year = song['year']

        # for storing the final result 
        result = {}
        result['song'] = song

        # get recommendations for the provided song
        temp = get_recommendation(name=song['song_name'], artist=artist, year=year)
        if len(temp) != 0:
            result['recommended_songs'] = temp
        
        # get details of the provided artist
        temp = get_artist(artist)
        if len(temp) != 0:

            # if valid store details of the artist
            result['song_artist'] = temp

            # get artist spotify id
            artist_id = result['song_artist']['id'].split('#')

            # get similar artists for the provided artist
            temp = similar_artists(artist_id[1])
            if len(temp) != 0:
                result['similar_artists'] = temp

            # get top songs of the provided artist
            temp = artist_top_songs(song['artist'])
            if len(temp) != 0:
                result['artist_top_songs'] = temp

        # if album type is not album (i.e. single)
        if song['album_type'] != 'album':
            result['album_songs'] = {}

        else:

            # get album details
            temp = get_album(song['album'], artist)
            if len(temp['songs']) != 0:
                result['album_songs'] = temp

        # remove duplicates from result of recommended songs
        song_names = {}
        recommend = []

        for song in result['recommended_songs']:
            if song['song_name'] not in song_names:
                recommend.append(song)
                song_names[song['song_name']] = 1
        
        result['recommended_songs'] = recommend
        
        return result
    
    except Exception as e:

        # return empty dictionary in case of an exception
        print(e)

        return {}


# Returns search.html page
def search(request):

    try:

        if request.method == 'POST':
            
            # get song and artist name
            song = request.POST['song'][:-1].split(' (Artist: ')

            song_name = song[0]
            artist = song[1]

            # get song details
            song = get_song(song = song_name, artist = artist)
            
            # if song name and artist name are valid
            if len(song) != 0:
                
                # get artist, album, recommendations and similar artists
                result = get_all(song = song_name, artist = artist)

                return render(request, 'Music/recommend.html', result)
            
            else:

                # display error in case of exception
                return explore(request, message="Some Error Occurred. Please Try Later.")
            
        else:
            
            # return all songs for search datalist
            all_songs = Song.objects.all().values()
            songs = []

            for song in all_songs:
                songs.append(song)

            return render(request, 'Music/search.html', {
                'songs': songs
            })
        

    except Exception as e:

        # return error in case of any exception
        print(e) 
    return explore(request, message="Some Error Occurred. Please Try Later.")


# Returns artist.html page
def artist(request, id):

    try:

        # replace modified artist id with original symbols to get original artist name
        id = id.replace('~~', '/')
        id = id.replace('@@', '\\')
        artist = id.split('#')

        artist_name = artist[0]
        artist_id = artist[1]

        # for storing final result
        result = {}

        # get artist details
        temp = get_artist(artist = artist_name) 

        # if artist is valid
        if len(temp) != 0: 

            # store artist details
            result['artist'] = temp 
        
            # get artist top songs
            temp = artist_top_songs(artist=artist_name) 
            if len(temp) != 0:
                result['artist_top_songs'] = temp
            
            # get similar artists for the given artist
            temp = similar_artists(artist_id=artist_id) 
            if len(temp) != 0:
                result['similar_artists'] = temp

        # return final result
        return render(request, 'Music/artist.html', result)  

    except Exception as e:

        # return error in case of any exception
        print(e) 

    return explore(request, message="Some Error Occurred. Please Try Later.")


# Returns recommended.html page with the given song
def song(request, id):

    try:
        # replace original song id with original symbols to get original song 
        id = id.replace('**', '/')
        id = id.replace('~~', '/')
        id = id.replace('@@', '\\')
        id = id.split('#')

        song_name = id[0]
        artist = id[1]

        # get song details
        song = get_song(song = song_name, artist = artist)
        if len(song) != 0:

            # get song, artist, album, recommendations and similar artists
            result = get_all(song = song_name, artist = artist)
            return render(request, 'Music/recommend.html', result)
    
    except Exception as e:
        print(e) 
    return explore(request, message="Some Error Occurred. Please Try Later.")


# Removes a song from the user favourites
def delete(request):
    try:

        # allow deletion only if user is authenticated
        if request.user.is_authenticated == False:
            return explore(request, message="Login/Sign Up to remove from playlist")

        if request.method == 'POST':

            # replace modified song id with original symbols to get original song
            song = request.POST['remove']
            song = song.replace('**', '/')
            song = song.replace('~~', '/')
            song = song.replace('@@', '\\')

            song = song.split('#')

            song_name = song[0]
            artist = song[1]

            # get song object to be removed from user's favourites
            song_obj = Song.objects.filter(name=song_name, artist=artist).first()

            if song_obj != None:
                
                # remove song from user's favourites
                song_obj.user.remove(request.user)

        # return new favourites
        return get_playlist_songs(request)

    except Exception as e:

        # return error in case of exception
        print(e) 
    
        return explore(request, message="Some Error Occurred. Please Try Later.")