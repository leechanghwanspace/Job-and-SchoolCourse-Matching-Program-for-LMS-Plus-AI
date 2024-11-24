from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db_connection import connect_to_db

# Flask 애플리케이션 생성
app = Flask(__name__)

# CSV 파일 처리
try:
    df = pd.read_csv('./data/courses.csv')
    df.columns = ['inflearnCourseName', 'inflearnCourseDetails', 'courseURL', 'imgURL']
    df = df.dropna(subset=['inflearnCourseName', 'inflearnCourseDetails']).reset_index(drop=True)
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

# 경로 2: /recommend/multiple
@app.route('/recommend/multiple', methods=['POST'])
def recommend_multiple_courses():
    # 입력 데이터 받기
    data = request.get_json()

    # 입력 데이터 유효성 검사
    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"error": "Invalid input. Provide a list of objects with 'courseName' and 'courseDetails'."}), 400

    # 데이터 병합 (NaN 처리 포함)
    df['combined'] = df['inflearnCourseName'].fillna('') + " " + df['inflearnCourseDetails'].fillna('')

    # 결과를 저장할 리스트
    all_recommendations = []

    # TF-IDF 벡터화 객체 생성
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['combined'])

    # 입력 데이터 각각 처리
    for item in data:
        input_name = item.get('courseName', '').strip()
        input_details = item.get('courseDetails', '').strip()

        if not input_name or not input_details:
            all_recommendations.append({
                "input": item,
                "error": "Invalid input. 'courseName' and 'courseDetails' must be non-empty."
            })
            continue

        # 입력 텍스트 벡터화 및 유사도 계산
        input_text = input_name + " " + input_details
        input_vector = vectorizer.transform([input_text])
        cosine_similarities = cosine_similarity(input_vector, tfidf_matrix).flatten()

        # 유사도 계산 및 상위 3개 추출
        df['similarity'] = cosine_similarities
        top_courses = df.sort_values(by='similarity', ascending=False).head(3)

        # 결과 추가
        recommendations = top_courses[['inflearnCourseName', 'inflearnCourseDetails', 'courseURL', 'similarity', 'imgURL']].to_dict(orient='records')
        all_recommendations.append({
            "input": item,
            "recommendations": recommendations
        })

    return jsonify(all_recommendations)

# 경로 3: /recommend/multiple/random
@app.route('/recommend/multiple/random', methods=['POST'])
def recommend_multiple_random_courses():
    # 입력 데이터 받기
    data = request.get_json()

    # 입력 데이터 유효성 검사
    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"error": "Invalid input. Provide a list of objects with 'CourseName' and 'CourseDetails'."}), 400

    # 데이터 병합 (NaN 처리 포함)
    df['combined'] = df['inflearnCourseName'].fillna('') + " " + df['inflearnCourseDetails'].fillna('')

    # 결과를 저장할 리스트
    all_recommendations = []

    # TF-IDF 벡터화 객체 생성
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['combined'])

    # 입력 데이터 각각 처리
    for item in data:
        input_name = item.get('courseName', '').strip()
        input_details = item.get('courseDetails', '').strip()

        if not input_name or not input_details:
            all_recommendations.append({
                "input": item,
                "error": "Invalid input. 'courseName' and 'courseDetails' must be non-empty."
            })
            continue

        input_text = input_name + " " + input_details
        input_vector = vectorizer.transform([input_text])
        cosine_similarities = cosine_similarity(input_vector, tfidf_matrix).flatten()

        # 유사도 계산 및 상위 20개 추출
        df['similarity'] = cosine_similarities
        top_courses = df.sort_values(by='similarity', ascending=False).head(20)

        # 상위 20개 중 랜덤으로 3개 선택
        if len(top_courses) >= 3:
            # 인덱스 재설정 후 샘플 추출
            random_courses = top_courses.reset_index(drop=True).sample(n=3, random_state=None)
        else:
            random_courses = top_courses.reset_index(drop=True)

        # 결과 추가
        recommendations = random_courses[['inflearnCourseName', 'inflearnCourseDetails', 'courseURL', 'similarity', 'imgURL']].to_dict(orient='records')
        all_recommendations.append({
            "input": item,
            "recommendations": recommendations
        })

    return jsonify(all_recommendations)

if __name__ == '__main__':
    app.run(debug=True)
