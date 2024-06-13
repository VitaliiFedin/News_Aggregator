from rest_framework import viewsets

from .models import News
from .serializers import NewsSerializer

# Create your views here.


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all().order_by("-sentiment_score")
    serializer_class = NewsSerializer
