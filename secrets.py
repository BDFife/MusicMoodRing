"""
This is a place to hold API keys and tools for managing these keys

Things like assembling sig/hashes are taken care of also. 
This is designed to allow this code to be deployed to Heroku
without checking in API keys. Do this by setting your app 
environments with the command: 

heroku config:add VAR_NAME=value

Thanks to Buddy Lindsey for advice on setting up Heroku. 
"""

import os
import time
import hashlib

# Insert your own secrets here
APIKEY = str(os.environ.get('ROVI_KEY', 'Your Rovi key'))
LFMKEY = str(os.environ.get('LFM_KEY', 'Your last.fm key'))
SECRET = str(os.environ.get('ROVI_SECRET', 'Your Rovi secret'))

def apikey():
    return APIKEY

def secret():
    return SECRET

def lfmkey():
    return LFMKEY

def sign():
    my_time = int(time.time())
    sig = hashlib.md5()
    sig.update(APIKEY)
    sig.update(SECRET)
    sig.update(str(my_time))

    return sig.hexdigest()

#if __name__ == '__main__':
#    return sign()
