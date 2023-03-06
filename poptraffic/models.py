from django.db import models
import os

# Create your models here.

def extract_direcotry_path(instance, filename):
    print(instance)
    ext = filename.split('.')[-1]
    return os.path.join("road_network", filename)


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

    # road
    road_num = models.IntegerField()
    road_dim = models.IntegerField()

    # region
    region_num = models.IntegerField()
    region_dim = models.IntegerField()

    # zone
    zone_num = models.IntegerField()
    zone_dim = models.IntegerField()

class PopTrafficRoutePlanData(models.Model):
    file = models.FileField(upload_to="pop_traffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="route_plan_trajectory")

    def __str__(self):
        return self.type

    
