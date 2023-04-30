import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


dataset = pd.read_csv('Datasets/useful_feature.csv')
complete_feature_set = pd.read_csv('Datasets/complete_feature.csv')


os.environ["SPOTIPY_CLIENT_ID"] = "04787040c97949849646c82ef8b93796"
os.environ["SPOTIPY_CLIENT_SECRET"] = "3400c76e285e4f9d92bcba39de3db775"

scope = 'user-library-read'

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)


def create_playlist_df_that_in_dataset(playlist_id, dataset):
    playlist = pd.DataFrame()

    for ix, i in enumerate(sp.playlist_tracks(playlist_id)['items']):
        playlist.loc[ix, 'artist'] = i['track']['artists'][0]['name']
        playlist.loc[ix, 'name'] = i['track']['name']
        playlist.loc[ix, 'track_id'] = i['track']['id'] # ['uri'].split(':')[2]
        # playlist.loc[ix, 'url'] = i['track']['album']['images'][1]['url']

    # playlist['date_added'] = pd.to_datetime(playlist['date_added'])

    playlist = playlist[playlist['track_id'].isin(dataset['track_id'].values)]

    return playlist


def generate_playlist_feature(complete_feature_set, playlist_in_df):
    #findings songs in playlist with their features
    complete_feature_set_playlist = complete_feature_set[complete_feature_set['track_id'].isin(playlist_in_df['track_id'].values)]
    # find non-playlist songs features
    complete_feature_set_nonplaylist = complete_feature_set[~complete_feature_set['track_id'].isin(playlist_in_df['track_id'].values)]
    complete_feature_set_playlist_final = complete_feature_set_playlist.drop(columns = "track_id")

    return complete_feature_set_playlist_final.sum(axis = 0), complete_feature_set_nonplaylist


def generate_recommendation(dataset, playlist_vector, nonplaylist_features):
    #songs that are in dataset but not in playlist
    non_playlist_df = dataset[dataset['track_id'].isin(nonplaylist_features['track_id'].values)]

    # Find cosine similarity between the playlist and the complete song set
    non_playlist_df['sim'] = cosine_similarity(nonplaylist_features.drop('track_id', axis = 1).values, playlist_vector.values.reshape(1, -1))[:,0]

    return non_playlist_df.sort_values('sim',ascending = False)


def get_top_rec(recommend, top):
    res_df = recommend.head(top).copy()
    res_df = res_df['track_id']
    # res_df['track_name'] = res_df['track_id'].apply(lambda x : sp.track(x)['name'])
    # res_df['artist_name'] = res_df['track_id'].apply(lambda x : sp.track(x)['artists'][0]['name'])
    # res_df['image_url'] = res_df['track_id'].apply(lambda x : sp.track(x)['album']['images'][0]['url'])
    # print(res_df.info())
    return res_df


def get_recommendation(pID):
    playlist_id = pID

    playlist_in_df  = create_playlist_df_that_in_dataset(playlist_id, dataset)

    complete_feature_set_playlist_vector, complete_feature_set_nonplaylist = generate_playlist_feature(complete_feature_set, playlist_in_df)

    recommend = generate_recommendation(dataset,complete_feature_set_playlist_vector, complete_feature_set_nonplaylist)

    res_recommended = get_top_rec(recommend, 6)

    return res_recommended.to_list()


def get_track_name(rec_list):
    track_name_list = []
    
    for x in rec_list:
        
        track_name = sp.track(x)['name']
        if track_name == '':
            track_name = 'null'

        track_name_list.append(track_name)
    print(track_name_list)
    return track_name_list


def get_track_artist(rec_list):
    artist_name_list = []
    for x in rec_list:
        try:    
            artist_list = sp.track(x)['artists']
        except:
            artist_list = []
        artist_names = []
        for idx, x in enumerate(artist_list):
            artist_names.append(artist_list[idx]['name'])

        artist_name_list.append(artist_names)

    return artist_name_list


def get_track_image(rec_list):
    track_image = []
    
    for x in rec_list:
        try:
            url = sp.track(x)['album']['images'][0]['url']
        except:
            url = 'assets/no_img.jpg'
        track_image.append(url)

    return track_image


track_name = []
track_artist = []
track_image = []


def display():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header(track_name[0])
        st.image(track_image[0])
        st.write(track_artist[0][0])

    with col2:
        st.header(track_name[1])
        st.image(track_image[1])
        st.write(track_artist[1][0])

    with col3:
        st.header(track_name[2])
        st.image(track_image[2])
        st.write(track_artist[2][0])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.header(track_name[3])
        st.image(track_image[3])
        st.write(track_artist[3][0])

    with col2:
        st.header(track_name[4])
        st.image(track_image[4])
        st.write(track_artist[4][0])

    with col3:
        st.header(track_name[5])
        st.image(track_image[5])
        st.write(track_artist[5][0])


st.title('Music Recommender system')

playlistID = st.text_input('Playlist ID', '')


if st.button('Recommend'):
    recommended_track_id_list = get_recommendation(playlistID)

    track_name = get_track_name(recommended_track_id_list)
    track_artist = get_track_artist(recommended_track_id_list)
    track_image = get_track_image(recommended_track_id_list)

    display()

link='check out this [link](https://retailscope.africa/)'
st.markdown(link,unsafe_allow_html=True)


# col1, col2, col3 = st.columns(3)

# with col1:
#    st.header(track_name[0])
#    st.image(track_image[0])
#    st.write(track_artist[0][0])

# with col2:
#    st.header("A dog")
#    st.image("https://i.scdn.co/image/ab67616d0000b273c8d7445dbee75973efa970e8")
#    st.write('DRE')

# with col3:
#    st.header("An owl")
#    st.image("https://i.scdn.co/image/ab67616d0000b273a2aa64255899f18ea3c855c8")
#    st.write('DRE')

# col1, col2, col3 = st.columns(3)

# with col1:
#    st.header("A cat")
#    st.image("https://i.scdn.co/image/ab67616d0000b2739180ec245c2d22d169155c79")
#    st.write('DRE')

# with col2:
#    st.header("A dog")
#    st.image("https://i.scdn.co/image/ab67616d0000b273c8d7445dbee75973efa970e8")
#    st.write('DRE')

# with col3:
#    st.header("An owl")
#    st.image("https://i.scdn.co/image/ab67616d0000b273a2aa64255899f18ea3c855c8")
#    st.write('DRE')





# col1, col2, col3, col4, col5 = st.columns(5)

# with col1:
#    st.header("A cat")
#    st.image("https://i.scdn.co/image/ab67616d0000b2739180ec245c2d22d169155c79")

# with col2:
#    st.header("A dog")
#    st.image("https://i.scdn.co/image/ab67616d0000b273c8d7445dbee75973efa970e8")

# with col3:
#    st.header("An owl")
#    st.image("https://i.scdn.co/image/ab67616d0000b273a2aa64255899f18ea3c855c8")

# with col4:
#    st.header("A dog")
#    st.image("https://i.scdn.co/image/ab67616d0000b273c8d7445dbee75973efa970e8")

# with col5:
#    st.header("An owl")
#    st.image("https://i.scdn.co/image/ab67616d0000b273a2aa64255899f18ea3c855c8")