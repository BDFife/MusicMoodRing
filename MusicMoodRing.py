from flask import Flask
from flask import request
from flask import url_for, redirect
from flask import render_template

from lfmlibs import lfm_get_history

# from secrets import apikey, sign
# import urllib
# import json

app = Flask (__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lfm_playlist/<uname>')
def get_lfm_list(uname):
    my_tracks = lfm_get_history(uname, 20)
    return str(my_tracks)
#    return render_template('tracklist.html', tracks=my_tracks)

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.logger.debug('The logger is running, hooray!')
