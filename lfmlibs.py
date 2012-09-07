import requests
from secrets import apikey, sign, lfmkey

def lfm_get_history(uid, number): 
    """ 
    Get a list of played/scrobbled tracks from a lfm user's history.
    
    This takes the last.fm user ID and the number of desired tracks as input. 
    It also requires a valid last.fm api key present in the 'secrets' file. 
    
    This calls the last.fm API user.getrecenttracks, and returns a python dict
    generated from the JSON reply. 
    """


    # Fixme - add in headers as well with a customer user-agent and gzip enabled
    req_vars = {'method': 'user.getrecenttracks',
                'user': uid,
                'api_key': lfmkey(),
                'limit': number,
                'format': 'json'}

    r = requests.get('http://ws.audioscrobbler.com/2.0', params=req_vars)

    history = r.json
    return historyt

if __name__ == '__main__':
    
    my_tracks = lfm_get_history('bdfife', 20)
    print my_tracks
