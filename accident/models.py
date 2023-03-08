from django.db import models

# Create your models here.
class AccidentnData(models.Model):
    file = models.FileField(upload_to="poptraffic", null=True)
    type = models.CharField(max_length=50, verbose_name="Data Type", default="route_plan_trajectory")

    def __str__(self):
        return self.type