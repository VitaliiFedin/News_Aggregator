from datetime import datetime, timedelta

import requests
from celery import shared_task
from django.utils import timezone

from .models import News

RSS_FEED_URL = "https://tsn.ua/rss/full.rss"
GOOGLE_TRENDS_URL = "https://trends.google.com/trends/trendingsearches/daily?geo=UA"
API_KEY = "your-chatgpt-api-key"
