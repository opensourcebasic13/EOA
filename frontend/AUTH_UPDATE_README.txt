EOA frontend auth update

변경 내용:
- react-router-dom 추가
- /login, /signup, /home 라우팅 추가
- 기존 대시보드 UI는 src/pages/Dashboard.jsx로 이동
- 로그인/회원가입 페이지 추가
- 로그인 token을 localStorage(eoa_token)에 저장
- 관심주식 추가/삭제 버튼 API 연결

적용 방법:
1. 이 zip의 frontend 폴더 내용을 기존 frontend 폴더에 덮어씌우기
2. cd frontend
3. npm install
4. echo "VITE_API_BASE_URL=http://127.0.0.1:8000" > .env
5. npm run dev

주소:
- http://localhost:5173/home
- http://localhost:5173/login
- http://localhost:5173/signup
