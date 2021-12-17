import streamlit as st
import pandas as pd
import altair as alt
import os
import yaml
import requests
from googleapiclient.discovery import build

CONFIG_FILE = "auth.yaml"
with open(CONFIG_FILE, "r") as config_file:
    config = yaml.safe_load(config_file)
YOUTUBE_KEY = config["youtube"]["api_key"]

youtube = build("youtube", "v3", developerKey=YOUTUBE_KEY)

if __name__ == '__main__':
    # Disable OAuthlib's HTTPs verification when running locally.
    # *DO NOT* leave this option enabled when running in production.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    youtubeAnalytics = get_service()
    execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate='2017-01-01',
        endDate='2017-12-31',
        metrics='estimatedMinutesWatched,views,likes,subscribersGained'
        dimensions='day',
        sort='day'
    )

    st.set_page_config(
        page_title="Singapore Trade Visualisation")

    st.title("Singapore Trade Visualisation")
