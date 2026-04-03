from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    date_joined = models.DateField()
    position = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    contact_person = models.CharField(max_length=100)

    def __str__(self):
        return self.name