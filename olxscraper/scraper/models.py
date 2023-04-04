from django.db import models

class OlxAdvertisement(models.Model):
    """Model representing an Olx advertisement."""

    title = models.TextField()
    price = models.FloatField()
    location = models.TextField()
    advertiser_name = models.TextField()
    advertiser_phone_number = models.CharField(max_length=20)
    olx_id = models.CharField(max_length=100)
    olx_query = models.ForeignKey('scraper.OlxQuery', on_delete=models.PROTECT)

class OlxQuery(models.Model):
    """Model representing an Olx query."""

    search_keyword = models.TextField()
    date_created = models.DateField(auto_now_add=True)
