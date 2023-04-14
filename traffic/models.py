from django.db import models

# Create your models here.

class RepresentationData(models.Model):
    file = models.FileField(upload_to='traffic', null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type")

    def __str__(self):
        return self.type

class RepresentationHyperparameter(models.Model):

    # hyperparameter
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    lr = models.FloatField()
    dropout = models.FloatField()

    # road_hp
    road_num = models.IntegerField()
    road_dim = models.IntegerField()

    # region_hp
    region_num = models.IntegerField()
    region_dim = models.IntegerField()

    # zone_hp
    zone_num = models.IntegerField()
    zone_dim = models.IntegerField()

class AccidentData(models.Model):
    file = models.FileField(upload_to="traffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="accident_data")

    def __str__(self):
        return self.type

class RoutePlanData(models.Model):
    file = models.FileField(upload_to="traffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="route_plan_data")

    def __str__(self):
        return self.type

class RoutePlanHyperparameter(models.Model):

    # hyperparameter
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    lr = models.FloatField()
    dropout = models.FloatField()

class NextLocData(models.Model):
    file = models.FileField(upload_to="traffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="next_loc_data")

    def __str__(self):
        return self.type

class NextLocHyperparameter(models.Model):

    # hyperparameter
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    lr = models.FloatField()
    dropout = models.FloatField()

class SpeedPredictionData(models.Model):
    file = models.FileField(upload_to="traffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="speed_prediction_data")

    def __str__(self):
        return self.type
