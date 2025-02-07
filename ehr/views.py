from django.shortcuts import render
from rest_framework import viewsets
from .serializers import patientSerializer, recordSerializer, doctorSerializer, appointmentSerializer
from .models import patient, record, doctor, appointment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import datetime
from .tasks import send_booking_email
from django.views.generic import TemplateView

#pass:Luckky@13
#anveshnagothu
#admin
#admin123
class create_user(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = patientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class get_user(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        try:
            users = patient.objects.filter(id=pk)
            serializer = patientSerializer(users, many=True)
            return Response(serializer.data)
        except patient.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
class delete_user(APIView):
    def delete(self, request, pk):
        user = patient.objects.get(pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class create_record(APIView):
    def post(self, request):
        serializer = recordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class get_record(APIView):
    def get(self, request, pk):
        try:
            patient_id = pk
            records = record.objects.filter(patient_id=patient_id)
            serializer = recordSerializer(records, many=True)
            return Response(serializer.data)
        except record.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
    
   

class deleteRecord(APIView):
    def delete(self, request, pk):
        try:
            rec = record.objects.get(pk=pk)
            rec.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except record.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)


class updateRecord(APIView):
    def put(self, request, pk):
        try:
            rec = patient.objects.get(pk=pk)
            serializer = recordSerializer(rec, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except record.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)


class create_doctor(APIView):
    def post(self, request):
        serializer = doctorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class get_doctor(APIView):
    def get(self, request):
        doctors = doctor.objects.all()
        serializer = doctorSerializer(doctors, many=True)
        return Response(serializer.data)
        


class create_appointment(APIView):
   
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = appointmentSerializer(data=request.data)
            if serializer.is_valid():
                pass
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            doctor_id = serializer.data.get('doctor')
            date_str = serializer.data.get('date')
            timeslot = serializer.data.get('timeslot')
            patient_name = serializer.data.get('patient')
            doct_obj=doctor.objects.get(name=doctor_id)
    

            if not all([doctor_id, date_str, timeslot, patient_name]):
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate date format
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            patient_instance = get_object_or_404(patient, name=patient_name)

            if not doct_obj.available_slots or date_str not in doct_obj.available_slots:
                return Response(
                    {"error": "No slots available for this date"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if timeslot not in doct_obj.available_slots.get(date_str, []):
                return Response(
                    {"error": "Selected slot is not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if appointment.objects.filter(
                doctor=doct_obj,
                date=date,
                timeslot=timeslot
            ).exists():
                return Response(
                    {"error": "This slot is already booked"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            new_appointment = appointment.objects.create(
                doctor=doct_obj,
                patient=patient_instance,
                date=date,
                timeslot=timeslot
            )

            available_slots = doct_obj.available_slots.copy()
            available_slots[date_str].remove(timeslot)
            doct_obj.available_slots = available_slots
            doct_obj.save()
            send_booking_email.delay(
                "Appointment Confirmation",
                f"Dear {patient_name}, your appointment with {doct_obj.name} on {date_str} at {timeslot} is confirmed.",
                [patient_instance.email]
            )
            return Response(
                appointmentSerializer(new_appointment).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    
class get_appointment(APIView):
    def get(self, request, pk):
        appointments = appointment.objects.filter(patient=pk)
        serializer = appointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
class reschedule_appointment(APIView):
    def put(self, request, pk):
        try:
            
            patient_name = request.data.get('patient')
            old_date = request.data.get('old_date')
            old_timeslot = request.data.get('old_timeslot')
            
            patient_instance = get_object_or_404(patient, name=patient_name)
            
            apt = appointment.objects.get(
                patient=patient_instance,
                date=old_date,
                timeslot=old_timeslot
            )
            
            new_date = request.data.get('new_date')
            new_timeslot = request.data.get('new_timeslot')
            
            if not new_date or not new_timeslot:
                return Response(
                    {"error": "New date and timeslot are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            doctor_obj = apt.doctor
            if not doctor_obj.available_slots or new_date not in doctor_obj.available_slots:
                return Response(
                    {"error": "No slots available for this date"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if new_timeslot not in doctor_obj.available_slots.get(new_date, []):
                return Response(
                    {"error": "Selected slot is not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            old_date_str = apt.date.strftime('%Y-%m-%d')
            available_slots = doctor_obj.available_slots.copy()
            
            if old_date_str in available_slots:
                if apt.timeslot not in available_slots[old_date_str]:
                    available_slots[old_date_str].append(apt.timeslot)
                    available_slots[old_date_str].sort()  
            else:
                
                available_slots[old_date_str] = [apt.timeslot]
            
            available_slots[new_date].remove(new_timeslot)
            
            doctor_obj.available_slots = available_slots
            doctor_obj.save()
            
            apt.date = new_date
            apt.timeslot = new_timeslot
            apt.save()
            send_booking_email.delay(
                "Appointment Rescheduled",
                f"Dear {patient_name}, your appointment with {doctor_obj.name} has been rescheduled to {new_date} at {new_timeslot}.",
                [patient_instance.email]
            )
            
            serializer = appointmentSerializer(apt)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
    
class cancel_appointment(APIView):
    def delete(self, request, pk):
        patient_name = request.data.get('patient')
        date = request.data.get('date')
        timeslot = request.data.get('timeslot')
        
        try:
            patient_instance = patient.objects.get(name=patient_name)
            
            if appointment.objects.filter(patient=patient_instance, date=date, timeslot=timeslot).exists():
                appointment_to = appointment.objects.get(patient=patient_instance, date=date, timeslot=timeslot)
                
                doctor_obj = appointment_to.doctor
                available_slots = doctor_obj.available_slots.copy()
                
                
                if hasattr(date, 'strftime'):
                    date_str = date.strftime('%Y-%m-%d')
                else:
                    date_str = date
                
                if date_str in available_slots:
                    if timeslot not in available_slots[date_str]:
                        available_slots[date_str].append(timeslot)
                        available_slots[date_str].sort()
                else:
                    available_slots[date_str] = [timeslot]
                
                doctor_obj.available_slots = available_slots
                doctor_obj.save()
                
                appointment_to.delete()
                send_booking_email.delay(
                "Appointment Canceled",
                f"Dear {patient_name}, your appointment with {doctor_obj.name} on {date_str} at {timeslot} has been canceled.",
                [patient_instance.email]
            )
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
                
        except patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        

