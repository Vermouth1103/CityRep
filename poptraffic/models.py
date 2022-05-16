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