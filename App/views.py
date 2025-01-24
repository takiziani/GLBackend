from django.shortcuts import get_object_or_404, render , redirect
from rest_framework import viewsets 
from rest_framework.mixins import CreateModelMixin , UpdateModelMixin , RetrieveModelMixin , ListModelMixin , DestroyModelMixin
from .models import (Instructor, Student , StudentProgress, User ,Course , CourseContent , Quiz , QuizQuestion  ,
                     ForumPostComment , ForumPost , Payment_Order , StripePayment , Enrollment , Certificate , StudentSubscription,Affiliation,affiliatedusers)
from .serializers import (InstructorSerializer, StudentSerializer , CourseSerializer , 
                          InstructorSerializerSensitive , CourseContentSerializer , QuizSerializer ,
                          QuizQuestionSerializer , ForumPostSerializer , ForumPostCommentSerializer,
                          StudentCourseContentSerializer , StudentQuizSerializer ,
                          StudentQuizQuestionSerializer ,StudentProgressSerializer, CourseContentWithQuizSerializer,
                          StudentCourseSerializer , UnEnrolledStudentCourseContentSerializer , CertificateSerializer , EnrollmentSerializer)
from rest_framework.permissions import IsAuthenticated , SAFE_METHODS , IsAdminUser
from rest_framework.viewsets import GenericViewSet , ReadOnlyModelViewSet , ModelViewSet 
from django.views import View
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.http import HttpResponse, JsonResponse, HttpRequest  , HttpResponseRedirect
import stripe
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
import os
import requests
from django.http import FileResponse, Http404
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
import logging  # For logging errors and important events
from django.utils.decorators import method_decorator  # Apply decorators to class methods
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
import hmac
import hashlib
from rest_framework.views import APIView
from uuid import uuid4
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsCourseInstructorOrReadOnly , IsInstructorOrReadOnly , IsStudent , IsUserPost , IsUserComment , IsExistStudentForUser
from rest_framework import status
from django.db import connection
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Func, F, Value, CharField
from django.db.models.functions import Concat, ExtractMonth, ExtractYear

class InstructorViewSet(ListModelMixin , CreateModelMixin, RetrieveModelMixin , UpdateModelMixin , GenericViewSet , DestroyModelMixin):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [IsAuthenticated , IsInstructorOrReadOnly]
    
    def create(self, request):
        instructor = Instructor.objects.create(user_id=request.user.id)
        serializer = InstructorSerializerSensitive(instructor, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data , status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if(self.request.method == 'POST'):
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated() , IsInstructorOrReadOnly()]
    
    def get_serializer_class(self):
        if self.request and self.request.method in SAFE_METHODS:
            return InstructorSerializer
        return InstructorSerializerSensitive
    
    
    @action(detail = False , methods = ['GET', 'PUT'] , permission_classes = [IsAuthenticated])
    def me(self, request):
       (instructor , is_created) = Instructor.objects.get_or_create(user=request.user)
       if  is_created :
            return Response("instructor does not exist")
        
       if( request.method == 'GET'):
              ser_data = InstructorSerializer(instructor)  
              return Response(ser_data.data)
       elif( request.method == 'PUT'):
           ser_data = InstructorSerializer(instructor , data= request.data)
           ser_data.is_valid(raise_exception=True)
           ser_data.save()
           return Response(ser_data.data)

class StudentViewSet(  GenericViewSet, CreateModelMixin,  RetrieveModelMixin,  UpdateModelMixin):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated , IsStudent]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsStudent()]
    
        
    def create(self, request):
        student = Student.objects.create(user=request.user)
        serializer = StudentSerializer(student, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data , status=status.HTTP_201_CREATED)

    
    @action(detail = False , methods = ['GET', 'PUT'] , permission_classes = [IsAuthenticated])
    def me(self, request):
        (student , is_created) = Student.objects.get_or_create(user=request.user)
       
        if  is_created :
            return Response("student does not exist")
        

        if( request.method == 'GET'):
            ser_data = StudentSerializer(student)  
            return Response(ser_data.data)
        elif( request.method == 'PUT'):
            ser_data = StudentSerializer(student , data= request.data)
            ser_data.is_valid(raise_exception=True)
            ser_data.save()
            return Response(ser_data.data)
            #permission_classes = [IsAuthenticated]
    
    
    @action(detail = False , methods = ['GET']   , permission_classes = [IsAuthenticated])
    def courses(self, request):
        
        (student , is_created ) = Student.objects.get_or_create(user=request.user)
        enrolled_courses =  Course.objects.filter(
        id__in=Enrollment.objects.filter(student_id=student.pk).values_list('course_id', flat=True)
        ).select_related('instructor__user')
        ser_data = CourseSerializer(enrolled_courses , many = True)
        
        is_sub = StudentSubscription.is_sub(student)
        
        if(is_sub):
            ser_data = CourseSerializer(Course.objects.all().select_related('instructor__user') , many = True)
        
        return Response(ser_data.data)
    
#ReadOnlyModelViewSet
class HomeCourseViewSet( ReadOnlyModelViewSet ):
       
    queryset = Course.objects.all().select_related('instructor')
    serializer_class = CourseSerializer
    
class HomeCourseContentViewSet( ReadOnlyModelViewSet ):
       
    permission_classes = [IsAuthenticated ]
    queryset = CourseContent.objects.all()
    serializer_class = UnEnrolledStudentCourseContentSerializer
    
    
    
    def get_queryset(self):
            course_pk = self.kwargs['course_pk']
                          
            return CourseContent.objects.filter(course_id=course_pk)

class CourseViewSet( ModelViewSet ):
    
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated , IsCourseInstructorOrReadOnly]
    
    def get_queryset(self):
            instructor_pk = self.kwargs['instructor_pk']
            return Course.objects.filter(instructor_id=instructor_pk)

    def get_serializer_context( self):

           return {'instructor_id' : self.kwargs['instructor_pk']}

class CourseContentViewSet( ModelViewSet ):
       
       
    queryset = CourseContent.objects.all()
    serializer_class = CourseContentWithQuizSerializer
    permission_classes = [IsAuthenticated , IsCourseInstructorOrReadOnly]
    
    def get_queryset(self):
            course_pk = self.kwargs['course_pk']
            local_queryset = CourseContent.objects.filter(course_id=course_pk).prefetch_related('quizzes')
            #if(user enrolled update the local_queryset to filter if it is free to watch
            # return or not return every thing just the path )
            return local_queryset
        
    
    def get_serializer_context(self):
           return {'course_id' : self.kwargs['course_pk']
                  }
           
    def get_serializer(self, *args, **kwargs ):
        
        
      try:
        instructor_id = -1
        
        instructor = Instructor.objects.filter(user = self.request.user).last()
        
        if(instructor):
            instructor_id = instructor.pk
        
        course_id=self.kwargs['course_pk']
                
        is_instructor = Course.objects.filter(pk = course_id , instructor_id = instructor_id).exists()
        
        is_student_exist = Student.objects.filter(user = self.request.user).last()

        is_subscribe = False
        
        is_enrolled = False
        
        if(is_student_exist):
            is_enrolled = Enrollment.objects.filter(
            student_id=  is_student_exist.pk  ,
            course_id=course_id
            ).exists()
            
            is_subscribe = StudentSubscription.is_sub( is_student_exist )
        
        if(is_instructor or is_enrolled or is_subscribe):
            serializer_class = CourseContentSerializer
            
        else:
            
            serializer_class = UnEnrolledStudentCourseContentSerializer
    
        # Return an instance of the serializer, not the class itself
        return serializer_class(*args, **kwargs, context=self.get_serializer_context())
      except:
          return Response("we get an error retry with proper arguments!") 
    
     #def save_progress       
        
class QuizViewSet( ModelViewSet ):
       
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated , IsCourseInstructorOrReadOnly]
    
    def get_queryset(self):

            course_content_pk = self.kwargs['course_content_pk']
            
            return Quiz.objects.filter(course_content=course_content_pk)
        
    
    def get_serializer_context(self):

           return {'course_content_id' : self.kwargs['course_content_pk']
                  }          
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class QuizQuestionViewSet( ModelViewSet ):
       
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer
    permission_classes = [IsAuthenticated , IsCourseInstructorOrReadOnly]
    
    def get_queryset(self):
            quiz_pk = self.kwargs['quiz_pk']
            
            q= QuizQuestion.objects.filter(quiz=quiz_pk)
            
            is_free = CourseContent.objects.get(pk = self.kwargs['course_content_pk']).is_free_preview
            
            if (is_free):
                return q
            try:
                
                 
                 course_pk = self.kwargs['course_pk']
                 instructor = Instructor.objects.filter(user = self.request.user).last()

                 is_course_inst = Course.objects.filter( pk = course_pk , instructor = instructor).exists()

                 if(is_course_inst):
                     return q
                 
                                 
                 student = Student.objects.get(user = self.request.user)
                 course_pk = self.kwargs['course_pk']
                 
                 is_enrolled = Enrollment.objects.filter(
                 student_id = student.pk  , 
                 course_id = course_pk 
                 ).exists()
                 
                 is_sub = StudentSubscription.is_sub(student)
                 if is_enrolled or is_sub:
                    return q
                 return QuizQuestion.objects.none()
            except:
                return QuizQuestion.objects.none()
            # return QuizQuestion.objects.filter(quiz=quiz_pk)
        
    
    def get_serializer_context(self):

           return {'quiz_id' : self.kwargs['quiz_pk'] }      

class ForumPostViewSet( ModelViewSet ):
       
    permission_classes = [IsAuthenticated , IsUserPost]
    queryset = ForumPost.objects.all()
    serializer_class = ForumPostSerializer
    
    def get_queryset(self):
            course_pk = self.kwargs['course_pk']
            return ForumPost.objects.filter(course=course_pk)
        
    
    def get_serializer_context(self):

           return {'course_id' : self.kwargs['course_pk'] } 
       
    
    def create(self, request, *args, **kwargs):
        # Get the instructor from the URL
        course_pk = self.kwargs['course_pk']
        user_id = request.user.id
        
        course = Course.objects.get(pk=course_pk)
        user = User.objects.get(pk=user_id)
        post = ForumPost.objects.create(course=course, user=user)
        
        # Get the serializer
        serializer = ForumPostSerializer(post , data=request.data)
        
        # Validate the data
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response(serializer.data , status=status.HTTP_201_CREATED)
        
class ForumPostCommentViewSet( ModelViewSet ):
       
    permission_classes = [IsAuthenticated , IsUserComment]
    queryset = ForumPostComment.objects.all()
    serializer_class = ForumPostCommentSerializer
    
    def get_queryset(self):
            post_pk = self.kwargs['post_pk']
            return ForumPostComment.objects.filter(post=post_pk)
        
    
    def get_serializer_context(self):
           return {'post_id' : self.kwargs['post_pk'] } 
       
    
    def create(self, request, *args, **kwargs):
        # Get the instructor from the URL
        post_pk = self.kwargs['post_pk']
        user_id = request.user.id
        post = ForumPost.objects.get(pk=post_pk)
        user = User.objects.get(pk=user_id)
        post = ForumPostComment.objects.create(post=post, user=user)

        serializer = ForumPostCommentSerializer(post , data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response(serializer.data , status=status.HTTP_201_CREATED)

#######"" for student
class StudentQuizQuestionViewSet( ReadOnlyModelViewSet ):
       
    queryset = QuizQuestion.objects.all()
    serializer_class = StudentQuizQuestionSerializer
    permission_classes = [IsAuthenticated , IsStudent]
    
    def get_queryset(self):

            quiz_pk = self.kwargs['quiz_pk']
            q= QuizQuestion.objects.filter(quiz=quiz_pk)
            is_free = CourseContent.objects.get(pk = self.kwargs['course_content_pk']).is_free_preview
            if (is_free):
                return q
            try:
                 student = Student.objects.get(user = self.request.user)
                 course_pk = self.kwargs['course_pk']
                 is_enrolled = Enrollment.objects.filter(
                 student_id = student.pk  , 
                 course_id = course_pk 
                 ).exists()
                 is_sub = StudentSubscription.is_sub(student)
                 if is_enrolled or is_sub:
                    return q
                 return QuizQuestion.objects.none()
            except:
                return QuizQuestion.objects.none()               

class StudentCourseViewSet( ReadOnlyModelViewSet ):
       
    queryset = Course.objects.all()
    serializer_class = StudentCourseSerializer
    permission_classes = [IsAuthenticated , IsStudent]
    
    def get_queryset(self):
            student_pk = self.kwargs['student_pk']
            
            if(StudentSubscription.is_sub(None , student_pk)):
                return Course.objects.all()
            
            return  Course.objects.filter(
        id__in=Enrollment.objects.filter(student_id=student_pk).values_list('course_id', flat=True)
        ).select_related('instructor__user')
            
    def get_serializer_context(self):
        # Pass additional context to the serializer
        context = super().get_serializer_context()
        context['student_pk'] = self.kwargs['student_pk']  # Pass student_pk to the serializer
        return context        
            
    @action(detail = True , methods = ['GET'])
    def progress(self, request , student_pk, pk):       
        student_id = student_pk
        course_id = pk        
        progress = StudentProgress.objects.filter(student = student_id , course = course_id)
        ser_data = StudentProgressSerializer(progress , many = True)  
        return Response(ser_data.data)
    
    
    @action(detail = True , methods = ['GET'])
    def certificate(self, request , student_pk, pk):   
        content_count = CourseContent.objects.filter(course_id=pk).count()
    
        

        watched_content_count = StudentProgress.objects.filter(
            student_id=student_pk,
            course_id=pk
        ).count()

        percentage = 0
        if(watched_content_count>0):
            percentage = (watched_content_count / content_count) * 100
        
        
        if(percentage < 100):
            return Response("You can't get a certificate if you did not complete the course")
                
        exist  =  Certificate.objects.filter(
            student_id= student_pk,
            course_id = pk
        ).exists()
        
        certificate = Certificate.objects.none()
        
        if exist:
         certificate = Certificate.objects.get(
            student_id= student_pk,
            course_id = pk
         )
         
         
        else:
            certificate_number = str(uuid4())[:8]
            certificate = Certificate.objects.create(
            student_id= student_pk,
            course_id = pk,
            certificate_number=certificate_number
         )
        
        ser_data = CertificateSerializer(certificate )
        
        return Response(ser_data.data)

class StudentCourseContentViewSet( ReadOnlyModelViewSet ):
       
    queryset = CourseContent.objects.all()
    serializer_class = StudentCourseContentSerializer
    permission_classes = [IsAuthenticated , IsStudent]
    
    
    def get_queryset(self):
        
            course_pk = self.kwargs['course_pk']            
            local_queryset = CourseContent.objects.filter(course_id=course_pk)
            return local_queryset
        
    
    def get_serializer_context(self):
        
        # Pass additional context to the serializer
        context = super().get_serializer_context()
        context['student_pk'] = self.kwargs['student_pk']  # Pass student_pk to the serializer
        return context
    
    
    def get_serializer(self, *args, **kwargs ):
        
        student_id = self.kwargs['student_pk']
        
        is_sub = StudentSubscription.is_sub(None , student_id)
        
        is_enrolled = Enrollment.objects.filter(
            student_id=self.kwargs['student_pk'],
            course_id=self.kwargs['course_pk']
            ).exists()
         
         
        serializer_class = (
        StudentCourseContentSerializer if is_enrolled or is_sub
        else UnEnrolledStudentCourseContentSerializer
        )
    
        # Return an instance of the serializer, not the class itself
        return serializer_class(*args, **kwargs, context=self.get_serializer_context())
    
    
    @action(detail = True , methods = ['POST'])
    def progress(self, request , pk , student_pk , course_pk):  
        
       try:      
        student= Student.objects.get (pk = student_pk)
        course= Course.objects.get (pk =course_pk)
        course_content = CourseContent.objects.get (pk = pk)
        
        is_enrolled_in_course = Enrollment.objects.filter(
           student = student  , 
           course = course
            ).exists()
        
        if(not is_enrolled_in_course):
            return Response("you are not enrolled in this course")
        
        is_enrolled = StudentProgress.objects.filter(
           student = student  , 
           course = course , watched_course_content = course_content
            ).exists()
        if is_enrolled:
            return Response("you already save this progress")
        

        progress = StudentProgress.objects.create(student = student  , 
                    course = course , watched_course_content = course_content)
        ser_data = StudentProgressSerializer(progress)  
        return Response(ser_data.data)
    
       except Student.DoesNotExist:
        return Response({"error": "Student not found."}, status=404)
       except Course.DoesNotExist:
           return Response({"error": "Course not found."}, status=404)
       except CourseContent.DoesNotExist:
           return Response({"error": "Course content not found."}, status=404)
       except Exception as e:
        return Response({"error": str(e)}, status=400)

class StudentQuizViewSet( ReadOnlyModelViewSet ):
    
    permission_classes = [IsAuthenticated , IsStudent]
    queryset = Quiz.objects.all()
    serializer_class = StudentQuizSerializer
    
    def get_queryset(self):
            course_content_pk = self.kwargs['course_content_pk']
            return Quiz.objects.filter(course_content=course_content_pk)

class SuccessView(TemplateView , APIView  ):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    template_name = "success.html"
    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add student ID to the context
        context['student'] =  Student.objects.get(user =  self.request.user)
        return context

class SuccessSubView(TemplateView , APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    template_name = "sub_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        # Add student ID to the context
        context['student'] =  Student.objects.get(user =  self.request.user)
        return context

class CancelView(TemplateView, APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    template_name = "cancel.html"
    
class CreateCheckoutSessionForPaymentView(APIView):
    
    
    
    def get_thumbnail_url(self , course : Course):
        if not course.thumbnail:
            return settings.DEFAULT_THUMBNAIL_URL
            
        try:
            with open(os.path.join(settings.MEDIA_ROOT, course.thumbnail.name), "rb") as image_file:
                response = requests.post(
                    "https://api.imgbb.com/1/upload",
                    data={"key": settings.IMGBB_API_KEY},
                    files={"image": image_file}
                ).json()
                return response['data']['url'] if response['status'] == 200 else settings.DEFAULT_THUMBNAIL_URL
        except:
            return settings.DEFAULT_THUMBNAIL_URL
    
    
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated , IsExistStudentForUser]
    def get(self, request, course_pk):
        try:
            # Ensure Stripe is configured
            
            
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Retrieve the course
            course = get_object_or_404(Course, pk=course_pk)
            student, _ = Student.objects.get_or_create(user=request.user)
            
            is_enrolled = Enrollment.objects.filter(
            student_id=student.pk,
            course_id=course_pk
            ).exists()
            
            
            if is_enrolled :
                return JsonResponse({'error': 'you already purchased this course'}, status=400)            
            
            # Validate course price
            if not course.price:
                return JsonResponse({'error': 'Course price is not set'}, status=400)
            
            # Convert price to cents        
            price_in_cents = int(float(course.price) * 100)
            
            # host the image so in checkout page stripe get the picture because it accept only hosted pictures
            
            thumbnail_url = self.get_thumbnail_url(course)

            checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': price_in_cents,
                        'product_data': {
                            'name': course.title,
                            'images':[thumbnail_url], 
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "course_id": course.pk,
                "course_title": course.title,
                "student_id": student.pk
            },
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri(f'/courses/{course_pk}'),
            )
                        
            # Redirect directly to Stripe Checkout
            return HttpResponseRedirect(checkout_session.url)
        
        except Exception as e:
            # Log the error and redirect to course details with an error message
            return JsonResponse({
                'error': f'Checkout failed: {str(e)}'
            }, status=500)

logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF protection for webhooks
class StripeWebhookView(View):
    """
    Handles webhook events from Stripe, processing course purchases
    and managing user enrollments
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize Stripe configuration when the view is instantiated
        Ensures Stripe API key and webhook secret are set up
        """
        super().__init__(*args, **kwargs)  # Call parent class initializer
        # Set Stripe API key from Django settings
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Retrieve Stripe webhook endpoint secret from settings
        self.endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    def post(self, request, *args, **kwargs):
        """
        Primary method to handle incoming POST requests from Stripe webhook
        
        Verifies webhook signature and routes to appropriate event handler
        """

        payload = request.body
        

        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            
            # Verify the webhook signature to prevent fraudulent requests
            event = stripe.Webhook.construct_event(
                payload,  # Raw request body
                sig_header,  # Stripe-provided signature
                self.endpoint_secret  # Our stored webhook secret
            )
            
            if event.type == 'checkout.session.completed':
                session = event['data']['object']
                # Check if this is a course purchase or subscription
                if session.get('metadata', {}).get('course_id'):
                    return self.handle_checkout_session_completed(event)
                else:
                    return self.handle_checkout_session_subscription_completed(event)
            
            return HttpResponse(status=200)
            
        except ValueError as e:
            # Logging and handling invalid payload
            logger.error(f"Invalid payload: {e}")
            return HttpResponse(status=400)  # Bad request
        except stripe.error.SignatureVerificationError as e:
            # Logging and handling signature verification failure
            logger.error(f"Invalid signature: {e}")
            return HttpResponse(status=400)  # Bad request
    
    def _send_enrollment_email_confirmation(self, user : User, enrollment : Enrollment):
        """
        Send an email confirmation of course enrollment
        """
        try:
            # Use Django's send_mail to send confirmation email
            send_mail(
                f'Enrollment Confirmed: {enrollment.course.title}',  # Email subject
                f'Congratulations! You have been enrolled in {enrollment.course.title}.',  # Email body
                settings.DEFAULT_FROM_EMAIL,  # Sender email
                [user.email],  # Recipient email
                fail_silently=False,  # Raise exceptions for email sending errors
            )
        except Exception as e:
            # Log any email sending errors
            logger.error(f"Failed to send confirmation email: {e}")

    def handle_checkout_session_completed(self, event):
        """
        Process a completed checkout session
        Creates StripePayment and Enrollment
        """
        session = event['data']['object']
        
        
        try:

            course_id = session['metadata'].get('course_id')
            student_id = session['metadata'].get('student_id')
            
            # Retrieve related objects
            course = Course.objects.get(pk=course_id)
            student = Student.objects.get(pk=student_id)
            
            
            # Create StripePayment record
            stripe_payment = StripePayment.objects.create(
                student=student,
                stripe_charge_id=session['payment_intent'],
                paid_amount=session['amount_total'] / 100,  # Convert cents to dollars
                course_price=course.price,
                timestamp=timezone.now()
            )
            # Create Enrollment
            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
                payment=stripe_payment
            )
            
            self._send_enrollment_email_confirmation( student.user , enrollment)
            affiliation=affiliatedusers.objects.filter(affiliateduser=student)
            if affiliation.exists():
                for aff in affiliation:
                    affiliationprogram=Affiliation.objects.get(pk=aff.affiliation)
                    if affiliationprogram.Course == course:
                        if (aff.created_at - timezone.now()).days < 30:
                            aff.boughted=True
                            aff.earning=course.price*0.2
                            aff.save()
                        else:
                            aff.delete()
            logger.info(f"Successful enrollment for student {student.__str__} in course {course.title}")
            
            return HttpResponse(status=200)
        
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return HttpResponse(status=500)

    def _send_subscriber_email_confirmation(self, user : User):
        """
        Send an email confirmation of course enrollment
        """
        try:
            # Use Django's send_mail to send confirmation email
            send_mail(
                f'subscription Confirmed',  # Email subject
                f'Congratulations! You have been subscribe in dz skills.',  # Email body
                settings.DEFAULT_FROM_EMAIL,  # Sender email
                [user.email],  # Recipient email
                fail_silently=False,  # Raise exceptions for email sending errors
            )
        except Exception as e:
            # Log any email sending errors
            logger.error(f"Failed to send confirmation email: {e}")

    def handle_checkout_session_subscription_completed(self, event):
        """
        Process a completed checkout session
        Creates StripePayment and Enrollment
        
        """
        
        session = event['data']['object']
        
        
        
        try:
            # Extract metadata from the session

            student_id = session.get('metadata', {}).get('student_id')
            
            
            # Retrieve related objects
            student = Student.objects.get(pk=student_id)
                        
            

            has_sub = StudentSubscription.is_sub(student)
            duration = int( getattr(settings, 'SUBSCRIPTION', {}).get('DURATION'))
            start_date = timezone.now()
            end_date = (timezone.now() + timedelta(days=duration))
            
            if(has_sub):
                sub = StudentSubscription.objects.get(
                student=student
                )
                end_date = sub.end_date + timedelta(days=duration)
                sub.delete()
            
            # Create StripePayment record
            subscription = StudentSubscription.objects.create(
                student=student,
                start_date = start_date,
                end_date = end_date
                
            )
            
            # Create Enrollment

            
            
            self._send_subscriber_email_confirmation( student.user )
            
            logger.info(f"Successful subscribe for student {student.__str__}")
            
            return HttpResponse(status=200)
        
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return HttpResponse(status=500)

class CreateCheckoutSessionForSubscriptionView(APIView): 
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated , IsExistStudentForUser]
    
    def get(self, request ,  student_pk):
        try:
            # Ensure Stripe is configured
            stripe.api_key = settings.STRIPE_SECRET_KEY
                        
            student, _ = Student.objects.get_or_create(user=request.user)
            
            price = getattr(settings, 'SUBSCRIPTION', {}).get('PRICE')
            
            if price == '0':
                return JsonResponse({'error': 'price is not set in settings'}, status=400)
            
            # Validate course price
            if not price:
                return JsonResponse({'error': 'price is not set'}, status=400)
            
            # Convert price to cents
            price_in_cents = int(float(price) * 100)

            checkout_session = checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': price_in_cents,
                            'product_data': {
                                'name': 'Dz Skills Subscription',
                            },
                        },
                        'quantity': 1,
                    },
                ],
                metadata={
                    "student_id": student.pk
                },
                mode='payment',
                success_url=request.build_absolute_uri('/sub_success/'),
                cancel_url=request.build_absolute_uri(f'/courses/'),
            )
            
            return HttpResponseRedirect(checkout_session.url)
        
        except Exception as e:
            # Log the error and redirect to course details with an error message
            return JsonResponse({
                'error': f'Checkout failed: {str(e)}'
            }, status=500)
import secrets
import string
class activateaffiliation(CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    def create(self, request):
        user1= request.user
        user= User.objects.get(pk=user1.id)
        alphabet = string.ascii_letters + string.digits
        while True:
            referalcode = ''.join(secrets.choice(alphabet) for i in range(8))
            if not User.objects.filter(referalcode=referalcode).exists():
                break
        user.referalcode = referalcode
        user.save()
        return JsonResponse({
            'message': 'Affiliation activated successfully',
            'referalcode': referalcode
        })
class generateaffiliationlink(CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    def create(self, request):
        user1= request.user
        course_pk = request.data['course_pk']
        course= Course.objects.get(pk=course_pk)
        user= User.objects.get(pk=user1.id)
        print(user)
        referalcode = user.referalcode
        referal_link = f'http://{request.get_host()}/DzSkills/affiliation/{course_pk}/contents/?referalcode={referalcode}'
        # Check if an affiliation with the same referal_link already exists
        if Affiliation.objects.filter(referal_link=referal_link).exists():
            return JsonResponse({
            'error': 'Affiliation link already exists'
        }, status=400)
        affiliation = Affiliation.objects.create(referal_link=referal_link)
        affiliation.Course.set([course])
        affiliation.user.set([user])
        affiliation.save()
        return JsonResponse({
            'message': 'Referal link generated successfully',
            'referal_link': referal_link
        })
class returnaffiliationlinks(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        user1 = self.request.user
        user = User.objects.get(pk=user1.id)
        affiliations = Affiliation.objects.filter(user=user)
        affiliation_links = [
            {
                'referal_link': affiliation.referal_link,
                'course': course.id,
                'course_title': course.title
            }
            for affiliation in affiliations
            for course in affiliation.Course.all()
        ]
        return Response({
            'affiliation_links': affiliation_links
        })
class handelaffiliatelinks(APIView):
    permission_classes = [IsAuthenticated]

class EnrollmentViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = EnrollmentSerializer

    queryset = Enrollment.objects.select_related(
        'course',
        'course__instructor',
        'course__instructor__user'
    ).annotate(
        month_year=Concat(
            ExtractMonth(F('enrolled_at')),
            Value('/'),
            ExtractYear(F('enrolled_at')),
            output_field=CharField()
        )
    ).values(
        'id',
        'enrolled_at',
        'course_id',
        'course__title',
        'course__price',
        'course__instructor_id',
        'course__instructor__bank_Account',
        'course__instructor__user_id',
        'course__instructor__user__first_name',
        'course__instructor__user__last_name',
        'course__instructor__user__username',
        'month_year'  # Include the annotated field in the values
    )
    def get(self, request,course_pk):
        referalcode = request.GET.get('referalcode')
        if not referalcode:
            return JsonResponse({'error': 'Referal code is required'}, status=400)

        try:
            user = User.objects.get(referalcode=referalcode)
            course = Course.objects.get(pk=course_pk)
            aff = Affiliation.objects.get(user=user, Course=course)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Affiliation.DoesNotExist:
            return JsonResponse({'error': 'Affiliation not found'}, status=404)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

        affiliateduser, created = affiliatedusers.objects.get_or_create(affiliateduser=request.user, affiliation=aff)
        affiliateduser.created_at = timezone.now()
        affiliateduser.save()

        return JsonResponse(CourseSerializer(course).data)
class getaffiliationearning(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        user = self.request.user
        affiliation= Affiliation.objects.filter(user=user)
        total_earning = 0
        for aff in affiliation:
            affiliatedusers = affiliatedusers.objects.filter(affiliation=aff, boughted=True)
            for affiliateduser in affiliatedusers:
                total_earning += affiliateduser.earning
        return JsonResponse({'total_earning': total_earning})
