from django.db import models

# Create your models here.

class Data(models.Model):
    file = models.FileField(upload_to='poptraffic', null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type")

    def __str__(self):
        return self.type

class Hyperparameter(models.Model):

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