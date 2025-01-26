from asyncio import mixins
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
class User(AbstractUser):

    email = models.EmailField(unique=True)
    referalcode=models.CharField(max_length=10, null=True, blank=True)
    def __str__(self):
        return self.username

class Instructor(models.Model):
    """Instructor profile model"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='instructor_profile'
    )
    biography = models.TextField(blank=True, null=True)
    bank_Account = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Instructor Profile"

class Student(models.Model):
    """Student profile model"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile'
    )
    
    biography = models.TextField(blank=True, null=False)
    
    
    
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Student Profile"

class Course(models.Model):
    instructor = models.ForeignKey(
        Instructor, 
        on_delete=models.CASCADE, 
        related_name='courses'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration_hours = models.IntegerField(
        validators=[MinValueValidator(0)],
        null=True
    )
    language = models.CharField(max_length=50)
    
    def __str__(self):
        return self.title
class CourseContent(models.Model):
    """Individual content units within a course"""
    CONTENT_TYPES = (
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )
    
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='contents'
    )
    title = models.CharField(max_length=200)
    content_type = models.CharField(
        max_length=20, 
        choices=CONTENT_TYPES
    )
    content_data_file = models.FileField(upload_to='course_contents/', null=True)
    uploaded_at = models.DateTimeField(auto_now=True)
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    is_free_preview = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Quiz(models.Model):
    """Quiz model associated with courses"""
    course_content = models.OneToOneField(
        CourseContent, 
        on_delete=models.CASCADE, 
        related_name='quizzes'
    )
    
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Quiz: {self.title}"

class QuizQuestion(models.Model):
    """Questions within a quiz"""
    
    
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    question_text = models.TextField()
    possible_answers = models.JSONField()
    correct_answer = models.CharField(max_length=500)    
    def __str__(self):
        return self.question_text[:50]

class StudentProgress(models.Model):
    """Tracks student progress in a course"""
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='course_progresses'
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='student_progresses'
    )

    watched_course_content =  models.ForeignKey(
        CourseContent, 
        on_delete=models.CASCADE, 
        related_name='course_content_progresses'
    )

    # completion_percentage = models.FloatField(
    #     validators=[
    #         MinValueValidator(0.0), 
    #         MaxValueValidator(100.0)
    #     ],
    #     default=0.0
    # )

    

    class Meta:
        
        verbose_name_plural = 'Student Progresses'
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.title} Progress"

class Certificate(models.Model):
    """Certificates issued to students upon course completion"""
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='certificates'
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='issued_certificates'
    )
    certificate_number = models.CharField(
        max_length=50, 
        unique=True
    )
    issue_date = models.DateTimeField(auto_now_add=True)
    # certifications_image = models.ImageField(
    #     upload_to='Certifications/', 
    #     null=True, 
    #     blank=True
    # )
    Student.__str__
    def __str__(self):
        return f"Certificate for {self.student.__str__} - {self.course.title}"

# class ForumTopic(models.Model):
#     """Discussion topics within a course"""
#     course = models.ForeignKey(
#         Course, 
#         on_delete=models.CASCADE, 
#         related_name='forum_topics'
#     )
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     # is_pinned = models.BooleanField(default=False)
    
#     def __str__(self):
#         return self.title

class ForumPost(models.Model):
    """Individual posts within a forum topic"""
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='forum_topics'
    )
    title = models.CharField(max_length=200)
    # description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_posts'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # is_solution = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Post by {self.user.username} in {self.title}"
    
class ForumPostComment(models.Model):
    """Individual posts within a forum topic"""
    post = models.ForeignKey(
        ForumPost, 
        on_delete=models.CASCADE, 
        related_name='post_comment'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_post_comments'
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # is_solution = models.BooleanField(default=False)
    
    def __str__(self):
        return f"post about: {self.Post.title} comment: {self.comment} by: {self.user.__str__} "

# class Subscription(models.Model):
#     """Subscription plans for the platform"""
#     PLAN_DURATIONS = (
#         (1, '1 Month'),
#         (3, '3 Months'),
#         (6, '6 Months'),
#         (12, '12 Months'),
#     )
    
#     plan_name = models.CharField(max_length=100)
#     price = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         validators=[MinValueValidator(0)]
#     )
#     duration_months = models.IntegerField(
#         choices=PLAN_DURATIONS
#     )
#     features = models.JSONField()
#     is_active = models.BooleanField(default=True)
    
#     def __str__(self):
#         return f"{self.plan_name} ({self.duration_months} months)"

class StudentSubscription(models.Model):
    """Subscriptions purchased by students"""
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
    )

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.student.__str__} - in sub"
    
    def is_sub(student : Student  , std_id  : int  = -1 ):
       sub= None
       if std_id !=-1:
           sub =  StudentSubscription.objects.filter(student_id = std_id).last() 
       else:
           sub =  StudentSubscription.objects.filter(student_id = student.pk).last()  
       print(sub)
       return (  (sub ) and ( sub.end_date >= timezone.now() ) )

class StripePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='stripe_payments')
    stripe_charge_id = models.CharField(max_length=100)
    paid_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    course_price= models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.stripe_charge_id


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_enrollments')
    payment = models.OneToOneField(StripePayment, on_delete=models.CASCADE, related_name='enrollment_pay')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment {self.student.__str__} - {self.course.title}"
class Affiliation(models.Model):
    user=models.ManyToManyField(User,related_name='user')
    refereduser=models.ManyToManyField(User,related_name='refereduser',blank=True)
    Course=models.ManyToManyField(Course,related_name='Course')
    referal_link=models.CharField( null=True, blank=True)
    def __str__(self):
        return f"Affiliate Program - {self.user.username}"
class affiliatedusers(models.Model):
    affiliateduser=models.ForeignKey(User, on_delete=models.CASCADE, related_name='affiliateduser')
    affiliation=models.ForeignKey(Affiliation, on_delete=models.CASCADE, related_name='affiliation')
    created_at = models.DateTimeField(default=timezone.now)
    boughted = models.BooleanField(default=False)
    earning=models.FloatField(default=0)
# models.py