from django.contrib.auth.models import AbstractUser
from django.db import models


class AppUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


class DataGenerationParams(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    time_mean = models.FloatField(default=12.0)
    time_std = models.FloatField(default=3.0)
    price_mean = models.FloatField(default=30.0)
    price_std = models.FloatField(default=10.0)
    pages_mean = models.FloatField(default=100.0)
    pages_std = models.FloatField(default=30.0)
    num_records = models.PositiveIntegerField(default=100, help_text="Number of records (100 to 1000)")


class DataSet(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    time_data = models.CharField(max_length=100)
    genre_data = models.CharField(max_length=100)
    price_data = models.FloatField()
    pages_data = models.PositiveIntegerField()
    params = models.ForeignKey(DataGenerationParams, null=True, on_delete=models.CASCADE)
