from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_connection import connect_to_db

# Flask 애플리케이션 생성
app = Flask(__name__)

# CSV 파일 처리
try:
    df = pd.read_csv('courses.csv')
    df.columns = ['courseName', 'courseDetails', 'courseURL']
    df = df.dropna(subset=['courseName', 'courseDetails']).reset_index(drop=True)
except FileNotFoundError:
    raise Exception("courses.csv 파일을 찾을 수 없습니다. 경로를 확인하세요.")

# 코사인 유사도 계산 함수
def calculate_cosine_similarity(text1, text2, boost_factor=1.5):
    documents = [text1, text2]
    tfidf = TfidfVectorizer().fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return min(cosine_sim * boost_factor, 1.0)

# 동적 job_id 기반 추천 함수
def get_recommended_courses(job_id):
    db_connection = connect_to_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT job_name FROM job WHERE id = %s", (job_id,))
    job_result = cursor.fetchone()
    job_name = job_result['job_name'] if job_result else ""
    query = "SELECT course_id, course_details, course_name, grade_score FROM school_course"
    cursor.execute(query)
    courses = cursor.fetchall()
    similarities = [
        (calculate_cosine_similarity(course['course_details'], job_name), course)
        for course in courses
    ]
    similarities.sort(reverse=True, key=lambda x: x[0])
    top_courses = [course for _, course in similarities[:5]]
    cursor.close()
    db_connection.close()
    return top_courses

# 경로 1: /recommend-courses
@app.route('/recommend-courses', methods=['POST'])
def recommend_courses_db():
    data = request.get_json()
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"error": "job_id is required."}), 400
    recommended_courses = get_recommended_courses(job_id)
    return jsonify(recommended_courses)

# 경로 2: /recommend
@app.route('/recommend', methods=['POST'])
def recommend_courses_csv():
    data = request.get_json()
    input_name = data.get('courseName', '').strip()
    input_details = data.get('courseDetails', '').strip()
    if not input_name or not input_details:
        return jsonify({"error": "Invalid input. 'courseName' and 'courseDetails' must be non-empty."}), 400
    df['combined'] = df['courseName'].fillna('') + " " + df['courseDetails'].fillna('')
    input_text = input_name + " " + input_details
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['combined'].tolist() + [input_text])
    input_vector = tfidf_matrix[-1]
    cosine_similarities = cosine_similarity(input_vector, tfidf_matrix[:-1]).flatten()
    df['similarity'] = cosine_similarities
    top_courses = df.sort_values(by='similarity', ascending=False).head(3)
    result = top_courses[['courseName', 'courseDetails', 'courseURL', 'similarity']].to_dict(orient='records')
    return jsonify(result)

# 경로 3: /recommend/random
@app.route('/recommend/random', methods=['POST'])
def recommend_courses_csv():
    data = request.get_json()
    input_name = data.get('courseName', '').strip()
    input_details = data.get('courseDetails', '').strip()

    if not input_name or not input_details:
        return jsonify({"error": "Invalid input. 'courseName' and 'courseDetails' must be non-empty."}), 400

    # 데이터 병합
    df['combined'] = df['courseName'].fillna('') + " " + df['courseDetails'].fillna('')
    input_text = input_name + " " + input_details

    # TF-IDF 벡터화
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['combined'].tolist() + [input_text])
    input_vector = tfidf_matrix[-1]
    cosine_similarities = cosine_similarity(input_vector, tfidf_matrix[:-1]).flatten()

    # 유사도 계산 및 상위 20개 추출
    df['similarity'] = cosine_similarities
    top_courses = df.sort_values(by='similarity', ascending=False).head(20)

    # 상위 20개 중 랜덤으로 3개 선택
    random_courses = top_courses.sample(n=3)

    # 결과 JSON 생성
    result = random_courses[['courseName', 'courseDetails', 'courseURL', 'similarity']].to_dict(orient='records')
    return jsonify(result)

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)
