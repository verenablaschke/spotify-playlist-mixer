import datetime
import random
import re
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


def find_most_recently_created_playlist(username, playlist_pattern):
    playlists = sp.user_playlists(username, limit=50)
    matching_playlists = []
    for i, item in enumerate(playlists['items']):
        if re.search(playlist_pattern, item['name']):
            matching_playlists.append((item['uri'], item['name']))
    if matching_playlists:
        matching_playlists.sort(key=lambda tup: tup[1])
        return matching_playlists[-1]
    return None, None


def create_playlist(username, playlist_name, public, description):
    # The current pip version of Spotify doesn't accept descriptions
    # (see README).
    if config.mix_playlist_description:
        try:
            return sp.user_playlist_create(username, playlist_name, public,
                                           description)['uri']
        except TypeError:
            pass
    return sp.user_playlist_create(username, playlist_name, public)['uri']


token = util.prompt_for_user_token(config.username,
                                   scope='playlist-modify-public '
                                   'playlist-modify-private '
                                   'playlist-read-private',
                                   client_id=config.client_id,
                                   client_secret=config.client_secret,
                                   redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    playlist_pattern = '^' + re.escape(config.mix_playlist_prefix.strip()) + \
                       ' \d\d\d\d-\d\d-\d\d( \d+)?$'
    prev_mix_playlist, prev_mix_name = find_most_recently_created_playlist(
                                        config.username,
                                        playlist_pattern)

    old_songs = []
    if prev_mix_playlist:
        old_songs = get_playlist_contents(sp, config.username,
                                          prev_mix_playlist)
    already_picked = []

    for playlist_id, num_songs in zip(config.source_playlist_ids,
                                      config.songs_per_source_playlist):
        songs = get_playlist_contents(sp, config.username, playlist_id)
        songs = pick_songs_from_playlist(songs, num_songs,
                                         old_songs, already_picked,
                                         config.username, playlist_id)
        already_picked.extend(songs)

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    playlist_name = config.mix_playlist_prefix.strip() + ' ' + date
    if prev_mix_playlist and prev_mix_name.startswith(playlist_name):
        # Already a playlist from this day!
        counter = 1
        if len(prev_mix_name) > len(playlist_name):
            counter = re.findall(' \d+$', prev_mix_name)[0]
            counter = int(counter.strip())
            counter += 1
        playlist_name += ' ' + str(counter)

    new_playlist = create_playlist(config.username, playlist_name,
                                   config.public_mix_playlist,
                                   config.mix_playlist_description)

    sp.user_playlist_add_tracks(config.username, new_playlist, already_picked)

else:
    print("Can't access the authorization token.")
