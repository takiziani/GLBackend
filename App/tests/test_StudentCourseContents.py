from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
import pytest
from model_bakery import baker
import App.models 
from  django.utils import timezone
# from datetime import timedelta
from  App.models import (Instructor, Student , StudentProgress, User ,Course , CourseContent , Quiz ,
                         QuizQuestion  , ForumPostComment , ForumPost , Payment_Order , 
                         StripePayment , Enrollment ,  Certificate , StudentSubscription )
from django.core.files.uploadedfile import SimpleUploadedFile
from  django.utils import timezone
from datetime import timedelta



@pytest.mark.django_db(transaction=True)
class TestCourseContentViewSet:
    class TestList:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.student = baker.make(Student , user = self.user)
            self.course = baker.make(Course )
            self.course_content = baker.make(CourseContent, course=self.course, is_free_preview = False ,content_data_file = 'c/test',_quantity=3)
            baker.make(Enrollment , student = self.student , course  = self.course)
            

        def test_if_user_is_anonymous_return_401(self):
            self.client.logout()
            response = self.client.get(f'/DzSkills/students/{self.student.id}/courses/{self.course.id}/contents/')
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


        def test_enrolled_student_can_list_content(self):
            
            self.client.force_authenticate(user=self.user)
                    
            
            response = self.client.get(f'/DzSkills/students/{self.student.id}/courses/{self.course.id}/contents/')
            
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 3
            for item in response.data:
                assert 'content_data_file' in item
        
        
        
        def test_unenrolled_student_get_course_contents_without_data_path(self):
            
            other_user = baker.make(User)
            student = baker.make(Student ,  user = other_user)
            self.client.force_authenticate(user=other_user)
                        
            response = self.client.get(f'/DzSkills/students/{student.id}/courses/{self.course.id}/contents/')
            
            assert response.status_code == status.HTTP_200_OK
            for item in response.data:
                assert 'content_data_file' not in item
            


        def test_student_can_not_see_course_contents_of_other(self):
            
            other_user = baker.make(User)
            student = baker.make(Student ,  user = other_user)
            self.client.force_authenticate(user=other_user)
                        
            response = self.client.get(f'/DzSkills/students/{self.student.id}/courses/{self.course.id}/contents/')
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
            
        def test_student_with_subscription_can_see_all_courses_and_all_contents(self):
            self.client.force_authenticate(user=self.user)
            s = baker.make(StudentSubscription , student = self.student ,start_date = timezone.now(), 
                           end_date = (timezone.now() + timedelta(days=120))  )
            
            course2 = baker.make(Course)
            
            baker.make(CourseContent , course=course2)
            
            response = self.client.get(f'/DzSkills/students/{self.student.id}/courses/{self.course.id}/contents/')
            
            assert response.status_code == status.HTTP_200_OK
            for item in response.data:
                assert 'content_data_file' in item
