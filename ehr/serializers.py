from rest_framework import serializers
from .models import patient, record, doctor, appointment

class patientSerializer(serializers.ModelSerializer):
    class Meta:
        model = patient
        fields = '__all__'

class recordSerializer(serializers.ModelSerializer):
    class Meta:
        model = record
        fields = '__all__'

class doctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = doctor
        fields = '__all__'

class appointmentSerializer(serializers.ModelSerializer):
    patient = serializers.SlugRelatedField(
        queryset=patient.objects.all(),
        slug_field='name'
    )
    doctor = serializers.SlugRelatedField(
        queryset=doctor.objects.all(),
        slug_field='name'
    )
    
    class Meta:
        model = appointment
        fields = ['doctor', 'patient', 'date', 'timeslot']