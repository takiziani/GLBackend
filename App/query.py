
def get_instructor_by_user_id(user_id):
    return """
    SELECT * FROM core_instructor WHERE user_id = %s
    """

def get_student_by_user_id(user_id):
    return """
    SELECT * FROM core_student WHERE user_id = %s
    """

def get_enrolled_courses(student_id):
    return """
    SELECT c.* FROM core_course c
    INNER JOIN core_enrollment e ON c.id = e.course_id
    INNER JOIN core_instructor i ON c.instructor_id = i.id 
    INNER JOIN auth_user u ON i.user_id = u.id
    WHERE e.student_id = %s
    """

def get_all_courses():
    return """
    SELECT c.* FROM core_course c
    INNER JOIN core_instructor i ON c.instructor_id = i.id
    """

def get_course_contents_by_course(course_id):
    return """
    SELECT cc.* FROM core_coursecontent cc
    WHERE cc.course_id = %s
    """

def get_course_by_instructor(instructor_id):
    return """
    SELECT * FROM core_course 
    WHERE instructor_id = %s
    """

def get_quiz_by_course_content(content_id):
    return """
    SELECT * FROM core_quiz
    WHERE course_content_id = %s
    """

def get_quiz_questions(quiz_id):
    return """
    SELECT * FROM core_quizquestion
    WHERE quiz_id = %s
    """

def get_forum_posts_by_course(course_id):
    return """
    SELECT * FROM core_forumpost
    WHERE course_id = %s
    """

def get_forum_comments_by_post(post_id):
    return """
    SELECT * FROM core_forumpostcomment
    WHERE post_id = %s
    """

def check_enrollment(student_id, course_id):
    return """
    SELECT EXISTS(
        SELECT 1 FROM core_enrollment
        WHERE student_id = %s AND course_id = %s
    )
    """

def get_student_progress(student_id, course_id):
    return """
    SELECT * FROM core_studentprogress
    WHERE student_id = %s AND course_id = %s
    """

def get_course_content_count(course_id):
    return """
    SELECT COUNT(*) FROM core_coursecontent 
    WHERE course_id = %s
    """

def get_watched_content_count(student_id, course_id):
    return """
    SELECT COUNT(*) FROM core_studentprogress
    WHERE student_id = %s AND course_id = %s
    """

def get_certificate(student_id, course_id):
    return """
    SELECT * FROM core_certificate
    WHERE student_id = %s AND course_id = %s
    """

def check_student_subscription(student_id):
    return """
    SELECT EXISTS(
        SELECT 1 FROM core_studentsubscription
        WHERE student_id = %s 
        AND end_date > CURRENT_TIMESTAMP
    )
    """