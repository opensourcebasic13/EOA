import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import "../App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function Login({ onLogin }) {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/api/users/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || "로그인에 실패했습니다.");
      }

      const token = result.data?.token;
      const user = result.data?.user;

      if (!token || !user) {
        throw new Error("로그인 응답에 token 또는 user 정보가 없습니다.");
      }

      onLogin(token, user);
      navigate("/home");
    } catch (error) {
      console.error(error);
      setError(error.message || "로그인 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">EOA</div>
        <h1>로그인</h1>
        <p>X 기반 해외주식 트렌드 분석 서비스를 시작하세요.</p>

        {error && <div className="error-box">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            아이디
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="아이디"
              autoComplete="username"
              required
            />
          </label>

          <label>
            비밀번호
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="비밀번호"
              autoComplete="current-password"
              required
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <div className="auth-footer">
          계정이 없나요? <Link to="/signup">회원가입</Link>
        </div>

        <Link className="back-link" to="/home">
          대시보드로 돌아가기
        </Link>
      </div>
    </div>
  );
}

export default Login;
