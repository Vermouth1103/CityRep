from django.db import models

# Create your models here.

class PopTrafficData(models.Model):
    file = models.FileField(upload_to='pop_traffic', null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type")

    def __str__(self):
        return self.type

class PopTrafficHyperparameter(models.Model):

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

class PopTrafficRoutePlanData(models.Model):
    file = models.FileField(upload_to="pop_traffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="route_plan_trajectory")

    def __str__(self):
        return self.type

class PopTrafficRoutePlanHyperparameter(models.Model):

    # hyperparameter
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    lr = models.FloatField()
    dropout = models.FloatField()
    
