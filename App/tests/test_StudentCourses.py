from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
import pytest
from model_bakery import baker
import App.models 
from  App.models import (Instructor, Student , StudentProgress, User ,Course , CourseContent , Quiz ,
                         QuizQuestion  , ForumPostComment , ForumPost , Payment_Order , 
                         StripePayment , Enrollment ,  Certificate , StudentSubscription )
from django.core.files.uploadedfile import SimpleUploadedFile
from  django.utils import timezone
from datetime import timedelta



@pytest.mark.django_db(transaction=True)

class TestStudentCourseViewSet:
    class TestList:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.student = baker.make(Student, user=self.user)
            self.course  = baker.make(Course)
            self.enrollment = baker.make(Enrollment, course=self.course, student=self.student)

        def test_if_user_is_anonymous_return_401(self):
            response = self.client.get(f'/DzSkills/students/{self.student.id}/courses/')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_student_can_list_enrolled_courses(self):
            
            self.client.force_authenticate(user=self.user)
                        
            response = self.client.get(f'/DzSkills/students/{self.student.id}/courses/')
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 1
        
        def test_another_student_cannot_see_courses_of_other_student(self):
            
            other_user = baker.make(User)
            student2 = baker.make('Student', user=other_user)
            
            self.client.force_authenticate(user=other_user)
            
            
            
            response = self.client.get(f'/DzSkills/students/{self.student.id}/courses/')
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            

        def test_student_with_subscription_can_see_all_courses(self):
            self.client.force_authenticate(user=self.user)
            s = baker.make(StudentSubscription , student = self.student ,start_date = timezone.now(), 
                           end_date = (timezone.now() + timedelta(days=120))  )
            baker.make('Course', _quantity=3)
            
            response = self.client.get(f'/DzSkills/students/{self.student.id}/courses/')
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 4