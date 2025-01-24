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
    class TestList:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)

        def test_if_user_is_anonymous_return_401(self):
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_if_authenticated_user_can_list_instructor_courses(self):
            self.client.force_authenticate(user=self.user)
            baker.make('Course', instructor=self.instructor, _quantity=3)
            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/')
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 3

    class TestCreate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)

        def test_if_instructor_can_create_course(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.post(f'/DzSkills/instructors/{self.instructor.id}/courses/', {
                'title': 'New Course',
                'description': 'Course description',
                'price': 99.99,
                'duration_hours' :0,
                'language': 'english',
                'thumbnail' : ''
                
            })
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['title'] == 'New Course'

        def test_if_non_instructor_cannot_create_course(self):
            other_user = baker.make(User)
            self.client.force_authenticate(user=other_user)
            
            response = self.client.post(f'/DzSkills/instructors/{self.instructor.id}/courses/', {
                'title': 'New Course',
                'description': 'Course description',
                'price': 99.99,
                'duration_hours' :0,
                'language': 'english',
                'thumbnail' : ''
            })
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
            
        def test_if_another_instructor_cannot_create_course(self):
            other_user = baker.make(User)
            Instructor2 = baker.make('Instructor', user=other_user)
            self.client.force_authenticate(user=other_user)
            
            response = self.client.post(f'/DzSkills/instructors/{self.instructor.id}/courses/', {
                'title': 'New Course',
                'description': 'Course description',
                'price': 99.99,
                'duration_hours' :0,
                'language': 'english',
                'thumbnail' : ''
            })
            
            assert response.status_code == status.HTTP_403_FORBIDDEN    

        def test_if_anonymous_user_cannot_create_course(self):
            response = self.client.post(f'/DzSkills/instructors/{self.instructor.id}/courses/', {
                'title': 'New Course',
                'description': 'Course description',
                'price': 99.99
            })
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    class TestRetrieve:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)

        def test_if_user_is_authenticated_can_retrieve_course(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/')
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['id'] == self.course.id

    class TestUpdate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)

        def test_instructor_can_update_own_course(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.patch(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/', {
                'title': 'Updated Course'
            })
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['title'] == 'Updated Course'

        def test_other_instructor_cannot_update_course(self):
            other_user = baker.make(User)
            other_instructor = baker.make('Instructor', user=other_user)
            self.client.force_authenticate(user=other_user)
            
            response = self.client.patch(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/', {
                'title': 'Updated Course'
            })
            
            assert response.status_code == status.HTTP_403_FORBIDDEN

    class TestDelete:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)

        def test_instructor_can_delete_own_course(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.delete(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/')
            
            assert response.status_code == status.HTTP_204_NO_CONTENT

        def test_other_instructor_cannot_delete_course(self):
            other_user = baker.make(User)
            other_instructor = baker.make('Instructor', user=other_user)
            self.client.force_authenticate(user=other_user)
            
            response = self.client.delete(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/')
            
            assert response.status_code == status.HTTP_403_FORBIDDEN