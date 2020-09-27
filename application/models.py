from django.db import models
import datetime
from django.contrib.auth.models import User, auth
from django.db.models import Sum, Count
from django.utils.timezone import now

# Create your models here.


class department(models.Model):
    name = models.CharField(max_length=75, unique=True)
    related_profession_name = models.CharField(max_length=75)
    department_image = models.ImageField(upload_to='department_pics')
    short_description = models.CharField(max_length=75)

    def __str__(self):
        return self.name

class patient(models.Model):
    #user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='patient')
    first_name = models.CharField(max_length=75)
    username = models.CharField(max_length=75)
    selfie = models.ImageField(null=True,upload_to='images')
    last_name = models.CharField(max_length=75)
    email = models.CharField(max_length=75)
    password = models.CharField(max_length=32)
    gender = models.CharField(max_length=15, default="Nothing")
    age = models.IntegerField(default=0)

    def __str__(self):
        return self.first_name+" - "+self.email

class doctors(models.Model):
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    image = models.ImageField(upload_to='doctors_pic')
    email = models.CharField(max_length=75)
    city = models.CharField(max_length=75)
    password = models.CharField(max_length=32)
    gender = models.CharField(max_length=15, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')), default="Nothing")
    age = models.IntegerField(default=0)

    # PROFESSION_CHOICES = (
    #     ("Neurologist", "Neurologist"),
    #     ("Gynecologist", "Gynecologist"),
    #     ("Physiologist", "Physiologist"),
    #     ("Orthopedic", "Orthopedic")
    # )

    temp_list = []
    
    all_depts = department.objects.all()

    for i in all_depts:
        temp_val = [i.related_profession_name, i.related_profession_name]
        temp_list.append(tuple(temp_val))
        print(temp_val)


    PROFESSION_CHOICES = tuple(temp_list)


    profession = models.CharField(choices = PROFESSION_CHOICES, max_length=75)
    hospital = models.CharField(max_length=75)

    
    def __str__(self):
        return self.first_name+"  -  "+self.email

    def save(self, *args, **kwargs):
        if not self.pk:
            new_doctor = User.objects.create_user(username=self.email, first_name=self.first_name, password=self.password, last_name=self.last_name)
            new_doctor.save()
        super(doctors, self).save(*args, **kwargs)


class doctor_review(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(patient, on_delete=models.CASCADE)
    review_star = models.IntegerField()
    review_msg = models.TextField()
    doctor = models.ForeignKey(doctors, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.datetime.today().strftime('%Y-%m-%d'))

    def __str__(self):
        return 'Doctor: {}  -  Review author: {}  -  Date: {}'.format(self.doctor.first_name, self.author.first_name, self.date)



class appointment(models.Model):
    sender_patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    to_doctor = models.ForeignKey(doctors, on_delete=models.CASCADE)
    depart = models.CharField(max_length=50)
    appointment_date = models.DateField(null=True, blank=True)
    appointment_time = models.TimeField(null=True, blank=True)
    status = models.IntegerField(default=0)

    # -2 = cancelled
    # -1 = rejected
    #  0 = waiting for response
    #  1 = accepted
    #  2 = completed

    def __str__(self):
        return "Patient: {} ({})  -  Doctor: Dr.{} ({})  -  Date: {}  -  Time: {}".format(self.sender_patient.first_name, self.sender_patient.email, self.to_doctor.first_name, self.to_doctor.email, self.appointment_date, self.appointment_time)



class fakes(models.Model):
    USER = models.ForeignKey(patient, on_delete=models.CASCADE)
    is_fake = models.BooleanField(default=True)



class doctor_leave(models.Model):
    doctor = models.ForeignKey(doctors, on_delete=models.CASCADE)
    leave_date = models.DateField()

    def __str__(self):
        return "Dr. {} ({})  -  Date: {}".format(self.doctor.first_name, self.doctor.email, self.leave_date)


class doctor_with_review:
    def __init__(self, obj):
        self.Doctor = obj
        self.all_ratings = float(0)
        self.getting_reviews()

    def getting_reviews(self):
        if doctor_review.objects.filter(doctor=self.Doctor).exists():
            self.counting = doctor_review.objects.filter(doctor=self.Doctor).count()
            self.summing = doctor_review.objects.filter(doctor=self.Doctor).aggregate(Sum('review_star'))

            self.all_ratings = round(self.summing['review_star__sum'] / self.counting, 1)
        else:
            self.all_ratings = 0



class Chats(models.Model):
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sender')
    receiver = models.ForeignKey(User,on_delete=models.CASCADE,related_name='receiver')
    message = models.TextField(blank=True,null=True)
    time = models.TimeField(auto_now=True, blank=True)
    date = models.DateField(auto_now=True, blank=True)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return self.sender.username
