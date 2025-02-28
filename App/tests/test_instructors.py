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
class TestInstructorViewSet:
    class TestInstructorCreate:
       
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)

        def test_if_user_is_authenticated_return_201(self):
            self.client = APIClient()
            User = get_user_model()
            self.client.force_authenticate(user=self.user)
            
            response = self.client.post('/DzSkills/instructors/', { 'biography': 'Expert developer' })
            
            assert response.status_code == status.HTTP_201_CREATED

        def test_if_user_is_anonymous_return_401(self):
            self.client = APIClient()
            self.client.logout()
            response = self.client.post('/DzSkills/instructors/', {
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

    class TestInstructorRetrieve:
        
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)

        def test_if_user_is_anonymous_return_403(self):
            self.client.force_authenticate(user={})
            
            baker.make('Instructor', _quantity=3)
            
            response = self.client.get('/DzSkills/instructors/')
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
        
        def test_if_user_is_authenticated_return_list_of_instructors(self):
            self.client.force_authenticate(user=self.user)
            
            baker.make('Instructor', _quantity=3)
            
            response = self.client.get('/DzSkills/instructors/')
            
            assert response.status_code == status.HTTP_200_OK

        def test_if_user_is_authenticated_return_specific_instructor(self):
            self.client.force_authenticate(user=self.user)
            
            instructor = baker.make('Instructor')
            
            response = self.client.get(f'/DzSkills/instructors/{instructor.id}/')
            
            assert response.status_code == status.HTTP_200_OK

        def test_if_user_is_instructor_return_own_instructor_profile(self):

            self.client.force_authenticate(user=self.user)
            instructor = baker.make('Instructor', user=self.user)            
            response = self.client.get('/DzSkills/instructors/me/')
            
            assert response.status_code == status.HTTP_200_OK

    class TestInstructorUpdate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)

        def test_if_user_updates_own_instructor_profile_return_200(self):

            self.client.force_authenticate(user=self.user)
            instructor = baker.make('Instructor', user=self.user, biography='Old bio')
            
            
            response = self.client.patch(f'/DzSkills/instructors/{instructor.id}/', {
                'biography': 'Updated bio'
            })
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['biography'] == 'Updated bio'

        # def test_if_user_updates_another_instructor_profile_return_403(self):

        #     another_user = baker.make(User)
        #     self.client.force_authenticate(user=another_user)
        #     instructor2 = baker.make('Instructor', user=another_user)
            
        #     self.client.force_authenticate(user=self.user)
            
        #     response = self.client.patch(f'/DzSkills/instructors/{instructor2.id}/', {
        #         'biography': 'Updated bio'
        #     })
            
        #     assert response.status_code == status.HTTP_403_FORBIDDEN

#     class TestInstructorDelete:
#         def setup_method(self):
#             self.client = APIClient()
#             User = get_user_model()
#             self.user = baker.make(User)

#         def test_if_user_deletes_own_instructor_profile_return_204(self):
#             # Create an instructor for the current user
#             instructor = baker.make('Instructor', user=self.user)
            
#             self.client.force_authenticate(user=self.user)
            
#             response = self.client.delete(f'/instructors/{instructor.id}/')
            
#             assert response.status_code == status.HTTP_204_NO_CONTENT

#         def test_if_user_deletes_another_instructor_profile_return_403(self):
#             # Create another user and their instructor
#             another_user = baker.make(User)
#             instructor = baker.make('Instructor', user=another_user)
            
#             self.client.force_authenticate(user=self.user)
            
#             response = self.client.delete(f'/instructors/{instructor.id}/')
            
#             assert response.status_code == status.HTTP_403_FORBIDDEN

# # Similar structure can be applied to other ViewSets
