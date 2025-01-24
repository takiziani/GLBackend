from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
import pytest
from model_bakery import baker
import App.models 
from  App.models import (Instructor, Student , StudentProgress, User ,Course , CourseContent , Quiz ,
                         QuizQuestion  , ForumPostComment , ForumPost , Payment_Order , 
                         StripePayment , Enrollment ,  Certificate , StudentSubscription )


@pytest.mark.django_db(transaction=True)
class TestCourseViewSet:

    class TestCourseRetrieve:
        
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)

        def test_if_user_is_anonymous_return__list_of_courses(self):
            self.client.force_authenticate(user=self.user)
            instructor = baker.make('Instructor', user=self.user) 
            baker.make('Course', instructor = instructor, _quantity=3)
            self.client.logout()
            
            response = self.client.get('/DzSkills/courses/')
            
            assert response.status_code == status.HTTP_200_OK
        
        def test_if_user_is_authenticated_return_list_of_courses(self):
            self.client.force_authenticate(user=self.user)
            instructor = baker.make('Instructor', user=self.user) 
            baker.make('Course', instructor = instructor, _quantity=3)
            
            
            response = self.client.get('/DzSkills/courses/')
            
            assert response.status_code == status.HTTP_200_OK

        def test_if_user_is_authenticated_return_specific_instructor(self):
            
            self.client.force_authenticate(user=self.user)
            instructor = baker.make('Instructor', user=self.user) 
            course = baker.make('Course', instructor = instructor)
                        
            response = self.client.get(f'/DzSkills/courses/{course.id}/')
            
            assert response.status_code == status.HTTP_200_OK

        