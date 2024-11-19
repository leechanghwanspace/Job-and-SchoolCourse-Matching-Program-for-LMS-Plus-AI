# course_similarity.py

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_connection import connect_to_db

def fetch_school_courses():
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT courseName, courseDetails FROM school_course"
    cursor.execute(query)
    courses = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return courses

def calculate_similarity(job_keywords, course_description):
    documents = [job_keywords, course_description]
    count_vectorizer = CountVectorizer().fit_transform(documents)
    vectors = count_vectorizer.toarray()
    cos_sim = cosine_similarity(vectors)
    
    return cos_sim[0][1]  # job_keywords와 course_description 간 유사도 반환
