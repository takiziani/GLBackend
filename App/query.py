import psycopg2
from psycopg2.extras import RealDictCursor
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from psycopg2 import errors
from uuid import uuid4
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta


class InstructorQueries:
    @classmethod
    def _get_db_connection(cls):
        """Establish a database connection."""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def create_instructor(cls, user_id, data):
        """Create a new instructor."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Insert into instructor table
                cursor.execute("""
                    INSERT INTO instructor (user_id, first_name, last_name, bio, expertise)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    user_id, 
                    data.get('first_name', ''), 
                    data.get('last_name', ''), 
                    data.get('bio', ''), 
                    data.get('expertise', '')
                ))
                instructor = cursor.fetchone()
                conn.commit()
                return instructor
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def get_all_instructors(cls):
        """Retrieve all instructors."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, first_name, last_name, bio, expertise 
                    FROM instructor
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def get_instructor_by_id(cls, instructor_id):
        """Retrieve a specific instructor by ID."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, first_name, last_name, bio, expertise 
                    FROM instructor 
                    WHERE id = %s
                """, (instructor_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @classmethod
    def get_or_create_instructor(cls, user_id):
        """Get or create an instructor for a user."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # First, try to find existing instructor
                cursor.execute("""
                    SELECT * FROM instructor 
                    WHERE user_id = %s
                """, (user_id,))
                instructor = cursor.fetchone()

                # If not found, create a new instructor
                if not instructor:
                    cursor.execute("""
                        INSERT INTO instructor (user_id) 
                        VALUES (%s) 
                        RETURNING *
                    """, (user_id,))
                    instructor = cursor.fetchone()
                    conn.commit()

                return instructor
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def update_instructor(cls, instructor_id, data):
        """Update an existing instructor."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Prepare the update query dynamically based on provided data
                update_fields = []
                values = []
                for key, value in data.items():
                    if key in ['first_name', 'last_name', 'bio', 'expertise']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                values.append(instructor_id)
                
                if update_fields:
                    query = f"""
                        UPDATE instructor 
                        SET {', '.join(update_fields)}
                        WHERE id = %s
                        RETURNING *
                    """
                    cursor.execute(query, values)
                    updated_instructor = cursor.fetchone()
                    conn.commit()
                    return updated_instructor
                return None
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def delete_instructor(cls, instructor_id):
        """Delete an instructor."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM instructor 
                    WHERE id = %s
                """, (instructor_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()
            
        
class StudentQueries:
    @classmethod
    def _get_db_connection(cls):
        """Establish a database connection."""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )


    @classmethod
    def get_student_by_id(cls, student_id):
        """
        Retrieve a student by ID
        
        Args:
            student_id (int): Student's primary key
        
        Returns:
            dict: Student details
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.*, u.email, u.username 
                    FROM student s
                    JOIN auth_user u ON s.user_id = u.id
                    WHERE s.id = %s
                """, (student_id,))
                return cur.fetchone()
    
    @classmethod
    def get_student_by_user_id(cls, user_id):
        """
        Retrieve a student by user ID.
        
        Args:
            user_id (int): ID of the user
        
        Returns:
            dict: Student details
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM student 
                    WHERE user_id = %s
                """, (user_id,))
                student = cur.fetchone()
                
                # Optionally create student if not exists
                if not student:
                    cur.execute("""
                        INSERT INTO student (user_id, created_at) 
                        VALUES (%s, NOW()) 
                        RETURNING *
                    """, (user_id,))
                    conn.commit()
                    student = cur.fetchone()
                
                return student
    
    
    @classmethod
    def create_student(cls, user_id, data):
        """Create a new student."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Insert into student table
                cursor.execute("""
                    INSERT INTO student (user_id, first_name, last_name, major, graduation_year)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    user_id, 
                    data.get('first_name', ''), 
                    data.get('last_name', ''), 
                    data.get('major', ''), 
                    data.get('graduation_year')
                ))
                student = cursor.fetchone()
                conn.commit()
                return student
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def get_or_create_student(cls, user_id):
        """Get or create a student for a user."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # First, try to find existing student
                cursor.execute("""
                    SELECT * FROM student 
                    WHERE user_id = %s
                """, (user_id,))
                student = cursor.fetchone()

                # If not found, create a new student
                if not student:
                    cursor.execute("""
                        INSERT INTO student (user_id) 
                        VALUES (%s) 
                        RETURNING *
                    """, (user_id,))
                    student = cursor.fetchone()
                    conn.commit()

                return student
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def update_student(cls, student_id, data):
        """Update an existing student."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Prepare the update query dynamically based on provided data
                update_fields = []
                values = []
                for key, value in data.items():
                    if key in ['first_name', 'last_name', 'major', 'graduation_year']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                values.append(student_id)
                
                if update_fields:
                    query = f"""
                        UPDATE student 
                        SET {', '.join(update_fields)}
                        WHERE id = %s
                        RETURNING *
                    """
                    cursor.execute(query, values)
                    updated_student = cursor.fetchone()
                    conn.commit()
                    return updated_student
                return None
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def get_enrolled_courses(cls, student_id):
        """Get courses enrolled by a student."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get enrolled courses
                cursor.execute("""
                    SELECT c.* 
                    FROM course c
                    JOIN enrollment e ON c.id = e.course_id
                    WHERE e.student_id = %s
                """, (student_id,))
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def check_student_subscription(cls, student_id):
        """Check if student has an active subscription."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT EXISTS(
                         SELECT select * from "App_studentsubscription" where CURRENT_DATE between 
                        "App_studentsubscription"."start_date" and "App_studentsubscription"."end_date" 
                        and "student_id" = %s 
                    ) as is_subscribed
                """, (student_id,))
                return cursor.fetchone()['is_subscribed']
        finally:
            conn.close()
            
            
    @classmethod
    def check_enrollment(cls, student_id, course_id):
        """
        Check if a student is enrolled in a course.
        
        Args:
            student_id (int): ID of the student
            course_id (int): ID of the course
        
        Returns:
            bool: Enrollment status
        """
        with cls.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM enrollment 
                        WHERE student_id = %s AND course_id = %s
                    )
                """, (student_id, course_id))
                return cur.fetchone()[0]


class HomeCourseQueries:
    @classmethod
    def _get_db_connection(cls):
        """Establish a database connection."""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_all_courses(cls):
        """Retrieve all courses with instructor details."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        *
                    FROM 
                        "App_course" c
                    JOIN 
                        "App_instructor" i ON c.instructor_id = i.id
                    JOIN 
                        "App_user" u ON i.user_id = u.id
                    ORDER BY 
                        c.created_at DESC
                """)
                return cursor.fetchall()
        finally:
            conn.close()


class HomeCourseContentQueries:
    @classmethod
    def _get_db_connection(cls):
        """Establish a database connection."""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_course_contents(cls, course_pk):
        """Retrieve course contents for a specific course."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        *
                    FROM 
                        "App_course_content"
                    WHERE 
                        course_id = %s
                    ORDER BY 
                        order_index
                """, (course_pk,))
                return cursor.fetchall()
        finally:
            conn.close()

class CourseQueries:
    @classmethod
    def _get_db_connection(cls):
        """Establish a database connection."""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_courses_by_instructor(cls, instructor_pk):
        """Retrieve courses for a specific instructor."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        c.id, 
                        c.title, 
                        c.description, 
                        c.price, 
                        c.level,
                        c.instructor_id,
                        i.user_id as instructor_user_id
                    FROM 
                        course c
                    JOIN 
                        instructor i ON c.instructor_id = i.id
                    WHERE 
                        c.instructor_id = %s
                """, (instructor_pk,))
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def create_course(cls, instructor_id, data):
        """Create a new course for an instructor."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO course 
                    (title, description, price, level, instructor_id) 
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    data.get('title', ''),
                    data.get('description', ''),
                    data.get('price', 0),
                    data.get('level', ''),
                    instructor_id
                ))
                course = cursor.fetchone()
                conn.commit()
                return course
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def update_course(cls, course_id, data):
        """Update an existing course."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                update_fields = []
                values = []
                for key, value in data.items():
                    if key in ['title', 'description', 'price', 'level']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                values.append(course_id)
                
                if update_fields:
                    query = f"""
                        UPDATE course 
                        SET {', '.join(update_fields)}
                        WHERE id = %s
                        RETURNING *
                    """
                    cursor.execute(query, values)
                    updated_course = cursor.fetchone()
                    conn.commit()
                    return updated_course
                return None
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def delete_course(cls, course_id):
        """Delete a course."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM course 
                    WHERE id = %s
                """, (course_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def get_course_by_pk(cls, course_pk):
        """
        Retrieve a course by its primary key.
        
        Args:
            course_pk (int): Primary key of the course
        
        Returns:
            dict: Course details or None
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM course 
                    WHERE id = %s
                """, (course_pk,))
                course = cur.fetchone()
                
                if not course:
                    raise ObjectDoesNotExist(f"Course with id {course_pk} does not exist")
                
                return course

class CourseContentQueries:
    @classmethod
    def _get_db_connection(cls):
        """Establish a database connection."""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_course_contents(cls, course_pk):
        """Retrieve course contents with associated quizzes."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Retrieve course contents
                cursor.execute("""
                    SELECT 
                        cc.id, 
                        cc.course_id, 
                        cc.title, 
                        cc.description, 
                        cc.content_type, 
                        cc.video_url, 
                        cc.duration, 
                        cc.order_index,
                        (SELECT json_agg(
                            json_build_object(
                                'id', q.id,
                                'title', q.title,
                                'description', q.description
                            )
                        ) FROM quiz q WHERE q.course_content_id = cc.id) as quizzes
                    FROM 
                        course_content cc
                    WHERE 
                        cc.course_id = %s
                    ORDER BY 
                        cc.order_index
                """, (course_pk,))
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def check_course_access(cls, user_id, course_pk):
        """Check user's access to course content."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if user is the instructor
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 
                        FROM course c
                        JOIN instructor i ON c.instructor_id = i.id
                        WHERE i.user_id = %s AND c.id = %s
                    ) as is_instructor
                """, (user_id, course_pk))
                is_instructor = cursor.fetchone()['is_instructor']

                # Check if student is enrolled
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 
                        FROM enrollment e
                        JOIN student s ON e.student_id = s.id
                        WHERE s.user_id = %s AND e.course_id = %s
                    ) as is_enrolled
                """, (user_id, course_pk))
                is_enrolled = cursor.fetchone()['is_enrolled']

                # Check if student has an active subscription
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 
                        FROM student_subscription ss
                        JOIN student s ON ss.student_id = s.id
                        WHERE s.user_id = %s AND ss.is_active = TRUE
                    ) as is_subscribed
                """, (user_id,))
                is_subscribed = cursor.fetchone()['is_subscribed']

                return {
                    'is_instructor': is_instructor,
                    'is_enrolled': is_enrolled,
                    'is_subscribed': is_subscribed
                }
        finally:
            conn.close()

    @classmethod
    def create_course_content(cls, course_id, data):
        """Create new course content."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO course_content 
                    (course_id, title, description, content_type, video_url, duration, order_index)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    course_id,
                    data.get('title', ''),
                    data.get('description', ''),
                    data.get('content_type', ''),
                    data.get('video_url', ''),
                    data.get('duration', 0),
                    data.get('order_index', 0)
                ))
                course_content = cursor.fetchone()
                conn.commit()
                return course_content
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def update_course_content(cls, content_id, data):
        """Update existing course content."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                update_fields = []
                values = []
                for key, value in data.items():
                    if key in ['title', 'description', 'content_type', 'video_url', 'duration', 'order_index']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                values.append(content_id)
                
                if update_fields:
                    query = f"""
                        UPDATE course_content 
                        SET {', '.join(update_fields)}
                        WHERE id = %s
                        RETURNING *
                    """
                    cursor.execute(query, values)
                    updated_content = cursor.fetchone()
                    conn.commit()
                    return updated_content
                return None
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def delete_course_content(cls, content_id):
        """Delete course content."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM course_content 
                    WHERE id = %s
                """, (content_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()


class QuizQueries:
    @classmethod
    def _get_db_connection(cls):
        """Establish a database connection."""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_quizzes_by_course_content(cls, course_content_pk):
        """Retrieve quizzes for a specific course content."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM quiz 
                    WHERE course_content_id = %s
                """, (course_content_pk,))
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def get_quiz_questions(cls, quiz_pk, user_id, course_content_pk, course_pk):
        """Retrieve quiz questions with access control."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if course content is free preview
                cursor.execute("""
                    SELECT is_free_preview 
                    FROM course_content 
                    WHERE id = %s
                """, (course_content_pk,))
                is_free = cursor.fetchone()['is_free_preview']

                if is_free:
                    # If free preview, return all questions
                    cursor.execute("""
                        SELECT * FROM quiz_question 
                        WHERE quiz_id = %s
                    """, (quiz_pk,))
                    return cursor.fetchall()

                # Check if user is course instructor
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1 
                        FROM course c
                        JOIN instructor i ON c.instructor_id = i.id
                        WHERE c.id = %s AND i.user_id = %s
                    ) as is_instructor
                """, (course_pk, user_id))
                is_instructor = cursor.fetchone()['is_instructor']

                if is_instructor:
                    # Instructor can see all questions
                    cursor.execute("""
                        SELECT * FROM quiz_question 
                        WHERE quiz_id = %s
                    """, (quiz_pk,))
                    return cursor.fetchall()

                # Check student enrollment or subscription
                cursor.execute("""
                    WITH student_check AS (
                        SELECT s.id as student_id
                        FROM student s
                        WHERE s.user_id = %s
                    )
                    SELECT 
                        EXISTS(
                            SELECT 1 
                            FROM enrollment e, student_check sc
                            WHERE e.student_id = sc.student_id 
                            AND e.course_id = %s
                        ) as is_enrolled,
                        EXISTS(
                            SELECT 1 
                            FROM student_subscription ss, student_check sc
                            WHERE ss.student_id = sc.student_id 
                            AND ss.is_active = TRUE
                        ) as is_subscribed
                """, (user_id, course_pk))
                access = cursor.fetchone()

                if access['is_enrolled'] or access['is_subscribed']:
                    # Return questions if enrolled or subscribed
                    cursor.execute("""
                        SELECT * FROM quiz_question 
                        WHERE quiz_id = %s
                    """, (quiz_pk,))
                    return cursor.fetchall()

                # No access, return empty list
                return []
        finally:
            conn.close()

    @classmethod
    def create_quiz(cls, course_content_id, data):
        """Create a new quiz."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO quiz 
                    (course_content_id, title, description)
                    VALUES (%s, %s, %s)
                    RETURNING *
                """, (
                    course_content_id,
                    data.get('title', ''),
                    data.get('description', '')
                ))
                quiz = cursor.fetchone()
                conn.commit()
                return quiz
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def create_quiz_question(cls, quiz_id, data):
        """Create a new quiz question."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO quiz_question 
                    (quiz_id, question_text, explanation, is_multiple_choice)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                """, (
                    quiz_id,
                    data.get('question_text', ''),
                    data.get('explanation', ''),
                    data.get('is_multiple_choice', False)
                ))
                question = cursor.fetchone()
                conn.commit()
                return question
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def delete_quiz(cls, quiz_id):
        """Delete a quiz."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM quiz 
                    WHERE id = %s
                """, (quiz_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def delete_quiz_question(cls, question_id):
        """Delete a quiz question."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM quiz_question 
                    WHERE id = %s
                """, (question_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()


class ForumPostQueries:
    @classmethod
    def _get_db_connection(cls):
        """Establish a database connection."""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_forum_posts_by_course(cls, course_pk):
        """Retrieve forum posts for a specific course."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        fp.id, 
                        fp.title, 
                        fp.content, 
                        fp.created_at, 
                        u.id as user_id,
                        u.username as username,
                        c.id as course_id
                    FROM 
                        forum_post fp
                    JOIN 
                        auth_user u ON fp.user_id = u.id
                    JOIN 
                        course c ON fp.course_id = c.id
                    WHERE 
                        fp.course_id = %s
                    ORDER BY 
                        fp.created_at DESC
                """, (course_pk,))
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def create_forum_post(cls, course_id, user_id, data):
        """Create a new forum post."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO forum_post 
                    (course_id, user_id, title, content)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                """, (
                    course_id,
                    user_id,
                    data.get('title', ''),
                    data.get('content', '')
                ))
                post = cursor.fetchone()
                conn.commit()
                return post
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def update_forum_post(cls, post_id, data):
        """Update an existing forum post."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                update_fields = []
                values = []
                for key, value in data.items():
                    if key in ['title', 'content']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                values.append(post_id)
                
                if update_fields:
                    query = f"""
                        UPDATE forum_post 
                        SET {', '.join(update_fields)}
                        WHERE id = %s
                        RETURNING *
                    """
                    cursor.execute(query, values)
                    updated_post = cursor.fetchone()
                    conn.commit()
                    return updated_post
                return None
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def delete_forum_post(cls, post_id):
        """Delete a forum post."""
        conn = cls._get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM forum_post 
                    WHERE id = %s
                """, (post_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()


class ForumPostCommentQueries:
    @classmethod
    def get_connection(cls):
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_comments_by_post(cls, post_pk):
        """Retrieve comments for a specific post."""
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM forum_post_comment 
                    WHERE post_id = %s
                """, (post_pk,))
                return cur.fetchall()

    @classmethod
    def create_comment(cls, post_pk, user_id, comment_data):
        """Create a new comment for a post."""
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Validate post and user exist
                cur.execute("SELECT id FROM forum_post WHERE id = %s", (post_pk,))
                if not cur.fetchone():
                    raise ValueError("Post does not exist")

                cur.execute("SELECT id FROM auth_user WHERE id = %s", (user_id,))
                if not cur.fetchone():
                    raise ValueError("User does not exist")

                # Insert comment
                query = """
                INSERT INTO forum_post_comment 
                (post_id, user_id, content, created_at)
                VALUES (%s, %s, %s, NOW())
                RETURNING *
                """
                cur.execute(query, (
                    post_pk, 
                    user_id, 
                    comment_data.get('content')
                ))
                conn.commit()
                return cur.fetchone()

    @classmethod
    def delete_comment(cls, comment_id, user_id):
        """Delete a comment, ensuring user owns the comment."""
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                DELETE FROM forum_post_comment 
                WHERE id = %s AND user_id = %s
                """
                cur.execute(query, (comment_id, user_id))
                conn.commit()
                return cur.rowcount > 0


class StudentCourseQueries:
    @classmethod
    def get_connection(cls):
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_student_courses(cls, student_pk):
        """
        Retrieve courses for a student based on subscription or enrollment.
        
        Args:
            student_pk (int): Primary key of the student
        
        Returns:
            List of courses
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if student has an active subscription
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM student_subscription 
                        WHERE student_id = %s AND status = 'active'
                    )
                """, (student_pk,))
                is_subscribed = cur.fetchone()['exists']
                
                # If subscribed, return all courses
                if is_subscribed:
                    cur.execute("""
                        SELECT c.*, 
                               u.username AS instructor_username, 
                               u.first_name AS instructor_first_name, 
                               u.last_name AS instructor_last_name
                        FROM course c
                        JOIN instructor i ON c.instructor_id = i.id
                        JOIN auth_user u ON i.user_id = u.id
                    """)
                    return cur.fetchall()
                
                # Otherwise, return enrolled courses
                cur.execute("""
                    SELECT c.*, 
                           u.username AS instructor_username, 
                           u.first_name AS instructor_first_name, 
                           u.last_name AS instructor_last_name
                    FROM course c
                    JOIN enrollment e ON c.id = e.course_id
                    JOIN instructor i ON c.instructor_id = i.id
                    JOIN auth_user u ON i.user_id = u.id
                    WHERE e.student_id = %s
                """, (student_pk,))
                return cur.fetchall()

    @classmethod
    def get_course_progress(cls, student_id, course_id):
        """
        Retrieve student progress for a specific course.
        
        Args:
            student_id (int): ID of the student
            course_id (int): ID of the course
        
        Returns:
            List of progress records
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM student_progress
                    WHERE student_id = %s AND course_id = %s
                """, (student_id, course_id))
                return cur.fetchall()

    @classmethod
    def get_or_create_certificate(cls, student_id, course_id):
        """
        Get or create a certificate for a student's course completion.
        
        Args:
            student_id (int): ID of the student
            course_id (int): ID of the course
        
        Returns:
            Certificate details
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check total and watched content count
                cur.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM course_content WHERE course_id = %s) AS total_content,
                        (SELECT COUNT(*) FROM student_progress WHERE student_id = %s AND course_id = %s) AS watched_content
                """, (course_id, student_id, course_id))
                progress = cur.fetchone()
                
                # Check course completion
                if progress['total_content'] == 0 or (progress['watched_content'] / progress['total_content']) * 100 < 100:
                    return None
                
                # Check if certificate exists
                cur.execute("""
                    SELECT * FROM certificate
                    WHERE student_id = %s AND course_id = %s
                """, (student_id, course_id))
                certificate = cur.fetchone()
                
                # If certificate exists, return it
                if certificate:
                    return certificate
                
                # Create new certificate
                certificate_number = str(uuid4())[:8]
                cur.execute("""
                    INSERT INTO certificate 
                    (student_id, course_id, certificate_number, created_at)
                    VALUES (%s, %s, %s, NOW())
                    RETURNING *
                """, (student_id, course_id, certificate_number))
                conn.commit()
                
                return cur.fetchone()


class StudentCourseContentQueries:
    @classmethod
    def get_connection(cls):
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_course_contents(cls, course_pk, student_pk):
        """
        Retrieve course contents based on student's enrollment or subscription.
        
        Args:
            course_pk (int): Primary key of the course
            student_pk (int): Primary key of the student
        
        Returns:
            List of course contents
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check student subscription
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM student_subscription 
                        WHERE student_id = %s AND status = 'active'
                    )
                """, (student_pk,))
                is_sub = cur.fetchone()['exists']
                
                # Check enrollment
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM enrollment 
                        WHERE student_id = %s AND course_id = %s
                    )
                """, (student_pk, course_pk))
                is_enrolled = cur.fetchone()['exists']
                
                # Retrieve course contents
                if is_sub or is_enrolled:
                    cur.execute("""
                        SELECT * FROM course_content 
                        WHERE course_id = %s 
                        ORDER BY order_index
                    """, (course_pk,))
                else:
                    # If not enrolled or subscribed, return only free preview contents
                    cur.execute("""
                        SELECT * FROM course_content 
                        WHERE course_id = %s AND is_free_preview = true 
                        ORDER BY order_index
                    """, (course_pk,))
                
                return cur.fetchall(), is_enrolled or is_sub

    @classmethod
    def create_course_content_progress(cls, student_pk, course_pk, content_pk):
        """
        Create progress for a course content.
        
        Args:
            student_pk (int): Primary key of the student
            course_pk (int): Primary key of the course
            content_pk (int): Primary key of the course content
        
        Returns:
            Created progress record or None
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    # Validate student, course, and course content
                    cur.execute("""
                        SELECT 
                            (SELECT EXISTS(SELECT 1 FROM student WHERE id = %s)) AS student_exists,
                            (SELECT EXISTS(SELECT 1 FROM course WHERE id = %s)) AS course_exists,
                            (SELECT EXISTS(SELECT 1 FROM course_content WHERE id = %s AND course_id = %s)) AS content_exists,
                            (SELECT EXISTS(SELECT 1 FROM enrollment WHERE student_id = %s AND course_id = %s)) AS is_enrolled
                    """, (student_pk, course_pk, content_pk, course_pk, student_pk, course_pk))
                    validations = cur.fetchone()
                    
                    # Check validations
                    if not all([
                        validations['student_exists'],
                        validations['course_exists'],
                        validations['content_exists'],
                        validations['is_enrolled']
                    ]):
                        return None, "Validation failed"
                    
                    # Check if progress already exists
                    cur.execute("""
                        SELECT EXISTS(
                            SELECT 1 FROM student_progress 
                            WHERE student_id = %s 
                              AND course_id = %s 
                              AND watched_course_content_id = %s
                        )
                    """, (student_pk, course_pk, content_pk))
                    if cur.fetchone()['exists']:
                        return None, "Progress already exists"
                    
                    # Create progress
                    cur.execute("""
                        INSERT INTO student_progress 
                        (student_id, course_id, watched_course_content_id, created_at)
                        VALUES (%s, %s, %s, NOW())
                        RETURNING *
                    """, (student_pk, course_pk, content_pk))
                    conn.commit()
                    
                    return cur.fetchone(), None
                
                except psycopg2.Error as e:
                    conn.rollback()
                    return None, str(e)

    @classmethod
    def check_course_enrollment(cls, student_pk, course_pk):
        """
        Check if a student is enrolled in a course.
        
        Args:
            student_pk (int): Primary key of the student
            course_pk (int): Primary key of the course
        
        Returns:
            Boolean indicating enrollment status
        """
        with cls.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM enrollment 
                        WHERE student_id = %s AND course_id = %s
                    )
                """, (student_pk, course_pk))
                return cur.fetchone()[0]

class StudentQuizQueries:
    @classmethod
    def get_connection(cls):
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_quizzes_by_course_content(cls, course_content_pk):
        """
        Retrieve quizzes for a specific course content.
        
        Args:
            course_content_pk (int): Primary key of the course content
        
        Returns:
            List of quizzes
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM quiz 
                    WHERE course_content_id = %s
                """, (course_content_pk,))
                return cur.fetchall()


class StripeWebhookQueries:
    @classmethod
    def get_connection(cls):
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )

    @classmethod
    def get_student_by_id(cls, student_id):
        """
        Retrieve a student by ID
        
        Args:
            student_id (int): Student's primary key
        
        Returns:
            dict: Student details
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.*, u.email, u.username 
                    FROM student s
                    JOIN auth_user u ON s.user_id = u.id
                    WHERE s.id = %s
                """, (student_id,))
                return cur.fetchone()

    @classmethod
    def create_stripe_payment(cls, student_id, stripe_charge_id, paid_amount, course_price):
        """
        Create a Stripe payment record
        
        Args:
            student_id (int): Student's primary key
            stripe_charge_id (str): Stripe charge ID
            paid_amount (float): Paid amount in dollars
            course_price (float): Course price
        
        Returns:
            dict: Created payment record
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO stripe_payment (
                        student_id, 
                        stripe_charge_id, 
                        paid_amount, 
                        course_price, 
                        timestamp
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    student_id, 
                    stripe_charge_id, 
                    paid_amount, 
                    course_price, 
                    timezone.now()
                ))
                conn.commit()
                return cur.fetchone()

    @classmethod
    def create_enrollment(cls, student_id, course_id, payment_id):
        """
        Create an enrollment record
        
        Args:
            student_id (int): Student's primary key
            course_id (int): Course's primary key
            payment_id (int): Payment record ID
        
        Returns:
            dict: Created enrollment record
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO enrollment (
                        student_id, 
                        course_id, 
                        payment_id
                    ) VALUES (%s, %s, %s)
                    RETURNING *
                """, (student_id, course_id, payment_id))
                conn.commit()
                return cur.fetchone()

    @classmethod
    def get_affiliated_users(cls, student_id):
        """
        Retrieve affiliated users for a student
        
        Args:
            student_id (int): Student's primary key
        
        Returns:
            list: Affiliated user records
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM affiliated_users
                    WHERE affiliated_user_id = %s
                """, (student_id,))
                return cur.fetchall()

    @classmethod
    def get_affiliation_program(cls, affiliation_id):
        """
        Retrieve affiliation program details
        
        Args:
            affiliation_id (int): Affiliation program ID
        
        Returns:
            dict: Affiliation program details
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM affiliation
                    WHERE id = %s
                """, (affiliation_id,))
                return cur.fetchone()

    @classmethod
    def update_affiliated_user(cls, aff_id, boughted, earning):
        """
        Update affiliated user record
        
        Args:
            aff_id (int): Affiliated user record ID
            boughted (bool): Whether the course was bought
            earning (float): Earning amount
        """
        with cls.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE affiliated_users
                    SET boughted = %s, earning = %s
                    WHERE id = %s
                """, (boughted, earning, aff_id))
                conn.commit()

    @classmethod
    def delete_affiliated_user(cls, aff_id):
        """
        Delete affiliated user record
        
        Args:
            aff_id (int): Affiliated user record ID
        """
        with cls.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM affiliated_users
                    WHERE id = %s
                """, (aff_id,))
                conn.commit()

    @classmethod
    def check_student_subscription(cls, student_id):
        """
        Check if student has an active subscription
        
        Args:
            student_id (int): Student's primary key
        
        Returns:
            bool: Subscription status
        """
        with cls.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM student_subscription
                        WHERE student_id = %s 
                        AND end_date > NOW()
                    )
                """, (student_id,))
                return cur.fetchone()[0]

    @classmethod
    def get_existing_subscription(cls, student_id):
        """
        Retrieve existing student subscription
        
        Args:
            student_id (int): Student's primary key
        
        Returns:
            dict: Existing subscription or None
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM student_subscription
                    WHERE student_id = %s
                """, (student_id,))
                return cur.fetchone()

    @classmethod
    def delete_existing_subscription(cls, student_id):
        """
        Delete existing student subscription
        
        Args:
            student_id (int): Student's primary key
        """
        with cls.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM student_subscription
                    WHERE student_id = %s
                """, (student_id,))
                conn.commit()

    @classmethod
    def create_student_subscription(cls, student_id, start_date, end_date):
        """
        Create a new student subscription
        
        Args:
            student_id (int): Student's primary key
            start_date (datetime): Subscription start date
            end_date (datetime): Subscription end date
        
        Returns:
            dict: Created subscription record
        """
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO student_subscription (
                        student_id, 
                        start_date, 
                        end_date
                    ) VALUES (%s, %s, %s)
                    RETURNING *
                """, (student_id, start_date, end_date))
                conn.commit()
                return cur.fetchone()











