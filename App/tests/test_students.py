from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import pytest
from model_bakery import baker
from  App.models import (Instructor, Student , StudentProgress, User ,Course , CourseContent , Quiz ,
                         QuizQuestion  , ForumPostComment , ForumPost , Payment_Order , 
                         StripePayment , Enrollment ,  Certificate , StudentSubscription )


    
    


@pytest.mark.django_db(transaction=True)
class TestStudentViewSet:
    class TestStudentCreate:
       
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)

        def test_if_user_is_authenticated_return_201(self):
            self.client = APIClient()
            User = get_user_model()
            self.client.force_authenticate(user=self.user)
            
            response = self.client.post('/DzSkills/students/', { 'biography': 'Expert developer' })
            
            assert response.status_code == status.HTTP_201_CREATED

        def test_if_user_is_anonymous_return_401(self):
            self.client = APIClient()
            self.client.logout()
            response = self.client.post('/DzSkills/students/', {
                'biography': 'Expert developer'
            })
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # def test_if_instructor_already_exists_return_400(self):
            
        #     self.client.force_authenticate(user=self.user)
        #     baker.make('Instructor', user=self.user)
            
        #     response = self.client.post('/DzSkills/instructors/', {
        #         'biography': 'Another bio'
        #     })
            
        #     assert response.status_code == status.HTTP_400_BAD_REQUEST

    class TestStudentRetrieve:
        
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)

        def test_if_user_is_anonymous_return_403(self):
            self.client.force_authenticate(user={})
            
            # Create multiple instructors
            baker.make('Student', _quantity=3)
            
            response = self.client.get('/DzSkills/students/')
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
        

        def test_if_user_is_authenticated_return_specific_student(self):
            self.client.force_authenticate(user=self.user)
            
            # Create an student
            student = baker.make('Student' , user = self.user)
            
            response = self.client.get(f'/DzSkills/students/{student.id}/')
            
            assert response.status_code == status.HTTP_200_OK

        def test_if_user_is_instructor_return_own_student_profile(self):
            # Create an instructor for the current user
            self.client.force_authenticate(user=self.user)
            student = baker.make('Student', user=self.user)            
            response = self.client.get('/DzSkills/students/me/')
            
            assert response.status_code == status.HTTP_200_OK

    class TestStudentUpdate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)

        def test_if_user_updates_own_student_profile_return_200(self):
            # Create an instructor for the current user
            self.client.force_authenticate(user=self.user)
            student = baker.make('Student', user=self.user, biography='Old bio')
            
            
            response = self.client.patch(f'/DzSkills/students/{student.id}/', {
                'biography': 'Updated bio'
            })
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['biography'] == 'Updated bio'

        # def test_if_user_updates_another_student_profile_return_403(self):
        #     # Create another user and their instructor
        #     User = get_user_model()
        #     another_user = baker.make(User)
        #     self.client.force_authenticate(user=another_user)
            
            
        #     student2 = baker.make(Student, user=another_user)
            
        #     print("user" , another_user)
            
        #     print("student" , student2.biography )
        #     self.client.force_authenticate(user=self.user)
            
        #     response = self.client.patch(f'/DzSkills/student/{student2.id}/', {
        #         'biography': 'Updated bio'
        #     })
            
        #     assert response.status_code == status.HTTP_403_FORBIDDEN
