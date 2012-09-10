"""
Last.fm Libraries
"""

import requests
from secrets import apikey, sign, lfmkey

def lfm_get_info(uid, number):
    my_tracks = lfm_get_history(uid, number)
    clean_tracks = lfm_scrub_json(my_tracks)
    rovi_albums = lfm_match_album(clean_tracks)
    return rovi_albums

def lfm_get_history(uid, number): 
    """ 
    Get a list of played/scrobbled tracks from a lfm user's history.
    
    This takes the last.fm user ID and the number of desired tracks as input. 
    It also requires a valid last.fm api key present in the 'secrets' file. 
    
    This calls the last.fm API user.getrecenttracks, and returns a python dict
    generated from the JSON reply. 
    """
    # Fixme - what is the max number that can be returned in a single page? 
    # Fixme - add in headers as well with a customer user-agent and gzip enabled
    req_vars = {'method': 'user.getrecenttracks',
                'user': uid,
                'api_key': lfmkey(),
                'limit': number,
                'format': 'json'}

    r = requests.get('http://ws.audioscrobbler.com/2.0', params=req_vars)

    history = r.json
    return history

def lfm_scrub_json(history):
    """
    Takes raw JSON-turned-dict result from getrecenttracks and cleans it up. 

    The function identifies missing track, album, and artist fields. It also 
    strips elements from the JSON reply that are peripheral to the track list. 
    
    This builds a python list [ ] with each track entry a dict with artist, 
    album title, and track name. If fields are missing, their data will be
    inserted as None. 

    If the read process fails for some reason, this will return False
    """
    
    track_list = history.get('recenttracks', False)
    # I believe the if clause is needed, just in case the previous fails. 
    if track_list: 
        track_list = track_list.get('track', False)

    # If the required track entries are missing, return false
    
    if track_list:
        tracks = [ ] 

        for track in track_list:
            # name is a raw string
            name = track.get('name')
            
            # album is a dict that includes mbid and #text
            album = track.get('album', False)
            if album: 
                album = album.get(r'#text')
            
            # artist is a dict that includes mbid and #text
            artist = track.get('artist', False)
            if artist: 
                artist = artist.get(u'#text')

            tracks.append({'artist':artist, 'album':album, 'track':name})
        return tracks
    else:
        return False

def lfm_match_album(tracks):
    """
    Match a set of tracks from LFM listening history by album, with moods/tones

    The intuitive thing to do here would be to perform a track level
    match and then request track level data on moods and tones. I'm not 
    planning to do this, looking at album-level instead for two reasons. 

    First, the Rovi API doesn't provide track-level mood/tone data. 
    Second, the Rovi API reasonable requires two API calls to get this
    on a track basis, and I can do it in a single go with the match/album API. 

    This function currently only considers the best match and does not perform
    any sanity-checking or worry about accuracy in any way. 

    It queries Rovi's Match/Album API. 
    """

    # Fixme: I should consider a shortcut for this which avoids multiple calls
    # to the same (suspected) album 

    rovi_ids = [ ] 
    for track in tracks:
        # Fixme: handle missing elements in the LFM data? 
        req_vars = {'name': track['album'],
                    'performername': track['artist'],
                    'include': 'moods,themes',
                    'size': 1,
                    'format': 'json',
                    'apikey': apikey(),
                    'sig': sign()}
 
        r = requests.get('http://api.rovicorp.com/recognition/v2.1/music/match/album',
                         params=req_vars)
        
        album_match = r.json
        
        album_data = album_match.get('matchResponse', False)
        if album_data:
            album_data = album_data.get('results', False)
        if album_data:
            # This should be a single entry list
            album_data = album_data[0]
            album_id = album_data.get('id')
            album_info = album_data.get('album')
            rovi_moods = album_info.get('moods')
            rovi_themes = album_info.get('themes')

            rovi_ids.append({'album_id': album_id,
                             'track': track['track'],
                             'artist': track['artist'],
                             'album': track['album'],
                             'moods': rovi_moods,
                             'themes': rovi_themes})

        # Continue looping through the tracks in list above.

    return rovi_ids

def lfm_match_tracks(tracks):
    """ 
    Associate Rovi IDs with a list of tracks from LFM listening history

    Take a track list in the format {artist: 'artist', track: 'track', 
    album: 'album'}

    This will use Rovi's match API to get a track ID back.
    It returns a list [ ] with format # Fixme.

    At the moment, the plan is to only record the single, best match and
    not worry too much about sanity-checking the accuracy of the match.

    This function is quite expensive since it requires a http call for 
    each track in the list. It currently works, more or less, but 
    is not actually used in the web app so hasn't been tested with a lot
    of data. lfm_match_album was used instead. 
    """
    
    rovi_ids = [ ] 
    for track in tracks:
        # Calling Rovi Match API - track match.
        # Fixme: manage missing album, artist case? 
        req_vars = {'name': track['track'],
                    'performername': track['artist'],
                    'albumtitle': track['album'],
                    'include': 'appearances',
                    'size': 1,
                    'format': 'json',
                    'apikey': apikey(),
                    'sig': sign() 
                    }
        r = requests.get('http://api.rovicorp.com/recognition/v2.1/music/match/track', 
                         params=req_vars)
        
        track_match = r.json

        track_data = track_match.get('matchResponse', False)
        if track_data: 
            track_data = track_data.get('results')
        if track_data: 
            # At this point we should have a single-element list. 
            # All I am looking for at this point, blindly, is ID
            # First, the unambiguous track_ID, and then a possibly
            # one-to-many album_ID. 
            # I'm not doing anything to check that I have the 
            # 'right' album_ID
            # Fixme: Ask the Rovi team about appearances API. 
            # Fixme: Put in some sanity checking here. 

            # Fixme: Ask Will about multi-level dict checking. I'm 
            # not happy with the way this code below is written. 
            track_data = track_data[0]
            rovi_track_id = track_data.get('id')
            rovi_song_data = track_data.get('song', False)
            rovi_track_appearances = False
            if rovi_song_data:                
                rovi_track_appearances = rovi_song_data.get('appearances', False)
            appearance_ids = False
            rovi_album_id = None
            if rovi_track_appearances:
                appearance_ids = rovi_track_appearances[0].get('ids', False)
            if appearance_ids:
                rovi_album_id = appearance_ids.get('albumId')

            # Append to the new list
            # This could be done by assigning the object directly.
            rovi_ids.append({'track_ID': rovi_track_id,
                             'track': track['track'],
                             'artist': track['artist'],
                             'album': track['album'],
                             'album_ID': rovi_album_id})            
        
        # Continue looping through tracks in list above
    
    return rovi_ids

if __name__ == '__main__':
    """ 
    Allow debugging these libraries from the command line

    Helpfully, no actual debug messages are used :) 
    """
    
    my_tracks = lfm_get_history('bdfife', 20)
    clean_tracks = lfm_scrub_json(my_tracks)
    rovi_albums = lfm_match_album(clean_tracks)
    print rovi_albums    
