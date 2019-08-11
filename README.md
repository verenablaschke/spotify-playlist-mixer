# Spotify Playlist Mixer

## Requirements

- Python 3
- The Spotipy library. If you do not need playlist descriptions, the pypi version will do, otherwise you need to work with the current development version.
```
pip install --upgrade spotipy
# or
pip install git+https://github.com/plamere/spotipy.git --upgrade
```

## Config
Rename `config-SAMPLE.py` to `config.py` and update the values. 
To get the playlist IDs, right-click on a playlist title and select `Share > Copy Spotify URI`.

## Running the script
In the directory containing the script, run `python mix.py`.

If running the script for the first time, your browser will open
and Spotify will ask you to agree that the _Playlist Mixer_ application can access some of your account information.
Confirm this.
You will be redirected to a URL starting with `http://localhost/?code=`.
Paste this URL into the command line.

Check out the resulting playlist!
