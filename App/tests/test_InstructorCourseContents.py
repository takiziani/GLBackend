from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from  django.utils import timezone
from datetime import timedelta
import pytest
from model_bakery import baker
import App.models 
from  App.models import (Instructor, Student , StudentProgress, User ,Course , CourseContent , Quiz ,
                         QuizQuestion  , ForumPostComment , ForumPost , Payment_Order , 
                         StripePayment , Enrollment ,  Certificate , StudentSubscription )
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db(transaction=True)
class TestCourseContentViewSet:
    class TestList:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make(Instructor, user=self.user)
            self.course = baker.make(Course , instructor = self.instructor)

        def test_if_user_is_anonymous_return_401(self):
            self.client.logout()
            c= baker.make(CourseContent, course=self.course ,_quantity=3)            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/')
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


        def test_instructor_can_list_his_own_content(self):
            
            self.client.force_authenticate(user=self.user)
            
            
            baker.make(CourseContent, course=self.course, is_free_preview = False ,content_data_file = 'c/test',_quantity=3)
            
            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/')
            
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 3
            for item in response.data:
                assert 'content_data_file' in item
        
        
        
        def test_authenticated_user_can_list_content_without_data_file_path(self):
            
            
            baker.make(CourseContent, course=self.course, is_free_preview = False ,content_data_file = 'c/test',_quantity=3)
            other_user = baker.make(User)
            self.client.force_authenticate(user=other_user)
                        
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/')
            print("res::" , response.data)
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 3
            for item in response.data:
                assert 'content_data_file' not in item

            
            
        def test_enrolled_student_can_list_contents(self):
            
            other_user = baker.make(User)
            student = baker.make('Student', user=other_user)
            
            baker.make(Enrollment , course = self.course , student = student)
                        
            self.client.force_authenticate(user=other_user)
            
            c = baker.make(CourseContent, course=self.course,is_free_preview = False ,content_data_file = 'c/test', _quantity=3)
            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/')
            
            print("co cont:" ,c[0].content_data_file )
            
            assert response.status_code == status.HTTP_200_OK
            for item in response.data:
                assert 'content_data_file' in item
            assert len(response.data) == 3


        def test_subscribe_student_can_list_contents(self):
            
            other_user = baker.make(User)
            
            student = baker.make('Student', user=other_user)
            
            s = baker.make(StudentSubscription , student = student ,start_date = timezone.now(), 
                           end_date = (timezone.now() + timedelta(days=120))  )
            
            print("sub::" , s)
            
            self.client.force_authenticate(user=other_user)
            
            c = baker.make(CourseContent, course=self.course,is_free_preview = False ,content_data_file = 'c/test', _quantity=3)
            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/')
            
            
            assert response.status_code == status.HTTP_200_OK
            
            print("res::" ,response.data )
            
            for item in response.data:
                assert 'content_data_file' in item
            assert len(response.data) == 3

    class TestCreate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)

        def test_instructor_can_create_content(self):
            
            self.client.force_authenticate(user=self.user)
            
            test_file = SimpleUploadedFile(
            name='test.txt',
            content=b'test content',
            content_type='text/plain'
            )

            response = self.client.post(
                f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/',
                {
                    'title': 'New Content',
                    'content_data_file': test_file,  # Use the simulated file
                    'is_free_preview': False,
                    'content_type': 'assignment',
                    'duration_minutes': 10,
                },
                format='multipart'  # Important for file uploads
            )
            
            
            assert response.status_code == status.HTTP_201_CREATED

        def test_non_instructor_cannot_create_content(self):
            other_user = baker.make(User)
            self.client.force_authenticate(user=other_user)
                        
            test_file = SimpleUploadedFile(
            name='test.txt',
            content=b'test content',
            content_type='text/plain'
            )

            response = self.client.post(
                f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/',
                {
                    'title': 'New Content',
                    'content_data_file': test_file,  # Use the simulated file
                    'is_free_preview': False,
                    'content_type': 'assignment',
                    'duration_minutes': 10,
                },
                format='multipart'  # Important for file uploads
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN

    class TestUpdate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)
            self.content = baker.make('CourseContent', course=self.course)

        def test_instructor_can_update_content(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.patch(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/', {
                'title': 'Updated Content'
            })
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['title'] == 'Updated Content'
            
            
        def test_non_instructor_user_can_not_update_content(self):
            other_user = baker.make(User)
            self.client.force_authenticate(user=other_user)
            
            response = self.client.patch(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/', {
                'title': 'Updated Content'
            })
            
            assert response.status_code == status.HTTP_403_FORBIDDEN

    class TestDelete:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)
            self.content = baker.make('CourseContent', course=self.course)

        def test_instructor_can_delete_content(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.delete(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/')
            
            assert response.status_code == status.HTTP_204_NO_CONTENT