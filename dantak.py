import nltk
nltk.downloader.download("SentimentIntensityAnalyzer")


import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googleapiclient.discovery import build
from translate import Translator
from scipy import signal

YOUTUBE_KEY = st.secrets["youtube_key"]
PLAYLIST_ID = st.secrets["playlist_id"]
TRANSLATOR_KEY = st.secrets["translator_key"]
youtube = build("youtube", "v3", developerKey=YOUTUBE_KEY)

def get_res(pageToken = None):
    request = youtube.playlistItems().list(
        part="snippet, contentDetails",
        playlistId=PLAYLIST_ID,
        maxResults = 50,
        pageToken = pageToken
    )
    response = request.execute()
    return response

def get_firstVideoLink(response):
    videoID = response["items"][0]["contentDetails"]["videoId"]
    channelTitle = response["items"][0]["snippet"]["channelTitle"]
    return f"https://www.youtube.com/watch?v={videoID}&ab_channel={channelTitle}"

def get_videoInfo(response):
    titles = []
    timePublished = []
    for item in response["items"]:
        titles.append(item["snippet"]["title"])
        timePublished.append(item["contentDetails"]["videoPublishedAt"])
    for i in range(9):
        pageToken = response["nextPageToken"]
        response = get_res(pageToken = pageToken)
        for item in response["items"]:
            titles.append(item["snippet"]["title"])
            timePublished.append(item["contentDetails"]["videoPublishedAt"])
    return titles, timePublished

def translate_titles(titles):
    translator = Translator(provider="microsoft", from_lang="ja",
                       to_lang="en", secret_access_key=TRANSLATOR_KEY)
    translation = [translator.translate(title) for title in titles]
    return titles, translation

def get_dataframe(titles, translation, timePublished):
    timePublished = pd.to_datetime(pd.Series(timePublished)).dt.date
    df = pd.DataFrame.from_dict({"title": titles, "translated_title":translation, "datePublished":timePublished})
    vader = SentimentIntensityAnalyzer()
    getscorefunc = lambda title: vader.polarity_scores(title)["compound"]
    df["compound"] = df["translated_title"].apply(getscorefunc)
    return df

def get_latestTitles(df):
    return df["translated_title"].head()

def plot_sentimentChart(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["datePublished"],
        y=df["compound"],
        mode='markers',
        marker=dict(size=2, color='black'),
        name='Data point'
    ))

    fig.add_trace(go.Scatter(
        x=df["datePublished"],
        y=signal.savgol_filter(df["compound"],
                            53, # window size used for filtering
                            3), # order of fitted polynomial
        mode='markers',
        marker=dict(
            size=6,
            color='mediumpurple',
            symbol='triangle-up'
        ),
        name='Savitzky-Golay calculation'
    ))

    fig.update_layout(
        title="Sentiment of video title by date",
        xaxis_title="Date",
        yaxis_title="Compound sentiment",
        legend_title="Legend",
        font=dict(
            family="DejaVu, Sans",
            size=12,
        ),
        width=1200,
        height=600,
    )

    return fig

def plot_wordCloud(df):
    text = " ".join(df["translated_title"][:20])

    # Create and generate a word cloud image:
    stopwords = set(STOPWORDS)
    stopwords.update(["PostPrime", "prime", "stock", "stocks"])
    wc = WordCloud(background_color="white", max_words=1000, stopwords=stopwords)
    wordcloud = wc.generate(text)

    # Display the generated image:
    fig = plt.figure(figsize=(12,12))
    axes = plt.axes()
    fig.suptitle("Word cloud for past 7 days", fontsize=12, y=0.72)
    axes.imshow(wordcloud, interpolation='bilinear')
    axes.axis("off")
    return fig

def main():
    st.set_page_config(page_title="Dan Takahashi Youtube", layout="wide")
    st.title("Dan Takahashi Youtube Translator + Sentiment Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.image("dantak.jpeg", width=500)
        st.caption("Dan Takahashi")
        response = get_res()
        titles, timePublished = get_videoInfo(response)
        titles, translation = translate_titles(titles)
        df = get_dataframe(titles, translation, timePublished)
        st.subheader("Last 500 videos info")
        st.write(df)
    with col2:
        st.markdown('''Trader + Youtuber + Influencer  
        PostPrime Founder. 930k Followers on Social Media.  
        Love natto beans + karaoke + Japan ❤  
        [Intro](https://www.thetop100magazine.com/dan-takahashi)&emsp;
        [Youtube](https://www.youtube.com/channel/UCFXl12dZUPs7MLy_dMkMZYw)&emsp; 
        [Twitter](https://twitter.com/dan_takahashi_?lang=en)''')
        firstVideoLink = get_firstVideoLink(response)
        st.video(firstVideoLink)
        st.subheader("Latest titles")
        st.write(get_latestTitles(df))
    fig = plot_sentimentChart(df)
    st.plotly_chart(fig)
    fig = plot_wordCloud(df)
    st.pyplot(fig)


if __name__ == '__main__':
    main()
