import base64
from rest_framework import serializers
from .models import  (Instructor, Student, User , Course , CourseContent , Quiz , 
                      StudentProgress , QuizQuestion  , ForumPostComment , ForumPost 
                      , Certificate , Enrollment)
from djoser.serializers import UserCreateSerializer as dj_user_create
from djoser.serializers import UserSerializer as dj_user
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserCreateSerializers(dj_user_create):
    class Meta(dj_user_create.Meta):
        fields = ['id' , 'email' , 'password' , 'username' , 'first_name' , 'last_name'  ]

class UserSerializers(dj_user):
    id = serializers.IntegerField(read_only=True)
    class Meta(dj_user_create.Meta):
        fields = ['id' , 'email'  , 'username' , 'first_name' , 'last_name'  ]


class UpdateUserSerializers(dj_user):
    id = serializers.IntegerField(read_only=True)
    class Meta(dj_user_create.Meta):
        fields = ['id' , 'email'  , 'username' , 'first_name' , 'last_name'  ]


class InstructorSerializer(serializers.ModelSerializer):#read_only=True
    user = UserSerializers(read_only=True)
    class Meta:
        model = Instructor
        fields = ['id',   'biography' , 'user']


class InstructorSerializerSensitive(serializers.ModelSerializer):
    # user = serializers.IntegerField(read_only=True)

    user = UserSerializers(read_only=True)
    class Meta:
        model = Instructor
        fields = ['id',  'user', 'biography', 'bank_Account' ]


class StudentSerializer(serializers.ModelSerializer):
    # user = serializers.IntegerField(read_only=True)

    user = UserSerializers(read_only=True)
    class Meta:
        model = Student
        fields = ['id' , 'user' , 'biography']


class CreteCourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = [
            'id',
            'instructor',
            'title',
            'description',
            'price',
            'thumbnail',
            'created_at',
            'updated_at',
            'duration_hours',
            'language'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at' , 'duration_hours']


class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only = True)
    thumbnail_data = serializers.SerializerMethodField()


    class Meta:
        model = Course
        fields = [
            'id',
            'instructor',
            'title',
            'description',
            'price',
            'thumbnail_data',
            'created_at',
            'updated_at',
            'duration_hours',
            'language'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at' , 'duration_hours']
        """
        you need to add duration field
        """

    def create(self , validated_data):

                   instructor_id  = self.context['instructor_id']
                   iinstructor = Instructor.objects.get(pk = instructor_id)
                   print("\n\n\n\n**************************************" , instructor_id,
                         "n\n\n\n**************************************")
                   return Course.objects.create(instructor = iinstructor , **validated_data)
    def update(self, instance, validated_data):
    # Update instructor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


    def get_thumbnail_data(self, instance):
        if instance.thumbnail and instance.thumbnail.storage.exists(instance.thumbnail.name):
            try:
                with instance.thumbnail.open('rb') as file:
                    return base64.b64encode(file.read()).decode('utf-8')
            except Exception:
                return None
        return None

class CourseContentSerializer(serializers.ModelSerializer):
    """Serializer for CourseContent model"""
    content_data = serializers.SerializerMethodField()
    content_data_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = CourseContent
        fields = [
            'id',
            'title',
            'content_type',
            'content_data_file',  # For upload
            'content_data',  
            'uploaded_at',
            'duration_minutes',
            'is_free_preview'
        ]
        read_only_fields = ['uploaded_at']
        
        
    def create(self, validated_data):
        course_id = self.context['course_id']
        course = Course.objects.get(pk=course_id)
        
        # Safely get request from context
        request = self.context.get('request')
        
        # Use get method with default None
        content_data = request.data.get('content_data') if request else None
        content_type = validated_data.get('content_type')
        
        if content_data:
            import base64
            from django.core.files.base import ContentFile
            
            format, imgstr = content_data.split(';base64,')
            ext = content_type.lower()  # Use content_type as extension
            
            content_data_file = ContentFile(
                base64.b64decode(imgstr), 
                name=f'content.{ext}'
            )
            
            validated_data['content_data_file'] = content_data_file

        return CourseContent.objects.create(
            course=course, 
            **validated_data
        )
        
        
    def update(self, instance, validated_data):
    # Update instructor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    
    def get_content_data(self, instance):
        # Check if file exists and is accessible
        if instance.content_data_file and instance.content_data_file.storage.exists(instance.content_data_file.name):
            # Read file content based on content type
            try:
                with instance.content_data_file.open('rb') as file:
                    # Base64 encode the file content
                    return base64.b64encode(file.read()).decode('utf-8')
            except Exception as e:
                return None
        return None

        
    

class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    thumbnail = serializers.ImageField(required=False, allow_null=True)
    thumbnail_data = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'instructor',
            'title',
            'description',
            'price',
            'thumbnail',
            'thumbnail_data',
            'created_at',
            'updated_at',
            'duration_hours',
            'language'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'duration_hours']

    def create(self, validated_data):
        instructor_id = self.context['instructor_id']
        instructor = Instructor.objects.get(pk=instructor_id)
        
        # Handle thumbnail upload
        thumbnail = validated_data.pop('thumbnail', None)
        
        course = Course.objects.create(
            instructor=instructor, 
            **validated_data
        )
        
        if thumbnail:
            course.thumbnail = thumbnail
            course.save()
        
        return course

    def update(self, instance, validated_data):
        # Handle thumbnail update
        thumbnail = validated_data.pop('thumbnail', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if thumbnail:
            instance.thumbnail = thumbnail
        
        instance.save()
        return instance

    def get_thumbnail_data(self, instance):
        if instance.thumbnail and instance.thumbnail.storage.exists(instance.thumbnail.name):
            try:
                with instance.thumbnail.open('rb') as file:
                    return base64.b64encode(file.read()).decode('utf-8')
            except Exception:
                return None
        return None
class StudentCourseSerializer(serializers.ModelSerializer):
    
    
    
    instructor = InstructorSerializer(read_only = True)
    percentage = serializers.SerializerMethodField()
    thumbnail_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id',
            'instructor',
            'title',
            'description',
            'price',
            'thumbnail_data',
            'created_at',
            'updated_at',
            'duration_hours',
            'language',
            'percentage'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at' , 'duration_hours']
        """
        you need to add duration field
        """
    def get_percentage(self, instance):
        student_pk = self.context.get('student_pk')  # Get student_pk from the context
        course_pk = instance.id  # Use the instance's id for course_pk
        
        # Ensure the required fields are present
        if not student_pk:
            return 0  
        
        # Calculate percentage
        content_count = CourseContent.objects.filter(course_id=course_pk).count()
        if content_count == 0:  # Avoid division by zero
            return 0
        
        watched_content_count = StudentProgress.objects.filter(
            student_id=student_pk, 
            course_id=course_pk
        ).count()
        
        return (watched_content_count / content_count) * 100
    
    def get_thumbnail_data(self, instance):
        if instance.thumbnail and instance.thumbnail.storage.exists(instance.thumbnail.name):
            try:
                with instance.thumbnail.open('rb') as file:
                    return base64.b64encode(file.read()).decode('utf-8')
            except Exception:
                return None
        return None

class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model"""

    class Meta:
        model = Quiz
        fields = [
            'id',
            'course_content',
            'title',
            'created_at'
        ]
        read_only_fields = ['created_at' ,  'course_content']

    def create(self , validated_data ):
                   course_content_id  = self.context['course_content_id']
                   course_content = CourseContent.objects.get(pk = course_content_id)
                   return Quiz.objects.create(course_content = course_content , **validated_data)
    def update(self, instance, validated_data):
    # Update instructor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer for QuizQuestion model"""
    quiz = QuizSerializer(read_only=True)
    class Meta:
        model = QuizQuestion
        fields = [
            'id',
            'quiz',
            'question_text',
            'possible_answers',
            'correct_answer'
        ]
        


    def create(self , validated_data):
                   quiz_id  = self.context['quiz_id']
                   quiz = Quiz.objects.get(pk = quiz_id)
                   return QuizQuestion.objects.create(quiz = quiz , **validated_data)

    def update(self, instance, validated_data):
    # Update instructor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance




class StudentQuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer for QuizQuestion model"""
    quiz = QuizSerializer(read_only=True)
    class Meta:
        model = QuizQuestion
        fields = [
            'id',
            'quiz',
            'question_text',
            'possible_answers',
            'correct_answer'
        ]


class StudentQuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model"""

    class Meta:
        model = Quiz
        fields = [
            'id',
            'course_content',
            'title',
            'created_at'
        ]
        read_only_fields = ['created_at' ,  'course_content']


class UnEnrolledStudentCourseContentSerializer(serializers.ModelSerializer):
    """Serializer for CourseContent model"""
    content_data_file = serializers.FileField(required=False)
    quizzes = StudentQuizSerializer(read_only=True)
    class Meta:
        model = CourseContent
        fields = [
            'id',
            'title',
            'content_type',
            'uploaded_at',
            'duration_minutes',
            'content_data_file',
            'is_free_preview',
            'quizzes'
        ]
        read_only_fields = ['uploaded_at']        

    
    

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)

        # Remove content_data_file if the content is not free preview
        if not instance.is_free_preview:
            representation.pop('content_data_file', None)
            representation.pop('quizzes', None)

        return representation


class StudentCourseContentSerializer(serializers.ModelSerializer):
    """Serializer for CourseContent model"""
    content_data = serializers.SerializerMethodField()
    is_in_progress = serializers.SerializerMethodField()
    quizzes = StudentQuizSerializer(read_only=True)
    class Meta:
        model = CourseContent
        fields = [
            'id',
            'title',
            'content_type',
            'uploaded_at',
            'duration_minutes',
             'content_data',
            'is_free_preview',
            'is_in_progress',
            'quizzes'
        ]
        read_only_fields = ['uploaded_at']        

    def get_is_in_progress(self, instance):
        """
        Determines if the course content is in the student's progress.
        """
        request = self.context.get('request')  # Get the request from the serializer context
        student_pk = self.context.get('student_pk')  # Pass the student_pk through context
        
        if not request or not student_pk:
            return False  # Default to False if request or student_pk is missing

        # Check if this course content exists in the student's progress
        return StudentProgress.objects.filter(
            student_id=student_pk,
            watched_course_content=instance
        ).exists()
        
        
    def get_content_data(self, instance):
        # Check if file exists and is accessible
        if instance.content_data_file and instance.content_data_file.storage.exists(instance.content_data_file.name):
            # Read file content based on content type
            try:
                with instance.content_data_file.open('rb') as file:
                    # Base64 encode the file content
                    return base64.b64encode(file.read()).decode('utf-8')
            except Exception as e:
                return None
        return None

    # def to_representation(self, instance):
    #     # Get the default representation
    #     representation = super().to_representation(instance)

    #     # Remove content_data_file if the content is not free preview
    #     if not instance.is_free_preview:
    #         representation.pop('content_data_file', None)

    #     return representation




class StudentProgressSerializer(serializers.ModelSerializer):
    class Meta:
        watched_course_content = CourseContentSerializer(read_only = True)
        course = CourseSerializer(read_only = True)
        model = StudentProgress
        fields = [
            'id', 
            'student', 
            'course', 
            'watched_course_content', 
        ]

# class ForumPostSerializer(serializers.ModelSerializer):
#     """Serializer for QuizQuestion model"""
#     class Meta:
#         user = UserSerializers()
#         model = QuizQuestion
#         fields = [
#             'id',
#             'course',
#             'user',
#             'created_at',
#             'content'
#         ]
#         read_only_fields = ['created_at' ,  'id' , 'course' ]

#     def create(self , validated_data):
#                    course_id  = self.context['course_id']
#                    course = Course.objects.get(pk = course_id)
#                    #user= user
#                    print("\n\n\n\n**************************************" , course_id,
#                          "n\n\n\n**************************************")
#                    return ForumPost.objects.create(course = course , **validated_data)
#     def update(self, instance, validated_data):
#     # Update instructor fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()
#         return instance


class ForumPostSerializer(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)
    
    class Meta:
        model = ForumPost
        fields = ['id', 'course', 'title', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at' ,  'id' , 'course' , 'user' , 'updated_at']



class ForumPostCommentSerializer(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)
    post = ForumPostSerializer(read_only=True)
    
    class Meta:
        model = ForumPostComment
        fields = ['id', 'post', 'user', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['created_at' , 'id' , 'updated_at']


class CertificateSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)  # Displays the string representation of the student
    course = serializers.StringRelatedField(read_only=True)   # Displays the string representation of the course

    class Meta:
        model = Certificate
        fields = [
            'id', 
            'student', 
            'course', 
            'certificate_number', 
            'issue_date'
        ]
        read_only_fields = ['id', 'issue_date', 'certificate_number']


class CourseContentWithQuizSerializer(serializers.ModelSerializer):
    """Serializer for CourseContent model"""
    quizzes = QuizSerializer(read_only=True)
    class Meta:
        model = CourseContent
        fields = [
            'id',
            'title',
            'content_type',
            'content_data_file',
            'uploaded_at',
            'duration_minutes',
            'is_free_preview',
            'quizzes'
        ]
        read_only_fields = ['uploaded_at']
        
        
    def create(self , validated_data):
                   course_id  = self.context['course_id']
                   course = Course.objects.get(pk = course_id)
                   print("\n\n\n\n**************************************" , course_id,
                         "n\n\n\n**************************************")
                   return CourseContent.objects.create(course = course , **validated_data)
    def update(self, instance, validated_data):
    # Update instructor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
        


class CreateCheckoutSessionSerializer(serializers.Serializer):
    
    order_id = serializers.IntegerField()
    success_url = serializers.CharField()
    cancel_url = serializers.CharField()
    class Meta:
        fields = ['order_id', 'success_url', 'cancel_url']
        
        
        
class EnrollmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    enrolled_at = serializers.DateTimeField()
    course_id = serializers.IntegerField()
    course_title = serializers.CharField(source='course__title')
    course_price = serializers.DecimalField(source='course__price', max_digits=10, decimal_places=2)
    instructor_id = serializers.IntegerField(source='course__instructor_id')
    instructor_bank_account = serializers.CharField(source='course__instructor__bank_Account')
    user_id = serializers.IntegerField(source='course__instructor__user_id')
    user_first_name = serializers.CharField(source='course__instructor__user__first_name')
    user_last_name = serializers.CharField(source='course__instructor__user__last_name')
    user_username = serializers.CharField(source='course__instructor__user__username')
    month_year = serializers.CharField()  # Include the month_year field
    class Meta:
        model = Enrollment
        fields = [
            'id', 
            'enrolled_at',
            'course_id', 
            'title', 
            'price',
            'bank_Account',
            'first_name',
            'last_name',
            'username'
        ]
        
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user_id = user.id
        
        # Check if the user is an instructor
        if Instructor.objects.filter(user_id=user_id).exists():
            role = 'instructor'
        # Check if the user is a student
        elif Student.objects.filter(user_id=user_id).exists():
            role = 'student'
        else:
            role = 'user'
        
        data['role'] = role
        return data


