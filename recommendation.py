from db_connection import connect_to_db
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify

# 코사인 유사도 계산 함수
def calculate_cosine_similarity(text1, text2, boost_factor=1.5):
    documents = [text1, text2]
    tfidf = TfidfVectorizer().fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return min(cosine_sim * boost_factor, 1.0)

# 동적 job_id 기반 추천 함수
def get_recommended_courses(job_id):
    # MySQL 연결 설정
    db_connection = connect_to_db()
    cursor = db_connection.cursor(dictionary=True)

    # job_id에 따른 job_name 조회
    cursor.execute("SELECT job_name FROM job WHERE id = %s", (job_id,))
    job_result = cursor.fetchone()
    job_name = job_result['job_name'] if job_result else ""

    # school_course에서 모든 교과목 조회
    query = "SELECT course_id, course_details, course_name, grade_score FROM school_course"
    cursor.execute(query)
    courses = cursor.fetchall()

    # job_name과 각 교과목의 유사도 계산
    similarities = []
    for course in courses:
        similarity = calculate_cosine_similarity(course['course_details'], job_name)
        similarities.append((similarity, course))

    # 유사도 높은 순으로 정렬 후 상위 5개 선택
    similarities.sort(reverse=True, key=lambda x: x[0])
    top_courses = [course for _, course in similarities[:5]]

    # MySQL 연결 닫기
    cursor.close()
    db_connection.close()

    return top_courses

# Flask API 설정
app = Flask(__name__)

@app.route('/recommend-courses', methods=['POST'])
def recommend_courses():
    data = request.get_json()
    job_id = data.get("job_id")
    recommended_courses = get_recommended_courses(job_id)
    return jsonify(recommended_courses)

if __name__ == '__main__':
    app.run(port=5000)