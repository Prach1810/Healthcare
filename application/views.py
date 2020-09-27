from django.shortcuts import render, redirect,reverse
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.contrib.auth.models import User, auth
import json
from django.db.models import Q
from webapp.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from application.forms import *
from django.conf import settings
import pandas as pd
import joblib
# Create your views here.



def partition(arr,low,high): 
    i = ( low-1 )         # index of smaller element 
    pivot = arr[high].all_ratings    # pivot 
  
    for j in range(low , high): 
  
        # If current element is smaller than the pivot 
        if   arr[j].all_ratings > pivot: 
          
            # increment index of smaller element 
            i = i+1 
            arr[i],arr[j] = arr[j],arr[i] 
  
    arr[i+1],arr[high] = arr[high],arr[i+1] 
    return ( i+1 ) 
  
# The main function that implements QuickSort 
# arr[] --> Array to be sorted, 
# low  --> Starting index, 
# high  --> Ending index 
  
# Function to do Quick sort 
def quickSort(arr,low,high): 
    if low < high: 
  
        # pi is partitioning index, arr[p] is now 
        # at right place 
        pi = partition(arr,low,high) 
  
        # Separately sort elements before 
        # partition and after partition 
        quickSort(arr, low, pi-1) 
        quickSort(arr, pi+1, high)



def get_ratings_objects(myList, con):
    temping = []
    if not con:
        for i in myList:
            t = doctor_with_review(i)
            temping.append(t)
    else:
        for i in myList:
            t = doctor_with_review(i)
            if t.all_ratings != 0:
                temping.append(t)

    return temping


def get_patient_obj_by_email(mail):
    return patient.objects.get(email=mail)


def isPatient(mail):
    return patient.objects.filter(email=mail).exists()


def index(request):
    context = {}

    all_depts = department.objects.all()
    context['departments'] = all_depts

    all_my_doctors = doctors.objects.all()

    all_doctors_with_review = get_ratings_objects(all_my_doctors, True)

    quickSort(all_doctors_with_review,0,len(all_doctors_with_review)-1)

    context['rec_doctor'] = all_doctors_with_review

    # context['doctors'] = get_ratings_objects(all_my_doctors, False)

    if request.user.is_authenticated and isPatient(request.user.username):
        requested_doctors1 = list(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.username), status=1).values_list('to_doctor', flat=True))
        requested_doctors2 = list(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.username), status=0).values_list('to_doctor', flat=True))
        requested_doctors = requested_doctors1 + requested_doctors2
        context['requested_doctors'] = requested_doctors


    if request.user.is_authenticated:
        context['is_patient'] = isPatient(request.user.username)

    return render(request, 'index.html', context)


def send_request(request):
    if request.method == "GET" and request.is_ajax():
        doctor_id = request.GET['doctor_id']
        doctor_id = int(doctor_id)

        thisDoct = doctors.objects.get(id=doctor_id)
        dept = thisDoct.profession

        isThisDoctor = doctors.objects.filter(email=request.user.username).exists()

        if request.user.is_superuser:
            return HttpResponse(json.dumps({'message': "You are admin, You can't send appointment request", 'status':0}), content_type="application/json")


        if isThisDoctor:
            return HttpResponse(json.dumps({'message': "You are a doctor, You can't send appointment request", 'status':0}), content_type="application/json")

        
        else:
            first_check = len(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.email), status=0))
            
            if first_check < 3:
                
                second_check = len(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.email), status=0, depart=dept))

                if second_check < 1:

                    new_appoint = appointment(sender_patient=get_patient_obj_by_email(request.user.email), to_doctor=thisDoct, depart=dept)
                    new_appoint.save()
                    return HttpResponse(json.dumps({'message': "Your request has been sent", 'status':1}), content_type="application/json")

                else:
                    new_fake = fakes(get_patient_obj_by_email(request.user.username))
                    return HttpResponse(json.dumps({'message': "Sorry You have sent request to the same department.", 'status':0}), content_type="application/json")

            else:
                return HttpResponse(json.dumps({'message': "You can't send more request to the doctos", 'status':0}), content_type="application/json")






def per_doct(request, id):

    if request.method == 'POST':
     
        doctor_id = int(request.POST['doctID'])    # post request from  profile.html form
        
        review_msg = request.POST['myReview']
        review_stars = request.POST['ratings']
        main_doc = doctors.objects.get(id=doctor_id)


        if request.user.is_superuser:
            messages.info(request, "Since you are admin, you can't post reviews.")

        
        else:
            if isPatient(request.user.username):

                author = get_patient_obj_by_email(request.user.username)

                new_review = doctor_review(author=author, review_star=review_stars, review_msg=review_msg, doctor=main_doc)
                new_review.save()

                print("review_msg =", review_msg)
                print("review_stars =", review_stars)
                print("main_doc =", main_doc.first_name)
                print("author =", author.first_name)
            else:
                messages.info(request, "Since you are a doctor, you can't post reviews. Thanks")


    doct_id = id

    context = {}

    

    this_doct = doctors.objects.get(id=doct_id)
    context['doctor'] = this_doct    # a selected doctor's attributes values are saving in context doctor 'key'
    all_reviews = doctor_review.objects.filter(doctor=this_doct)
    context['reviews'] = all_reviews    # from model 'doctor_reviews' of selected doctor's reviews are saving in context..
    context['review_view'] = True

    if request.user.is_authenticated and isPatient(request.user.username):
        requested_doctors1 = list(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.username), status=1).values_list('to_doctor', flat=True))
        requested_doctors2 = list(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.username), status=0).values_list('to_doctor', flat=True))
        requested_doctors = requested_doctors1 + requested_doctors2
        context['requested_doctors'] = requested_doctors

    if request.user.is_authenticated:
        context['is_patient'] = isPatient(request.user.username)

    return render(request, "profile.html", context)


def myProfile(request):

    if request.method == 'POST' and 'AP_ID' in request.POST and 'DATE' in request.POST:
        AP_ID = int(request.POST['AP_ID'])
        DATE = request.POST['DATE']
        TIME = request.POST['TIME']

        if appointment.objects.filter(appointment_date=DATE, appointment_time=TIME).exists():
            messages.info(request, "Sorry! this date & time is already booked for appointment")
        else:
            appoint = appointment.objects.get(id=AP_ID)
            appoint.appointment_date = DATE
            appoint.appointment_time = TIME
            appoint.status = 1
            appoint.save()

    return profile(request, request.user.id)

def reject(request, id):
    appoint = appointment.objects.get(id=id)
    appoint.status = -1
    appoint.save()

    return profile(request, request.user.id)

def completed(request, id):
    appoint = appointment.objects.get(id=id)
    appoint.status = 2
    appoint.save()

    return profile(request, request.user.id)


def check_password(request):
    if request.method == 'GET' and request.is_ajax():
        current_password = request.GET['current_password']
        new_password = request.GET['new_password']

        pointer = request.user.username

        if isPatient(pointer):
            USER = patient.objects.get(email=pointer)
        else:
            USER = doctors.objects.get(email=pointer)

        
        status = False

        if current_password==USER.password:
            status = True

            USER.password = new_password
            USER.save()


        print(current_password)
        print(new_password)

        return HttpResponse(json.dumps({'status': status}), content_type="application/json")

def profile(request, id):
    context = {}
    if request.user.is_authenticated and request.user.id == id:
        getUser = User.objects.get(id=id)
        
        

        if doctors.objects.filter(email=getUser.username).exists():
            all_doc = doctors.objects.filter(email=getUser.username)[0]
            context['is_doctor'] = True
            get_whole_info = all_doc
            print(all_doc.hospital)    #showing output dep in terminal
            context['user_info'] = get_whole_info

            
            # all_appoints = appointment.objects.filter(to_doctor=get_whole_info)
            # context['all_appoints'] = all_appoints

            if request.method == 'POST' and 'leave_date' in request.POST:
                leave_date = request.POST['leave_date']

                if doctor_leave.objects.filter(doctor=get_whole_info, leave_date=leave_date).exists():
                    messages.info(request, "You have already taken leave of this date!")
                
                
                else:
                    new_leave = doctor_leave(doctor=get_whole_info, leave_date=leave_date)
                    new_leave.save()

                    # appointment cancellation
                
                    if appointment.objects.filter(to_doctor=get_whole_info, appointment_date=leave_date, status=1).exists():
                        all_appointments_of_this_date = appointment.objects.filter(to_doctor=get_whole_info, appointment_date=leave_date)

                        for i in all_appointments_of_this_date:
                            i.status = -2
                            i.save()
                
                print('leave_date =', leave_date)

            
            context['leave_taken'] = doctor_leave.objects.filter(doctor=get_whole_info).exists()

            
            all_appoints = appointment.objects.filter(to_doctor=get_whole_info)
            context['all_appoints'] = all_appoints

        else:
            context['is_doctor'] = False
            
            all_appoints = appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.email))
            context['all_appoints'] = all_appoints

        if request.user.is_authenticated:
            context['is_patient'] = isPatient(request.user.username)


        if isPatient(request.user.email):
            context['patient_data'] = patient.objects.get(email=request.user.email)


        return render(request, "profile.html", context)
    else:
        return redirect("index")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        name = request.POST['name']
        l_name = request.POST['l_name']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        gender = request.POST['gender']
        age = request.POST['age']

        context = {
            "username":username,
            "name":name,
            "l_name":l_name,
            "email":email,
            "pass1":pass1,
            "pass2":pass2,
        }
        if pass1==pass2:
            if User.objects.filter(email=email).exists():
                print("Email already taken")
                messages.info(request, "Entered Email already in use!")
                context['border'] = "email" 
                return render(request, "signup.html", context)

            
            new_patient = patient(first_name=name, last_name=l_name, email=email, password=pass1, gender=gender, age=age)
            new_patient.save()

            user = User.objects.create_user(username=username, first_name=name, password=pass1, last_name=l_name,email=email)
            user.save()
            
            return redirect("login")
        else:
            messages.info(request, "Your pasword doesn't match!")
            context['border'] = "password"
            return render(request, "signup.html", context)


    
    return render(request, "signup.html")


def login(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, "Incorrect login details!")
            return redirect("login")
    else:
        return render(request, "login.html")

def all_doctors(request):
    context = {}
    all_my_doctors = doctors.objects.all()
    context['rec_doctor'] = get_ratings_objects(all_my_doctors, False)
    
    context['title'] = ["All Doctors", ""]

    if request.user.is_authenticated and isPatient(request.user.username):
        requested_doctors1 = list(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.username), status=1).values_list('to_doctor', flat=True))
        requested_doctors2 = list(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.username), status=0).values_list('to_doctor', flat=True))
        requested_doctors = requested_doctors1 + requested_doctors2
        context['requested_doctors'] = requested_doctors


    if request.user.is_authenticated:
        context['is_patient'] = isPatient(request.user.username)

    return render(request, 'Doctors.html', context)


def logout(request):
    auth.logout(request)
    return redirect("index")

def all_departments(request):
    context = {}
    all_depts = department.objects.all()
    context['departments'] = all_depts
    if request.user.is_authenticated:
        context['is_patient'] = isPatient(request.user.username)
    return render(request, 'Department.html', context)

def per_department(request, name):
    context = {}
    dept = department.objects.get(name=name)
    filtered_doc = doctors.objects.filter(profession=dept.related_profession_name)
    context['title'] = [dept.name, "Departments / "+dept.name]
    context['rec_doctor'] = get_ratings_objects(filtered_doc, False)

    for i in context['rec_doctor']:
        print(i.all_ratings)
        # print(i.first_name)

    if request.user.is_authenticated and isPatient(request.user.username):
        requested_doctors1 = list(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.username), status=1).values_list('to_doctor', flat=True))
        requested_doctors2 = list(appointment.objects.filter(sender_patient=get_patient_obj_by_email(request.user.username), status=0).values_list('to_doctor', flat=True))
        requested_doctors = requested_doctors1 + requested_doctors2
        context['requested_doctors'] = requested_doctors


    if request.user.is_authenticated:
        context['is_patient'] = isPatient(request.user.username)

    return render(request, 'Doctors.html', context)

def emergency(request):
    return render(request,"emergency.html")

def chat(request):
    
    current_user = request.user
    #print(current_user)

    '''
    all_chat = Chats.objects.all()
    all_chat_set = []

    for i in all_chat:
        
            if (i.sender==current_user):
                print(i.receiver)
                all_chat_set.append(i.receiver)
            elif (i.receiver==current_user):
                print(i.sender)
                all_chat_set.append(i.sender)
            
    print(all_chat_set)
    all_chat_set= list(set(all_chat_set))
    print(all_chat_set)

    '''
    #print(current_user)
    patient_obj = patient.objects.get(username=current_user)
    #print(patient_obj)

    appointment_set = appointment.objects.filter(sender_patient=patient_obj)
    #print(appointment_set)
    all_chat_set = []

    for i in appointment_set:
        

        all_chat_set.append(User.objects.get(username=i.to_doctor.email))

    
    
    print(all_chat_set)
    return render(request,'chat.html',{'all_chat_set':all_chat_set,'current_user':current_user})

def chat_pk(request,pk=None):
    all_chat = Chats.objects.all()

    current_user = request.user
    
    chat_partner  = User.objects.get(pk=pk)
    

    all_chat_set = []

    for i in all_chat:
        
            if (i.sender==current_user):
                print(i.receiver)
                all_chat_set.append(i.receiver)
            elif (i.receiver==current_user):
                print(i.sender)
                all_chat_set.append(i.sender)
            
    
    all_chat_set= list(set(all_chat_set))
    

    
    
    

    ##chat_items = all_chat.filter((Q(sender= chat_partner) & Q(receiver=current_user))) #|(Q(sender= current_user) & Q(receiver=chat_partner)) )

    
    chat_set = []
    for i in all_chat:
        if ((i.sender==chat_partner and i.receiver==current_user) or (i.sender==current_user and i.receiver==chat_partner)):
            chat_set.append(i)

    chat_set.reverse()        

    if request.method == 'POST':
        msg_obj  = Chats()
        msg = request.POST['msg']
        
        msg_obj.sender = current_user
        msg_obj.receiver = chat_partner
        msg_obj.message = msg
        msg_obj.save()
        all_chat = Chats.objects.all()
        for i in all_chat:
        
            if (i.sender==current_user):
                
                all_chat_set.append(i.receiver)
            elif (i.receiver==current_user):
                
                all_chat_set.append(i.sender)
            
        
        all_chat_set= list(set(all_chat_set))
        

    
        
    
    

        ##chat_items = all_chat.filter((Q(sender= chat_partner) & Q(receiver=current_user))) #|(Q(sender= current_user) & Q(receiver=chat_partner)) )

        
        chat_set = []
        for i in all_chat:
            if ((i.sender==chat_partner and i.receiver==current_user) or (i.sender==current_user and i.receiver==chat_partner)):
                chat_set.append(i)
                
        chat_set.reverse() 
        return render(request,'chat.html',{'chat_set':chat_set,'current_user':current_user,'all_chat_set':all_chat_set})


    else:
        return render(request,'chat.html',{'chat_set':chat_set,'current_user':current_user,'all_chat_set':all_chat_set})

def update(request):

    
    accounts = patient.objects.get(email=request.user.email)

    if request.method == 'POST':
        form = UpdateForm(request.POST, request.FILES or None, instance=request.user)
        form.actual_user = accounts
        
        print(accounts.age)
        
        if form.is_valid():
            print(form.errors)
            form.save()
            #messages.success(request, f'Your account has been updated!')
            return redirect('myProfile')
            
    else:
        form = UpdateForm(instance=accounts)
        
    context = {'media_url':settings.MEDIA_URL,'form':form,'accounts':accounts}
    
    return render(request,'edit.html',context)

def home_form(request):
        return render(request, "home_form.html")

def home_view(request):
    if request.user.is_authenticated:
        loaded_model = joblib.load("model.pkl")
        
        
        age = int(request.POST['age'])
        country = request.POST['country']
        sex = request.POST['sex']
        diffBreathe = int(request.POST['diffBreathe'])
        #sore = int(request.POST['sore'])
        bodyPain = int(request.POST['bodyPain'])
        runnyNose = int(request.POST['runnyNose'])
        nasal = int(request.POST['nasal'])
        diarrhea = int(request.POST['diarrhea'])
        #tired = int(request.POST['tired'])
        fever = int(request.POST['fever'])
        dry = float(request.POST['dry'])
        #contact = request.POST['contact']
        #severe = request.POST['severe']

        lst = [fever,bodyPain,age, runnyNose, diffBreathe]
        #lst = [age, country,sex, breathe, sore, pain, nose, nasal, diarrhea, tired, fever, dry, contact, severe]
        print(lst)
        df =pd.DataFrame([lst])
        df.columns=['fever','bodyPain','age', 'runnyNose', 'diffBreathe']
        #df.columns =['age','country','sex',' breathe', 'sore', 'pain', 'nose', 'nasal', 'diarrhea', 'tired', 'fever', 'dry', 'contact', 'severe']
        result= loaded_model.predict_proba(df)[0][1]
        print(result)
        context={"result":result}
        df = pd.read_csv('data.csv')
        if result <0.5:
            return render(request, "mild.html",context)
            

        elif result >=0.3 and result < 0.7:
            return per_department(request,"Covid Team")
            #return render(request, "doctor/8",context)

        else:
            #return render(request, "severe.html",context)
            return per_department(request,"Covid Team")
        
    else:
        return redirect(reverse('login'))