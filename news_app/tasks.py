import os
import random
from datetime import datetime, timedelta

import environ
import feedparser
import pytz
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone
from dotenv import load_dotenv
from openai import OpenAI

from .models import News

load_dotenv()
RSS_FEED_URL = "https://tsn.ua/rss/full.rss"
GOOGLE_TRENDS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=UA"
API_KEY = str(os.getenv("key"))

client = OpenAI(api_key=API_KEY)


@shared_task(name="sentiment-task")
def fetch_news_and_update_sentiment():
    # Fetch RSS feed
    feed = feedparser.parse(RSS_FEED_URL)
    news_items = feed.entries

    trends_feed = feedparser.parse(GOOGLE_TRENDS_URL)
    # print(trends_feed)
    trending_topics = [entry.title for entry in trends_feed.entries]

    for news_item in news_items:
        try:
            published_at = datetime(*news_item.published_parsed[:6])
            published_at = pytz.utc.localize(published_at)
        except (TypeError, ValueError):
            published_at = timezone.now()

        one_week_ago = timezone.now() - timedelta(days=7)

        if published_at >= one_week_ago:
            title = news_item.title
            link = news_item.link
            if any(trend.lower() in title.lower() for trend in trending_topics):
                # print(f"Trending Topics: {trending_topics}")
                existing_news = News.objects.filter(title=title).first()
                if existing_news:
                    print(f"Skipping sentiment analysis for '{title}' (already exists)")
                    continue
                sentiment_score = get_sentiment(title)
                print(f"Sentiment Score: {sentiment_score}")
                news_obj = News.objects.create(
                    title=title,
                    published_at=published_at,
                    sentiment_score=sentiment_score,
                    link=link,
                    trends=", ".join(
                        [
                            trend
                            for trend in trending_topics
                            if trend.lower() in title.lower()
                        ]
                    ),
                )
                print(f"Created new News object: {news_obj}")


def get_sentiment(text):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a sentiment analysis assistant. Do not provide any additional explanation or context. Analyze the given text and respond with a single numeric value representing the sentiment score between -1 (negative) and 1 (positive).",
            },
            {"role": "user", "content": text},
        ],
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    print(response.json())
    sentiment_score = analyze_sentiment(
        response.json()["choices"][0]["message"]["content"]
    )
    return sentiment_score


def analyze_sentiment(text):
    try:
        sentiment_score = float(text.strip())
        if sentiment_score < -1 or sentiment_score > 1:
            raise ValueError("Sentiment score should be between -1 and 1")
    except ValueError:
        sentiment_score = 0.0
    return sentiment_score
