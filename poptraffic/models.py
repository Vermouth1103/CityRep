from django.db import models

# Create your models here.
class SpeedPredictionData(models.Model):
    file = models.FileField(upload_to='poptraffic', null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type")

    def __str__(self):
        return self.type

class SpeedPredictionHyperparameter(models.Model):

    # hyperparameter
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    lr = models.FloatField()
    dropout = models.FloatField()

class FlowPredictionData(models.Model):
    file = models.FileField(upload_to="poptraffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="route_plan_trajectory")

    def __str__(self):
        return self.type

class FlowPredictionHyperparameter(models.Model):

    # hyperparameter
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    lr = models.FloatField()
    dropout = models.FloatField()
    
