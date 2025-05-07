# 🔐 CodeAnalyze CLI

**AI 기반 코드 보안 분석기를 명령어로 간편하게 실행할 수 있는 CLI 도구입니다.**  
CodeBERT와 GPT API를 활용해 소스 코드의 보안 취약점을 자동으로 탐지하고, 리포트를 생성합니다.


## 📦 설치 방법

```bash
pip install codeanalyze

※ PyPI에 등록 완료 후 사용 가능

## 🚀 사용 예시

### 🔍 보안 취약점 분석

```bash
codeanalyze analyze -f vulnerable.py
```

출력 예시:

```
🛡️ 예측 결과: ⚠️ SQL Injection 취약점 감지
🔖 라벨: SQL_Injection
📊 보안 점수: 30
```

### 📝 보안 리포트 생성 (DOCX 다운로드)

```bash
codeanalyze report -f vulnerable.py --docx
```

생성 결과:

```
📄 Security_Report.docx 파일이 생성되었습니다.
```

---

## 🛠️ 주요 기능

* ✅ CodeBERT 기반 보안 취약점 탐지
* ✅ GPT 기반 상세 보안 리포트 자동 생성
* ✅ Word(DOCX) 리포트 파일 다운로드

---

## 🌐 백엔드 API 서버 정보

본 CLI는 다음 API 서버와 연결됩니다:

```
https://ai-powered-code-security-analyzer.onrender.com
```

---

## 📁 예제 코드 (vulnerable.py)

```python
user_input = input("Enter ID: ")
sql = "SELECT * FROM users WHERE id = " + user_input
```

---

## 🧑‍💻 개발자 정보

* GitHub: [https://github.com/tealight03/CapstoneDesign](https://github.com/tealight03/CapstoneDesign)
* Email: [davin0706@gmail.com](mailto:davin0706@gmail.com)

---

## 📝 라이선스

MIT License