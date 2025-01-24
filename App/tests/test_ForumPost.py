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
class TestForumPostViewSet:
    class TestList:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.course = baker.make('Course')

        def test_if_user_is_anonymous_return_401(self):
            response = self.client.get(f'/DzSkills/courses/{self.course.id}/posts/')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_authenticated_user_can_list_posts(self):
            self.client.force_authenticate(user=self.user)
            baker.make('ForumPost', course=self.course, _quantity=3)
            
            response = self.client.get(f'/DzSkills/courses/{self.course.id}/posts/')
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 3

    class TestCreate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.course = baker.make('Course')

        def test_authenticated_user_can_create_post(self):
            
            self.client.force_authenticate(user=self.user)
            
            response = self.client.post(f'/DzSkills/courses/{self.course.id}/posts/', {
                'title': 'New Post',
                'content': 'Post content'
            })
            
            assert response.status_code == status.HTTP_201_CREATED
            
        def test_anonymous_user_can_not_create_post(self):
            
            self.client.logout()
            
            response = self.client.post(f'/DzSkills/courses/{self.course.id}/posts/', {
                'title': 'New Post',
                'content': 'Post content'
            })
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
            
    class TestUpdate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.course = baker.make('Course')
            self.post = baker.make('ForumPost', course=self.course, user=self.user)

        def test_author_can_update_post(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.patch(f'/DzSkills/courses/{self.course.id}/posts/{self.post.id}/', {
                'title': 'Updated Post',
                'content': 'Updated content'
            })
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['title'] == 'Updated Post'

        def test_non_author_cannot_update_post(self):
            other_user = baker.make(User)
            self.client.force_authenticate(user=other_user)
            
            response = self.client.patch(f'/DzSkills/courses/{self.course.id}/posts/{self.post.id}/', {
                'title': 'Updated Post'
            })
            
            assert response.status_code == status.HTTP_403_FORBIDDEN

    class TestDelete:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.course = baker.make('Course')
            self.post = baker.make('ForumPost', course=self.course, user=self.user)

        def test_author_can_delete_post(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.delete(f'/DzSkills/courses/{self.course.id}/posts/{self.post.id}/')
            
            assert response.status_code == status.HTTP_204_NO_CONTENT

        def test_non_author_cannot_delete_post(self):
            other_user = baker.make(User)
            self.client.force_authenticate(user=other_user)
            
            response = self.client.delete(f'/DzSkills/courses/{self.course.id}/posts/{self.post.id}/')
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
