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
class TestQuizQuestionsViewSet:
    class TestList:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make(Instructor , user = self.user)
            self.course = baker.make(Course , instructor = self.instructor )
            self.content = baker.make(CourseContent, content_type = 'quiz' ,is_free_preview= False ,course=self.course)
            self.quiz = baker.make(Quiz, course_content=self.content)
            self.questions  = baker.make(QuizQuestion , quiz = self.quiz ,_quantity=3 )

        def test_if_user_is_anonymous_return_401(self):
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/quiz/{self.quiz.id}/questions/')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_unenrolled_student_return_empty_array(self):
            
            other_user = baker.make(User)
            student = baker.make(Student ,  user = other_user)
            
            self.client.force_authenticate(user=other_user)
            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/quiz/{self.quiz.id}/questions/')
            
            assert response.status_code == status.HTTP_200_OK
            # verify empty array
            assert response.data == []

        def test_enrolled_student_can_list_quiz_questions(self):
            
            
            other_user = baker.make(User)
            student = baker.make(Student ,  user = other_user)
            baker.make(Enrollment , student = student , course  = self.course)
            
            self.client.force_authenticate(user=other_user)
                    
            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/quiz/{self.quiz.id}/questions/')
            
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 3
            
        
            
        def test_student_with_subscription_can_list_quiz_questions(self):
            other_user = baker.make(User)
            student = baker.make(Student ,  user = other_user)
            s = baker.make(StudentSubscription , student = student ,start_date = timezone.now(), 
                           end_date = (timezone.now() + timedelta(days=120))  )
            
            
            self.client.force_authenticate(user=other_user)
            
            response = self.client.get(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/quiz/{self.quiz.id}/questions/')
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 3
        
        
    class TestCreate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)
            self.content = baker.make('CourseContent', course=self.course ,  content_type = 'quiz')
            self.quiz = baker.make(Quiz, course_content=self.content)
            
            
        def test_instructor_can_create_quiz_questions(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.post(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/quiz/{self.quiz.id}/questions/', {
                "question_text": "What is the correct file extension for Python files?",
                "possible_answers": [
                    "a) .py",
                    "b) .python",
                    "c) .pyth",
                    "d) .pyt"
                ],
                "correct_answer": "a) .py"
                    } , format='json')

            assert response.status_code == status.HTTP_201_CREATED

        def test_non_instructor_cannot_create_quiz_questions(self):
            other_user = baker.make(User)
            inst = baker.make(Instructor , user = other_user)
            self.client.force_authenticate(user=other_user)
            
            response = self.client.post(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/quiz/{self.quiz.id}/questions/', {
                "question_text": "What is the correct file extension for Python files?",
                "possible_answers": [
                    "a) .py",
                    "b) .python",
                    "c) .pyth",
                    "d) .pyt"
                ],
                "correct_answer": "a) .py"
                    }, format='json')
            
            assert response.status_code == status.HTTP_403_FORBIDDEN

    class TestUpdate:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)
            self.content = baker.make(CourseContent , content_type = 'quiz'  , course=self.course)
            self.quiz = baker.make(Quiz, course_content=self.content)
            self.question  = baker.make(QuizQuestion , quiz = self.quiz  )

        def test_instructor_can_update_quiz_question(self):
            self.client.force_authenticate(user=self.user)

            response = self.client.patch(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/quiz/{self.quiz.id}/questions/{self.question.id}/', {
                'question_text': 'Updated question text'
            })
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['question_text'] == 'Updated question text'

    class TestDelete:
        def setup_method(self):
            self.client = APIClient()
            User = get_user_model()
            self.user = baker.make(User)
            self.instructor = baker.make('Instructor', user=self.user)
            self.course = baker.make('Course', instructor=self.instructor)
            self.content = baker.make('CourseContent' , content_type = 'quiz' , course=self.course)
            self.quiz = baker.make('Quiz', course_content=self.content)
            self.question  = baker.make(QuizQuestion , quiz = self.quiz  )

        def test_instructor_can_delete_quiz_question(self):
            self.client.force_authenticate(user=self.user)
            
            response = self.client.delete(f'/DzSkills/instructors/{self.instructor.id}/courses/{self.course.id}/contents/{self.content.id}/quiz/{self.quiz.id}/questions/{self.question.id}/')
            
            assert response.status_code == status.HTTP_204_NO_CONTENT
