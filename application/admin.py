from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(doctors)
admin.site.register(department)
admin.site.register(appointment)
admin.site.register(fakes)
admin.site.register(doctor_review)
admin.site.register(doctor_leave)
admin.site.register(patient)
admin.site.register(Chats)