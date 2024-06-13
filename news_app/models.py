from django.db import models

# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    published_at = models.DateTimeField()
    sentiment_score = models.FloatField()
    trends = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title
