from django.db import models

# Create your models here.
from django.db import models


    
class Register(models.Model):      
    Firstname=models.CharField(max_length=20,blank=True,null=True)
    Lastname=models.CharField(max_length=20,blank=True,null=True)
    RollNumber=models.CharField(max_length=10,unique=True,null=True,blank=True)
    DOB=models.DateField(blank=True,null=True)
    Email=models.EmailField(unique=True,null=True,blank=True)
    Password=models.CharField(max_length=20,blank=True,null=True)
    Image=models.ImageField(upload_to='student/',blank=True,null=True)
    courses = models.CharField(max_length=25,null=True,blank=True)
    sem = models.IntegerField(blank=True,null=True)
    def __str__(self):
        return str(self.Firstname)
    

    
class Teacherreg(models.Model):
    STATUS=(
        ('applied','Applied'),
        ('approved','Approved'),
        ('rejected','Rejected'),
    )
    Firstname=models.CharField(max_length=20,blank=True,null=True)
    Lastname=models.CharField(max_length=20,blank=True,null=True)
    IDNumber=models.CharField(max_length=10,unique=True,null=True,blank=True)
    DOB=models.DateField(blank=True,null=True)
    Email=models.EmailField(unique=True,null=True,blank=True)
    Password=models.CharField(max_length=20,blank=True,null=True)
    Image=models.ImageField(upload_to='Teacher/',blank=True,null=True)
    status=models.CharField(max_length=20,choices=STATUS,default='applied')
    def __str__(self):
        return str(self.Firstname)


class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    
    feedback_text = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    email=models.EmailField(unique=True,null=True,blank=True)


    def __str__(self):
        return self.email

class uploadnotes(models.Model):
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    files=models.FileField(upload_to='upload/',blank=True,null=True)
    courses = models.CharField(max_length=25,null=True,blank=True)
    sem = models.IntegerField(blank=True,null=True)
    subject = models.CharField(max_length=25,null=True,blank=True)



class Attendance(models.Model):
    student = models.ForeignKey(Register, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=False)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"{self.student.Firstname} - {self.date} - {self.status}"

class Assignment(models.Model):
    student = models.ForeignKey(Register, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='assignments/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    accept_reject = models.CharField(
        max_length=10, 
        choices=[('Accepted', 'Accepted'), ('Rejected', 'Rejected')], 
        default='Pending'
    )

    def __str__(self):
        return f"{self.title} - {self.student.Firstname} - {self.accept_reject}"
    def __str__(self):
        return f"{self.student.Firstname} - {self.title}"

class Result(models.Model):
    student = models.ForeignKey(Register, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks = models.IntegerField()
    total_marks = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    courses = models.CharField(max_length=25,null=True,blank=True)
    semester = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return f"{self.student.Firstname} - {self.subject} - {self.marks}/{self.total_marks}"


from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    messages = models.TextField(null=True, blank=True)
    user = models.ForeignKey('Register', on_delete=models.CASCADE, null=True, blank=True)  # Student
    teacher = models.ForeignKey('Teacherreg', on_delete=models.CASCADE, null=True, blank=True)  # Teacher
    is_read = models.BooleanField(default=False)  # Track unread notifications
    type = models.CharField(
        max_length=50,
        choices=[
            ('info', 'Info'),
            ('warning', 'Warning'), 
            ('error', 'Error')
        ],
        default='info'
    )

    def __str__(self):
        return f"{self.title}"


