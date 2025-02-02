from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from . models import *






#AI Code explainer

import base64
import requests
import re
from huggingface_hub import InferenceClient

client = InferenceClient(api_key="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")

def codeexplainer(request):
    if request.method=="POST":
        text=request.POST.get('text')
        messages = [
            {
                "role": "user",
                "content": text
            }
        ]

        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=messages,
            max_tokens=500
        )
        result = completion.choices[0].message['content'] if isinstance(completion.choices[0].message, dict) else completion.choices[0].message

        # Step 5: Perform regex operations to clean the result
        if isinstance(result, str):
            # Remove LaTeX math expressions (e.g., \(...\), \[...\])
            content_normal = re.sub(r'\\[(){}\[\]]|\\[a-zA-Z]+', '', result)

            # Remove extra line breaks
            content_normal = re.sub(r'\n+', ' ', content_normal)

            print('Result Is:', content_normal)
        else:
            print("Result is not a string.")
        msg=content_normal
        print(msg,'code')
        return render(request,'ai.html',{'msg':msg})
    else:
        return render(request,'ai.html')

    
def mathexplainer(request):
    content_normal=None
    if request.method=="POST":
        text=request.POST.get('text')
        math_expression_pattern = r'^[\d+\-*/().\s]+$'

        if re.match(math_expression_pattern, text):
            messages = [
                {
                    "role": "user",
                    "content": text
                }
            ]

            completion = client.chat.completions.create(
                model="Qwen/Qwen2.5-Coder-32B-Instruct",
                messages=messages,
                max_tokens=500
            )

            result = completion.choices[0].message['content'] if isinstance(completion.choices[0].message, dict) else completion.choices[0].message

            if isinstance(result, str):
        # Remove LaTeX math expressions (e.g., \(...\), \[...\])
                content_normal = re.sub(r'\\[(){}\[\]]|\\[a-zA-Z]+', '', result)

                # Remove extra line breaks
                content_normal = re.sub(r'\n+', ' ', content_normal)

                print('Result Is:', content_normal)
            else:
                print("Result is not a string.")
        else:
            print("Please enter a valid mathematical query.")
        msg=content_normal
        print(msg,'code')
        return render(request,'math.html',{'msg':msg})
    else:
        return render(request,'math.html')
    





# Create your views here.
def index(request):
    return render(request,'index.html') 


def studentindex(request):
    return render(request,'studentindex.html')

def teacherindex(request):
    return render(request,'teacherindex.html')

# Student details

def register(request):
    if request.method=='POST':
        fname=request.POST.get('Firstname')
        lname=request.POST.get('Lastname')
        rollno=request.POST.get('RollNumber')
        DOB=request.POST.get('DOB')
        mail=request.POST.get('Email')
        image=request.FILES.get('image')
        passw=request.POST.get('Password')
        if Register.objects.filter(RollNumber=rollno).exists():
            alert="<script>alert('Roll Number already exists');window.location.href='/login/';</script>"
            return HttpResponse(alert)
        Register(Firstname=fname,Lastname=lname,RollNumber=rollno,DOB=DOB,Email=mail,Password=passw,Image=image).save()
        return redirect('login')
    return render(request,'register.html')

def login(request):
    if request.method=="POST":
        RollNumber=request.POST.get('rollnumber')
        password=request.POST.get('password')
        try:
            user=Register.objects.get(RollNumber=RollNumber,Password=password)
            semail=user.RollNumber
            request.session['rollnumber']=semail
            return render(request,'studentindex.html')
        except:
            msg="invalid roll number or password"
            return render(request,'login.html',{"msg":msg})
    return render(request,'login.html')
    

def profile(request):
    if 'rollnumber' in request.session:
        num=request.session['rollnumber']
        usr=Register.objects.get(RollNumber=num)
    return render(request,'profile.html',{'usr':usr}) 

def edit_profile(request,uid):
# mail=request.session['email']
    edit=Register.objects.get(id=uid)
    if request.method=='POST':
        fname=request.POST.get('fname')
        lname=request.POST.get('lname')
        rollno=request.POST.get('rollno')
        image=request.FILES.get('image')
        email=request.POST.get('email')
        dob=request.POST.get('dob')
        edit=Register.objects.get(id=uid)
        edit.Firstname=fname
        edit.Lastname=lname
        edit.Email=email
        edit.RollNumber=rollno
        edit.DOB=dob
        print(image)
        if image is not None:
            edit.Image=image    
        im=edit.Image
        print(im)
        edit.Image=im
        print(edit.Image)
        edit.save()
        return redirect('profile') 
    return render(request,'edit_profile.html',{'edit':edit})

def logout(request):
    request.session.flush()
    return redirect('index')


# Teacher details


def teacherreg(request):
    if request.method=='POST':
        fname=request.POST.get('Firstname')
        lname=request.POST.get('Lastname')
        ID=request.POST.get('ID')
        DOB=request.POST.get('DOB')
        mail=request.POST.get('Email')
        image=request.FILES.get('image')
        passw=request.POST.get('Password')
        if Teacherreg.objects.filter(IDNumber=ID).exists():
            alert="<script>alert('ID Number already exists');window.location.href='/teacherlogin/';</script>"
            return HttpResponse(alert)
        Teacherreg(Firstname=fname,Lastname=lname,IDNumber=ID,DOB=DOB,Email=mail,Password=passw,Image=image,status='applied').save()
        return render(request,'index.html')
    return render(request,'teacherreg.html')



from django.shortcuts import render, redirect
from .models import Teacherreg

def teacherlogin(request):
    if request.method == "POST":
        IDNumber = request.POST.get('ID')
        password = request.POST.get('password')

        try:
            user = Teacherreg.objects.get(IDNumber=IDNumber)
            # Check if the password is correct
            if user.Password == password:
                # Check if the user is approved
                if user.status == 'approved':
                    # Store IDNumber in session
                    request.session['IDNumber'] = user.IDNumber
                    return render(request,'teacherindex.html')
                else:
                    msg = "Your application has not been approved yet."
            else:
                msg = "Invalid ID number or password."
        except Teacherreg.DoesNotExist:
            msg = "Invalid ID number or password."

        return render(request, 'teacherlogin.html', {"msg": msg})

    return render(request, 'teacherlogin.html')

    


def teacherprofile(request):
    if 'IDNumber' in request.session:
        num=request.session['IDNumber']
        usr=Teacherreg.objects.get(IDNumber=num)
    return render(request,'teacherprofile.html',{'usr':usr}) 

def T_edit_profile(request, id):
    teacher = get_object_or_404(Teacherreg, id=id)

    if request.method == 'POST':
        teacher.Firstname = request.POST.get('Firstname', teacher.Firstname)
        teacher.Lastname = request.POST.get('Lastname', teacher.Lastname)
        teacher.DOB = request.POST.get('DOB', teacher.DOB)
        teacher.Email = request.POST.get('Email', teacher.Email)

        if 'Image' in request.FILES:
            teacher.Image = request.FILES['Image']

        teacher.save()
        return redirect('teacherprofile')  

    return render(request, 'teacherprofile.html', {'usr': teacher})


# def upload(request):
#     if 'IDNumber' in request.session:
#         num=request.session['IDNumber']
#         usr=Teacherreg.objects.get(IDNumber=num)
#         if request.method=='POST':
#             title=request.POST.get('title')
#             description=request.POST.get('description')






# admin starts here >>>>>>>>>>

def adminhome(request):
     return render(request,'adminhome.html')




# def addteacher(request):
#     if request.method=='POST':
#         fname=request.POST.get('Firstname')
#         lname=request.POST.get('Lastname')
#         ID=request.POST.get('ID')
#         DOB=request.POST.get('DOB')
#         mail=request.POST.get('Email')
#         image=request.FILES.get('image')
#         addteachers=Teacherreg(
#             Firstname=fname,
#             Lastname=lname,
#             IDNumber=ID,
#             DOB=DOB,
#             Email=mail,
#             Image=image,
#             status='applied'
#         )
#         addteachers.save()
#         return redirect(adminhomepg)
#     return render(request,'addteacher.html')


    #     if addteacher.objects.filter(IDNumber=ID).exists():
    #         alert="<script>alert('ID Number already exists');window.location.href='/teacherlogin/';</script>"
    #         return HttpResponse(alert)
    #     addteacher(Firstname=fname,Lastname=lname,IDNumber=ID,DOB=DOB,Email=mail,Image=image).save()
    #     return redirect('adminindex')
    # return render(request,'adminindex.html')



#student list viewed by admin
def admin_studentlist(request):
    data=Register.objects.all()
    return render(request,'studentlist.html',{'data':data})

#student delete
def student_delete(request,sid):
    student=Register.objects.get(id=sid)
    student.delete()
    return redirect('studentlist')


def update_status(request):
    if request.method == 'POST':
        update_id = request.POST.get('update_id')
        status = request.POST.get('status')
        if status in['approved', 'rejected']:
            update=get_object_or_404(Teacherreg,id=update_id)
            update.status = status
            update.save()
        return redirect('teacherlist')


#teacher list viewed by admin
def admin_teacherlist(request):
    data=Teacherreg.objects.all()
    return render(request,'teacherlist.html',{'data':data})


#teacher delete by admin
def teacher_delete(request,sid):
    student=Teacherreg.objects.get(id=sid)
    student.delete()
    return redirect('teacherlist')


#admin login
def admin_login(request):
    if request.method=='POST':
        uemail=request.POST.get('email')
        passw=request.POST.get('password')
        u='admin@gmail.com'
        p='admin'
        if uemail==u:
            if passw==p:
                return render(request,'adminhome.html')
    return render(request,'adminlogin.html')


from django.http import HttpResponse
from django.shortcuts import render
from .models import Feedback

def feedback(request):
    if request.method == "POST":
        # Get form data
        feedback_text = request.POST.get('feedback_text')
        rating = request.POST.get('rating')
        email = request.POST.get('email')  # Capture the email
        
        # Check if the required fields are provided
        if not feedback_text or not rating:
            alert_message = """
                <script>
                    alert('Please fill in all required fields.');
                    window.location.href='/feedback_rate';
                </script>
            """
            return HttpResponse(alert_message)
        
        # Validate rating value (should be between 1 and 5)
        try:
            rating = int(rating)
            if rating not in [1, 2, 3, 4, 5]:
                raise ValueError("Invalid rating value")
        except (ValueError, TypeError):
            alert_message = """
                <script>
                    alert('Invalid rating value. Please select a valid rating.');
                    window.location.href='/feedback_rate';
                </script>
            """
            return HttpResponse(alert_message)
        
        # Create the Feedback instance and save it to the database
        feedback_instance = Feedback(
            feedback_text=feedback_text,
            rating=rating,
            email=email  # Save the email as well
        )
        feedback_instance.save()

        # Show success message with JavaScript alert
        success_message = """
            <script>
                alert('Feedback submitted successfully!');
                window.location.href='/feedback_rate';
            </script>
        """
        return HttpResponse(success_message)
    
    # Render the form for GET requests
    return render(request, 'feedback_rate.html')

#feedbacklist on admin interface
def admin_feedbacklist(request):
    feedlist=Feedback.objects.all()
    return render(request,'feedbacklist.html',{'feedlist':feedlist})

def feedback_delete(request,fid):
    feedlist=Feedback.objects.get(id=fid)
    feedlist.delete()
    return redirect('feedbacklist')







# Student 

def view_attendance(request):
    if 'rollnumber' in request.session:
        student = Register.objects.get(RollNumber=request.session['rollnumber'])
        attendance_records = Attendance.objects.filter(student=student)
        return render(request, 'student_attendance.html', {'attendance_records': attendance_records})
    return redirect('login')


def upload_assignment(request):
    if 'rollnumber' in request.session:
        student = Register.objects.get(RollNumber=request.session['rollnumber'])
        if request.method == 'POST':
            title = request.POST.get('title')
            file = request.FILES.get('file')
            Assignment(student=student, title=title, file=file).save()
            return HttpResponse("<script>alert('Assignment uploaded successfully');window.location.href='/studentindex/';</script>")
        return render(request, 'upload_assignment.html')
    return redirect('login')



def view_results(request):
    if 'rollnumber' in request.session:
        student = Register.objects.get(RollNumber=request.session['rollnumber'])
        results = Result.objects.filter(student=student)
        return render(request, 'student_results.html', {'results': results})
    return redirect('login')


def view_notes(request):
    note = uploadnotes.objects.all() 

    return render(request, 'view_notes.html', {'note': note})



##teacher side


def mark_attendance(request):
    students = Register.objects.all()  
    if request.method == 'POST':
        rollnumber = request.POST.get('rollnumber')
        date = request.POST.get('date')
        status = request.POST.get('status')
        try:
            student = Register.objects.get(RollNumber=rollnumber)
            Attendance(student=student, date=date, status=status).save()
            return HttpResponse("<script>alert('Attendance marked successfully');window.location.href='/teacherindex/';</script>")
        except Register.DoesNotExist:
            return HttpResponse("<script>alert('Student not found');window.location.href='/teacherindex/';</script>")
    
    return render(request, 'mark_attendance.html', {'students': students})



def add_result(request):
    students = Register.objects.all()
    results = Result.objects.all() 
    if request.method == 'POST':
        rollnumber = request.POST.get('rollnumber')
        subject = request.POST.get('subject')
        marks = request.POST.get('marks')
        total_marks = request.POST.get('total_marks')
        try:
            student = Register.objects.get(RollNumber=rollnumber)
            Result(student=student, subject=subject, marks=marks, total_marks=total_marks).save()
            return HttpResponse("<script>alert('Result added successfully');window.location.href='/teacherindex/';</script>")
        except Register.DoesNotExist:
            return HttpResponse("<script>alert('Student not found');window.location.href='/teacherindex/';</script>")
    
    return render(request, 'add_result.html', {'students': students, 'results': results})


def upload_notes(request):
    notes = uploadnotes.objects.all()  
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        uploadnotes(title=title, files=file).save()
        return HttpResponse("<script>alert('Notes uploaded successfully');window.location.href='/upload/';</script>")
    
    return render(request, 'upload_notes.html', {'notes': notes})




def assignment_v(request):
    assignments = Assignment.objects.all() 
    return render(request, 'view_assign.html', {'assignments': assignments}) 

