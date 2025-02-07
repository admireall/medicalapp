from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class patient(models.Model):
    def __str__(self):
        return self.name
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=200)

class record(models.Model):
    def __str__(self):
        return self.patient.name
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    details = models.TextField()
    date = models.DateField()
    

class doctor(models.Model):
    def __str__(self):
        return self.name
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)  
    specialization = models.CharField(max_length=200)
    available_slots = models.JSONField()


    
class appointment(models.Model):
    def __str__(self):
        return self.patient.name
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('doctor', on_delete=models.CASCADE)  
    date = models.DateField()
    timeslot = models.JSONField()
    

    

    