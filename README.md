# HaterBlocker
Gets tweets from your timeline, throws them through a sentiment analysis library and only shows the positive ones.

Currently live at haterblocker.herokuapp.com

To install:
1) Run virtualenv and pip install from requirements
2) Get nltk to point to the right folder: export NLTK_DATA="$PWD/nltk_data"
3) Run with python haterblocker.py
