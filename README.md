# Job and SchoolCourse Similarity Extraction Program

이 프로젝트는 Flask 기반의 API로, 선택한 직업과 관련성이 높은 교과목을 추천해주는 프로그램입니다. MySQL 데이터베이스와 연결하여 직업 및 교과목 정보를 조회하고, 코사인 유사도를 사용하여 선택한 직업과 교과목 간의 유사도를 계산합니다. 이후 상위 5개의 관련 교과목을 반환합니다.

## 기능

- **직업과 교과목 유사도 계산**: TF-IDF 벡터화와 코사인 유사도를 사용하여 직업과 교과목 설명을 비교합니다.
- **동적 추천 기능**: 사용자가 선택한 직업에 따라 관련 교과목을 추천합니다.
- **Flask API 엔드포인트**: `/recommend-courses` 엔드포인트를 통해 접근할 수 있으며, 직업 ID를 입력하면 유사도가 높은 상위 5개의 교과목 정보를 반환합니다.

## 주요 구성 요소

- `calculate_cosine_similarity`: 두 텍스트 간 코사인 유사도를 계산하여 주어진 boost factor(1.5)를 적용하여 유사도를 강화합니다.
- `get_recommended_courses`: job_id를 기반으로 직업 이름을 조회하고, school_course 테이블의 모든 교과목과 비교하여 유사도를 계산한 뒤, 상위 5개의 교과목을 추천합니다.
- `Flask API`: 사용자가 직업 ID를 입력으로 제공하여 추천 교과목을 조회할 수 있도록 하는 API입니다.

<br>

---
### 관련 레포지토리
[RedPenLMS-BE](https://github.com/leechanghwanspace/RedPenLMS-BE)