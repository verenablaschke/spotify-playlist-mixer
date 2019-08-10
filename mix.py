import random
import spotipy
import spotipy.util as util
import config


def get_playlist_contents(sp, username, playlist_id):
    results = sp.user_playlist(username, playlist_id, 'tracks,items,track,uri')
    contents = []
    for item in results['tracks']['items']:
        contents.append(item['track']['uri'].split(':')[2])
    return contents


def pick_songs_from_playlist(song_ids, num_songs, old_songs, already_picked,
                             username, playlist_id):
    if len(song_ids) <= num_songs:
        playlist_name = sp.user_playlist(username, playlist_id, 'name')['name']
        print('{} contains only {} songs, but I am supposed to pick {}. '
              'Choosing all songs.'
              .format(playlist_name, len(song_ids), num_songs))
        return song_ids
    songs_picked = []
    i = 0
    max_iter = 1000  # TODO what's a reasonable number here?
    skip_old_songs = True
    while len(songs_picked) < num_songs:
        i += 1
        if i == max_iter:
            if skip_old_songs:
                playlist_name = sp.user_playlist(username, playlist_id,
                                                 'name')['name']
                print('Need to include previously used songs from ' +
                      playlist_name)
                skip_old_songs = False
                i = 0
            else:
                # TODO Could also systematically go through list and add songs.
                print('Cannot find more new songs from ' + playlist_name)
                break
        song = random.choice(song_ids)
        if song in songs_picked or song in already_picked or \
                (skip_old_songs and song in old_songs):
            continue
        songs_picked.append(song)
    return songs_picked


scope = 'playlist-modify-public playlist-modify-private'
token = util.prompt_for_user_token(config.username,
                                   scope,
                                   client_id=config.client_id,
                                   client_secret=config.client_secret,
                                   redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    old_songs = get_playlist_contents(sp, config.username,
                                      config.mix_playlist_id)
    already_picked = []

    for playlist_id, num_songs in zip(config.source_playlist_ids,
                                      config.songs_per_source_playlist):
        songs = get_playlist_contents(sp, config.username, playlist_id)
        songs = pick_songs_from_playlist(songs, num_songs,
                                         old_songs, already_picked,
                                         config.username, playlist_id)
        already_picked.extend(songs)

    sp.user_playlist_replace_tracks(config.username,
                                    config.mix_playlist_id, already_picked)

else:
    print("Can't access the authorization token.")
