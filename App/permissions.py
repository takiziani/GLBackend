from rest_framework.permissions import IsAuthenticated , BasePermission , SAFE_METHODS

from .models import (Instructor, Student , StudentProgress, User ,Course , ForumPost , ForumPostComment )


class IsCourseInstructorOrReadOnly(BasePermission):
    def has_permission (self, request, view) :
        if request and (request.method in SAFE_METHODS):
            return True
        
        
        
        else:
            course_pk = None
            for key in ['pk', 'course_pk']:
                if key in view.kwargs:
                    course_pk = int(view.kwargs[key])
                    
            inst_pk = None
            for key in ['pk', 'instructor_pk']:
                if key in view.kwargs:
                    inst_pk = int(view.kwargs[key])
            instructor = Instructor.objects.filter(user = request.user).last()
            
            if not instructor:
                return False
            
            if (request.method == 'POST' and (instructor.pk == inst_pk)):
                return True
            
            if(instructor and course_pk):
                return Course.objects.filter(pk = course_pk , instructor_id = instructor.pk).exists()
            else:
                return False


class IsInstructorOrReadOnly(BasePermission):
    def has_permission (self, request, view) :
        if (request) and ( request.method in SAFE_METHODS ):
            return True
        else:            
            is_instructor = Instructor.objects.filter(user = request.user).exists()
            if(is_instructor):
                return True
            else:
                return False


class IsStudent(BasePermission):
    def has_permission (self, request, view) :
        print("the request method is :: " , request.method )
        ## verify the current user student does not access information of other students
        
        if getattr(view, 'action', None) == 'me' or getattr(view, 'action', None) == 'courses' :
            return True
        
        
        student = Student.objects.filter(user = request.user).last()
        

        
        student_pk = None
        
        
        for key in ['pk', 'student_pk']:
            if key in view.kwargs:
                student_pk = int(view.kwargs[key])
        
        
        if((student)):   
            if ((student.pk==student_pk)):
                
                return True
            else:
                
                return False
        else:
            return False
        
class IsExistStudentForUser(BasePermission):
    def has_permission (self, request, view) :
        
        return Student.objects.filter(user = request.user).exists()
        
class IsUserPost(BasePermission):
    def has_permission (self, request, view) :
       
        
        if(request.method in ['PUT' , 'DELETE' , 'PATCH']  ):
            current_user = request.user
            post_pk = view.kwargs.get('pk')
            print(post_pk)
            b = ForumPost.objects.filter(pk = post_pk , user = current_user).exists()
            print("b:::", b)
            return b
        
        
        return True
        
        
class IsUserComment(BasePermission):
    def has_permission (self, request, view) :
       
        
        if(request.method in ['PUT' , 'DELETE' , 'PATCH']  ):
            current_user = request.user
            comment_pk = view.kwargs.get('pk')
            print(comment_pk)
            b = ForumPostComment.objects.filter(pk = comment_pk , user = current_user).exists()
            print("b:::", b)
            return b
        
        
        return True
        
        
        
class IsCourseStudent(BasePermission):
    def has_permission (self, request, view) :
        
        student = Student.objects.filter(user = request.user).last()
        student_pk = view.kwargs.get('pk') 
        #print("student ::: " , student)
        if((student)):   
            student_pk = int(student_pk)    
            if ((student.pk==student_pk)):
                
                return True
            else:
                
                return False
        else:
            return False

