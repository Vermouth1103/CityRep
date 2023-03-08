from django.db import models

# Create your models here.
class RoutePlanData(models.Model):
    file = models.FileField(upload_to="indtraffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="route_plan_trajectory")

    def __str__(self):
        return self.type

class RoutePlanHyperparameter(models.Model):

    # hyperparameter
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    lr = models.FloatField()
    dropout = models.FloatField()

class NextLocData(models.Model):
    file = models.FileField(upload_to="indtraffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="route_plan_trajectory")

    def __str__(self):
        return self.type

class NextLocHyperparameter(models.Model):

    # hyperparameter
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    lr = models.FloatField()
    dropout = models.FloatField()

