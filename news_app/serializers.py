from rest_framework import serializers

from .models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        models = News
        fields = ["title", "link", "published_at", "sentiment_score", "trends"]
