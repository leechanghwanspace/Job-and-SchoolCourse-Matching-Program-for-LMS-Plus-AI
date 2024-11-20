import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify

app = Flask(__name__)

# CSV 파일 읽기
try:
    df = pd.read_csv('courses.csv')
    # 열 이름 확인 및 변경
    df.columns = ['courseName', 'courseDetails', 'courseURL']  # 컬럼 이름 강제 지정
except FileNotFoundError:
    raise Exception("courses.csv 파일을 찾을 수 없습니다. 경로를 확인하세요.")

# 데이터 전처리: 결측치 제거
df = df.dropna(subset=['courseName', 'courseDetails']).reset_index(drop=True)

@app.route('/recommend', methods=['POST'])
def recommend_courses():
    # 입력 데이터
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

    # 코사인 유사도 계산
    input_vector = tfidf_matrix[-1]  # 마지막 벡터가 입력 데이터
    cosine_similarities = cosine_similarity(input_vector, tfidf_matrix[:-1]).flatten()

    # 유사도 결과 추가 및 정렬
    df['similarity'] = cosine_similarities
    top_courses = df.sort_values(by='similarity', ascending=False).head(3)

    # 결과 JSON 생성
    result = top_courses[['courseName', 'courseDetails', 'courseURL', 'similarity']].to_dict(orient='records')
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
