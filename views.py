from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, render,redirect,HttpResponse
from . models import *






#AI Code explainer

import base64
import requests
import re
from huggingface_hub import InferenceClient

client = InferenceClient(api_key="")#lama api key from hugging face

import easyocr
import re
from groq import Groq
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings


client = Groq(api_key=settings.LAMA_API_KEY)


def detect_language(code_text):
    """
    Basic language detection based on common patterns
    """
    code_lower = code_text.lower()
    patterns = {
        'python': (r'\bdef\b|\bclass\b|\bimport\b|\bfrom\b.*\bimport\b', 'python'),
        'javascript': (r'\bfunction\b|\bconst\b|\blet\b|\bvar\b|\=\>', 'javascript'),
        'java': (r'\bpublic\b.*\bclass\b|\bprivate\b|\bprotected\b', 'java'),
        'cpp': (r'\#include\b|\bstd::\b|\bint\smain\(', 'cpp'),
        'typescript': (r'\binterface\b|\btype\b|\bnamespace\b', 'typescript'),
        'php': (r'\<\?php|\becho\b|\bfunction\b', 'php'),
        'ruby': (r'\bdef\b|\bclass\b|\bend\b|\bmodule\b', 'ruby'),
        'go': (r'\bfunc\b|\bpackage\s+main\b', 'go'),
    }
    
    for lang, (pattern, class_name) in patterns.items():
        if re.search(pattern, code_text):
            return lang, class_name
    
    return 'unknown', 'plaintext'

def codeexplainer(request):
    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        code_image = request.FILES.get('code_image')
        request_type = request.POST.get('request_type', 'explain')  # 'explain' or 'generate'
        preferred_language = request.POST.get('preferred_language', '')
        
        try:
            if request_type == 'explain' and code_image and isinstance(code_image, UploadedFile):
                # Process image input for code explanation
                reader = easyocr.Reader(['en'])
                image_content = code_image.read()
                extracted_text = reader.readtext(image_content)
                code_text = ' '.join(text for _, text, _ in extracted_text)
                if not code_text:
                    return render(request, 'code_helper.html', 
                                {'error': 'Could not extract code from image'})
                
                lang, prism_class = detect_language(code_text)
                query = f"""Please analyze this {lang} code and provide:
                    1. A detailed explanation of what the code does
                    2. Any potential improvements or best practices
                    3. If there are any potential issues or bugs
                    4. Example usage if applicable

                    Code:
                    {code_text}"""
            
            elif request_type == 'explain' and text:
                # Process text input for code explanation
                code_text = text
                lang, prism_class = detect_language(code_text)
                query = f"""Please analyze this {lang} code and provide:
                    1. A detailed explanation of what the code does
                    2. Any potential improvements or best practices
                    3. If there are any potential issues or bugs
                    4. Example usage if applicable

                    Code:
                    {code_text}"""
            
            elif request_type == 'generate' and text:
                # Process code generation request
                lang = preferred_language.lower() if preferred_language else 'python'
                prism_class = lang
                query = f"""Please write code in {lang} that accomplishes the following:
                    {text}

                    Please provide:
                    1. Complete, working code solution
                    2. Brief explanation of how the code works
                    3. Example usage
                    4. Any important notes or considerations"""
            else:
                return render(request, 'code_helper.html', 
                            {'error': 'Please provide a valid request'})

            messages = [
                {
                    "role": "user",
                    "content": query
                }
            ]

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1500,
                top_p=1,
                stream=False
            )

            result = completion.choices[0].message.content

            if isinstance(result, str):
                # Split response into explanation and code sections
                sections = result.split('```')
                
                explanation = sections[0].strip()
                
                # Extract code blocks with language info
                code_blocks = []
                for i in range(1, len(sections), 2):
                    if i < len(sections):
                        code = sections[i].strip()
                        # Remove language identifier if present
                        if code.split('\n')[0] in ['python', 'javascript', 'java', 'cpp', 'typescript', 'php', 'ruby', 'go']:
                            code = '\n'.join(code.split('\n')[1:])
                        code_blocks.append({
                            'code': code,
                            'language': prism_class
                        })
                
                context = {
                    'explanation': explanation,
                    'code_blocks': code_blocks,
                    'original_code': code_text if request_type == 'explain' else None,
                    'language': prism_class,
                    'detected_lang': lang.title(),
                    'request_type': request_type
                }
                
                return render(request, 'ai.html', context)
            else:
                return render(request, 'ai.html', 
                            {'error': 'Could not process the response'})

        except Exception as e:
            return render(request, 'ai.html', 
                        {'error': f'An error occurred: {str(e)}'})

    return render(request, 'ai.html')

# def codeexplainer(request):
#     if request.method=="POST":
#         text=request.POST.get('text')
#         messages = [
#             {
#                 "role": "user",
#                 "content": text
#             }
#         ]

#         completion = client.chat.completions.create(
#             model="Qwen/Qwen2.5-Coder-32B-Instruct",
#             messages=messages,
#             max_tokens=500
#         )
#         result = completion.choices[0].message['content'] if isinstance(completion.choices[0].message, dict) else completion.choices[0].message

#         # Step 5: Perform regex operations to clean the result
#         if isinstance(result, str):
#             # Remove LaTeX math expressions (e.g., \(...\), \[...\])
#             content_normal = re.sub(r'\\[(){}\[\]]|\\[a-zA-Z]+', '', result)

#             # Remove extra line breaks
#             content_normal = re.sub(r'\n+', ' ', content_normal)

#             print('Result Is:', content_normal)
#         else:
#             print("Result is not a string.")
#         msg=content_normal
#         print(msg,'code')
#         return render(request,'ai.html',{'msg':msg})
#     else:
#         return render(request,'ai.html')

# import easyocr  
# def mathexplainer(request):
#     content_normal=None
#     if request.method=="POST":
#         text=request.POST.get('text')
#         im=request.FILES.get('im')
#         if im:
#             print("59")
#             reader = easyocr.Reader(['en'])
#             tex = reader.readtext(im)
#             math_expression_pattern = r'^[\d+\-*/().\s]+$'
#             prg =''
#             for (bbox, string,confidence) in tex:
#                 prg += string
#             print("fr",prg)
#             tex="solve the problem"+prg
#             if re.match(math_expression_pattern, text):
#                 messages = [
#                     {
#                         "role": "user",
#                         "content": tex
#                     }
#                 ]

#                 completion = client.chat.completions.create(
#                     model="Qwen/Qwen2.5-Coder-32B-Instruct",
#                     messages=messages,
#                     max_tokens=500
#                 )

#                 result = completion.choices[0].message['content'] if isinstance(completion.choices[0].message, dict) else completion.choices[0].message
#                 if isinstance(result, str):
#                         # Remove LaTeX math expressions (e.g., \(...\), \[...\])
#                     content_normal = re.sub(r'\\[(){}\[\]]|\\[a-zA-Z]+', '', result)

#                         # Remove extra line breaks
#                     content_normal = re.sub(r'\n+', ' ', content_normal)

#                     print('Result Is:', content_normal)
#                 else:
#                     print("Result is not a string.")
#             else:
#                 print("Please enter a valid mathematical query.")
#                 msg=content_normal
#                 print(msg,'code')
#                 return render(request,'math.html',{'msg':msg})
#         else:
#             print("gth")
#             math_expression_pattern = r'^[\d+\-*/().\s]+$'

#             if re.match(math_expression_pattern, text):
#                     messages = [
#                         {
#                             "role": "user",
#                             "content": text
#                         }
#                     ]

#                     completion = client.chat.completions.create(
#                         model="Qwen/Qwen2.5-Coder-32B-Instruct",
#                         messages=messages,
#                         max_tokens=500
#                     )

#                     result = completion.choices[0].message['content'] if isinstance(completion.choices[0].message, dict) else completion.choices[0].message
#                     if isinstance(result, str):
#                         # Remove LaTeX math expressions (e.g., \(...\), \[...\])
#                         content_normal = re.sub(r'\\[(){}\[\]]|\\[a-zA-Z]+', '', result)

#                         # Remove extra line breaks
#                         content_normal = re.sub(r'\n+', ' ', content_normal)

#                         print('Result Is:', content_normal)
#                     else:
#                         print("Result is not a string.")
#             else:
#                 print("Please enter a valid mathematical query.")
#                 msg=content_normal
#                 print(msg,'code')
#                 return render(request,'math.html',{'msg':msg})
#     else:
#         return render(request,'math.html')
    

import easyocr
import re
from groq import Groq
from django.core.files.uploadedfile import UploadedFile

def format_math_response(response):
    """
    Formats the AI response to make step-by-step math explanations clearer.
    """
    # Add new lines between steps
    formatted_response = re.sub(r'(\d+)\.', r'\n**Step \1:**', response)
    
    # Ensure proper spacing around operators
    formatted_response = re.sub(r'(\d)([+\-*/])(\d)', r'\1 \2 \3', formatted_response)

    return formatted_response

def mathexplainer(request):
    content_normal = None
    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        image_file = request.FILES.get('im')
        
        # Input validation
        if not text and not image_file:
            return render(request, 'math.html', {'msg': 'Please provide either text or an image'})
        
        try:
            # Handle image input
            if image_file and isinstance(image_file, UploadedFile):
                reader = easyocr.Reader(['en'])
                # Read the image file content
                image_content = image_file.read()
                
                # Process with EasyOCR
                tex = reader.readtext(image_content)
                extracted_text = ' '.join(string for _, string, _ in tex)
                query_text = f"solve this mathematical problem: {extracted_text},note one thing if the query not related to maths say dont know"
                
                # Validate the extracted text
                if not extracted_text:
                    return render(request, 'math.html', {'msg': 'Could not extract text from the image'})
            
            # Handle text input
            elif text:
                # Validate mathematical expression
                math_expression_pattern = r'^[\d+\-*/().\s]+$'
                if not re.match(math_expression_pattern, text):
                    return render(request, 'math.html', {'msg': 'Please enter a valid mathematical expression'})
                query_text = text
            
            # Process with Groq API
            messages = [
                {
                    "role": "user",
                    "content": query_text
                }
            ]

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_completion_tokens=500,
                top_p=1,
                stream=False
            )

            # Process the response
            result = completion.choices[0].message.content
            if isinstance(result, str):
                # Clean up the response
                content_normal = re.sub(r'\\[(){}\[\]]|\\[a-zA-Z]+', '', result)
                content_normal = re.sub(r'\n+', ' ', content_normal)
                content_normal = format_math_response(content_normal)
            else:
                content_normal = "Error: Unable to process the result"

        except Exception as e:
            content_normal = f"An error occurred: {str(e)}"
            print(f"Error processing request: {str(e)}")

        return render(request, 'math.html', {'msg': content_normal})
    
    # GET request - just show the form
    return render(request, 'math.html')



# Create your views here.
def index(request):
    return render(request,'index.html') 


def studentindex(request):
    return render(request,'studentindex.html')

def teacherindex(request):
    return render(request,'teacherindex.html')

# Student details

from django.shortcuts import render, redirect

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Register

def register(request):
    if request.method == "POST":
        fname = request.POST.get("Firstname")
        lname = request.POST.get("Lastname")
        rollno = request.POST.get("RollNumber")
        DOB = request.POST.get("DOB")
        mail = request.POST.get("Email")
        image = request.FILES.get("image")
        passw = request.POST.get("Password")
        sem = request.POST.get("sem")
        courses = request.POST.get("courses")  # Get selected course (single ID)

        # Check if the roll number already exists
        if Register.objects.filter(RollNumber=rollno).exists():
            return HttpResponse("<script>alert('Roll Number already exists');window.location.href='/register/';</script>")

        # Fetch the selected course
       

        # Create and save the student
        student = Register(
            Firstname=fname,
            Lastname=lname,
            RollNumber=rollno,
            DOB=DOB,
            Email=mail,
            Password=passw,
            sem=sem,
            Image=image,
            courses=courses  # Assigning a single course
        )
        student.save()

        return redirect("login")  # Redirect after successful registration

    # Fetch all courses to display in the registration form
    
    return render(request, "register.html")


def login(request):
    if request.method=="POST":
        RollNumber=request.POST.get('rollnumber')
        password=request.POST.get('password')
        try:
            user=Register.objects.get(RollNumber=RollNumber,Password=password)
            semail=user.RollNumber
            request.session['rollnumber']=semail
            return redirect('studenindex') 
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
        sem = request.POST.get("sem")
        courses = request.POST.get("courses") 
        edit=Register.objects.get(id=uid)
        edit.Firstname=fname
        edit.Lastname=lname
        edit.Email=email
        edit.RollNumber=rollno
        edit.DOB=dob
        edit.sem=sem
        edit.courses=courses
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
    course = request.GET.get('course')
    sem = request.GET.get('sem')

    data = Register.objects.all()

    if course:
        data = data.filter(courses=course)
    if sem:
        data = data.filter(sem=sem)

    return render(request, 'studentlist.html', {'data': data})

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


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Register, Result, uploadnotes

def view_results(request):
    if 'rollnumber' in request.session:
        student = Register.objects.get(RollNumber=request.session['rollnumber'])
        results = Result.objects.filter(student=student)

        # Get available semesters for filtering
        semesters = Result.objects.filter(student=student).values_list('semester', flat=True).distinct()

        # Apply filters if selected
        semester_filter = request.GET.get('semester')

        if semester_filter:
            results = results.filter(semester=semester_filter)

        return render(request, 'student_results.html', {
            'results': results,
            'semesters': semesters
        })
    
    return redirect('login')


def view_notes(request):
    if 'rollnumber' in request.session:
        student = Register.objects.get(RollNumber=request.session['rollnumber'])
        
        # Get all notes for the student's course and semester
        notes = uploadnotes.objects.filter(courses=student.courses, sem=student.sem)

        return render(request, "view_notes.html", {"notes": notes})

    return redirect("login")



##teacher side
from django.shortcuts import render
from .models import  Register, Attendance
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


def mark_attendance(request):
    if request.method == "POST":
        rollnumber = request.POST.get("rollnumber")
        date = request.POST.get("date")
        status = request.POST.get("status")

        try:
            student = Register.objects.get(RollNumber=rollnumber)
            Attendance.objects.create(student=student, date=date, status=status)
            return HttpResponse("<script>alert('Attendance marked successfully');window.location.href='/teacherindex/';</script>")
        except Register.DoesNotExist:
            return HttpResponse("<script>alert('Student not found');window.location.href='/teacherindex/';</script>")

    # Fetch all unique course names for the dropdown
    courses = Register.objects.values_list("courses", flat=True).distinct()
    return render(request, "mark_attendance.html", {"courses": courses})
from django.http import JsonResponse  # Add this import

@csrf_exempt
def get_students(request):
    """Fetch students dynamically based on selected course and semester"""
    if request.method == "POST":
        print("POST Data:", request.POST)
        course_name = request.POST.get("course").strip()  # Course stored as text
        semester = request.POST.get("semester").strip()
        print(f"Filtering for Course: {course_name}, Semester: {semester}")

        # Filter students using the course name and semester
        students = Register.objects.filter(courses=course_name, sem=semester).values("RollNumber", "Firstname", "Lastname")
        print("Students Found:", list(students))
        
        return JsonResponse(list(students), safe=False)



from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Register, Result

@csrf_exempt
def get_students_for_result(request):
    """Fetch students dynamically based on selected course and semester"""
    if request.method == "POST":
        course_name = request.POST.get("course")  # Course stored as text
        semester = request.POST.get("semester")
        print("Course:", course_name)  # Debugging
        print("Semester:", semester)

        if not course_name or not semester:
            return JsonResponse({"error": "Invalid data"}, status=400)

        students = Register.objects.filter(courses=course_name.strip(), sem=str(semester)).values("RollNumber", "Firstname", "Lastname")

        return JsonResponse(list(students), safe=False)

def add_result(request):
    courses = Register.objects.values_list("courses", flat=True).distinct()  # Get unique courses
    results = Result.objects.all()

    if request.method == 'POST':
        rollnumber = request.POST.get('rollnumber')
        course_name = request.POST.get('courses')
        semester = request.POST.get('semester')
        subject = request.POST.get('subject')
        marks = request.POST.get('marks')
        total_marks = request.POST.get('total_marks')

        try:
            student = Register.objects.get(RollNumber=rollnumber)
            
            Result.objects.create(
                student=student,
                courses=course_name,
                semester=semester,
                subject=subject,
                marks=marks,
                total_marks=total_marks
            )
            return HttpResponse("<script>alert('Result added successfully');window.location.href='/teacherindex/';</script>")
        except Register.DoesNotExist:
            return HttpResponse("<script>alert('Student not found');window.location.href='/teacherindex/';</script>")

    return render(request, 'add_result.html', {'courses': courses, 'results': results})

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import uploadnotes, Register
from django.views.decorators.csrf import csrf_exempt

def upload_notes(request):
    courses = ["BBA", "BSc.ComputerScience", "BCOM", "BSc.Chemistry", "BSc.Zoology", "BSc.Botany"]
    notes = uploadnotes.objects.all()  # Fetch all notes

    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        course = request.POST.get('course')
        sem = request.POST.get('sem')
        subject = request.POST.get('subject')

        # Save the uploaded note
        uploadnotes.objects.create(title=title, files=file, courses=course, sem=sem, subject=subject)

        return HttpResponse("<script>alert('Notes uploaded successfully');window.location.href='/upload/';</script>")

    return render(request, 'upload_notes.html', {'notes': notes, 'courses': courses})


@csrf_exempt
def get_students_for_notes(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        sem = request.POST.get('semester')
        
        students = Register.objects.filter(course=course, semester=sem).values('RollNumber', 'Firstname', 'Lastname')
        return JsonResponse(list(students), safe=False)



from django.shortcuts import render
from .models import Assignment

def assignment_v(request):
    query = request.GET.get('q', '') 
    assignments = Assignment.objects.all()
    if query:
        assignments = assignments.filter(title__icontains=query)  
    return render(request, 'view_assign.html', {'assignments': assignments, 'query': query})


def update_assignment_status(request, pk, status):
    assignment = get_object_or_404(Assignment, pk=pk)
    if status in ['Accepted', 'Rejected']:
        assignment.accept_reject = status
        assignment.save()
        return JsonResponse({'success': True, 'status': assignment.accept_reject})
    return JsonResponse({'success': False})



from django.shortcuts import render, redirect
from .models import Notification,Register
from django.shortcuts import render, redirect
from .models import Notification, Register
from django.core.mail import send_mail
from django.conf import settings
def create_notification(request):
    if request.method == "POST":
        title = request.POST.get('title')
        messages = request.POST.get('messages')
        type = request.POST.get('type')
        course = request.POST.get('course')
        semester = request.POST.get('sem')

        # Create and save notification
        notification = Notification.objects.create(
            title=title,
            messages=messages,
            type=type
        )

        # Filter recipients based on course and semester
        recipients = Register.objects.filter(
            courses=course, sem=semester
        ).values_list('Email', flat=True)
        email_list = list(filter(None, recipients))  # Remove empty emails

        if email_list:
            subject = f"New Notification: {title}"
            message = messages
            from_email = settings.EMAIL_HOST_USER
            
            send_mail(
                subject,
                message,
                from_email,
                email_list,
                fail_silently=False,
            )
        
        notification.save()
        return redirect('view_notifications')

    return render(request, 'create_notification.html')


def view_notifications(request):
    n=Notification.objects.all()
    return render(request,'view_notifications.html',{'n':n})


def view_nstudent(request):
    n=Notification.objects.all()
    return render(request,'view_nstudent.html',{'n':n})

import os
from django.shortcuts import render
from django.http import JsonResponse
from groq import Groq



def chat(request):
    result = None
    if request.method == 'POST':
        query = request.POST.get('prompt')
        if query:
            try:
                messages = [
                    {
                        "role": "user",
                        "content": query
                    }
                ]
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_completion_tokens=1500,
                    top_p=1,
                    stream=False
                )
                result = completion.choices[0].message.content
            except Exception as e:
                result = f"Error: {str(e)}"
    
    return render(request, 'chat.html', {'result': result})

def schat(request):
    result = None
    if request.method == 'POST':
        query = request.POST.get('prompt')
        if query:
            try:
                messages = [
                    {
                        "role": "user",
                        "content": query
                    }
                ]
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_completion_tokens=1500,
                    top_p=1,
                    stream=False
                )
                result = completion.choices[0].message.content
            except Exception as e:
                result = f"Error: {str(e)}"
    
    return render(request, 'schat.html', {'result': result})

