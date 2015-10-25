# coding: utf-8

import os

from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from flask_oauthlib.client import OAuth
from textblob import TextBlob

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key=os.environ['twitter_key'],
    consumer_secret=os.environ['twitter_secret'],
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


def tweet_avg_sentiment(tweet):
    blob = TextBlob(tweet['text'])
    return sum(s.sentiment.polarity for s in blob.sentences) / len(blob.sentences)

@app.route('/')
def index():
    error = False
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json?count=50&include_rts=true&exclude_replies=false')
        if resp.status == 200:
            tweets = resp.data

            for t in tweets:
            	t['avg_sentiment'] = tweet_avg_sentiment(t)
            return render_template('timeline.html', tweets=tweets)
        else:
            error = True
    return render_template('index.html', error=error)


# TODO: make version without login
#
# @app.route('/user/<username>')
# def user_timeline(username):
#     resp = twitter.request('statuses/user_timeline.json?screen_name={}'.format(username))
#     if resp.status == 200:
#         tweets = resp.data

#         for t in tweets:
#             t['avg_sentiment'] = tweet_avg_sentiment(t)
#         return render_template('timeline.html', tweets=tweets)


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
