from djongo import models
from django.utils import timezone
from accounts.models import User


class Election(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.EmailField()  # Admin email
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'elections'

    def __str__(self):
        return self.title

    def is_ongoing(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def has_started(self):
        return timezone.now() >= self.start_date

    def has_ended(self):
        return timezone.now() > self.end_date


class Candidate(models.Model):
    _id = models.ObjectIdField()
    election_id = models.CharField(max_length=100)  # Store election ObjectId as string
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='candidates/', null=True, blank=True)
    position = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'candidates'

    def __str__(self):
        return f"{self.name} - {self.position}"


class LocationData(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True


class Vote(models.Model):
    _id = models.ObjectIdField()
    election_id = models.CharField(max_length=100)
    candidate_id = models.CharField(max_length=100)
    voter_email = models.EmailField()
    voter_image = models.ImageField(upload_to='voter_images/')
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votes'
        unique_together = ['election_id', 'voter_email']

    def __str__(self):
        return f"Vote by {self.voter_email}"
