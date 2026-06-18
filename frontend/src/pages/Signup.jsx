import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import "../App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function Signup({ onLogin }) {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password_confirm: "",
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

    if (form.password !== form.password_confirm) {
      setError("비밀번호와 비밀번호 확인이 다릅니다.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/api/users/signup/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || "회원가입에 실패했습니다.");
      }

      const token = result.data?.token;
      const user = result.data?.user;

      if (token && user) {
        onLogin(token, user);
        navigate("/home");
        return;
      }

      navigate("/login");
    } catch (error) {
      console.error(error);
      setError(error.message || "회원가입 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">EOA</div>
        <h1>회원가입</h1>
        <p>관심 종목을 저장하고 맞춤형 주식 트렌드를 확인하세요.</p>

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
            이메일
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="email@example.com"
              autoComplete="email"
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
              autoComplete="new-password"
              required
            />
          </label>

          <label>
            비밀번호 확인
            <input
              name="password_confirm"
              type="password"
              value={form.password_confirm}
              onChange={handleChange}
              placeholder="비밀번호 확인"
              autoComplete="new-password"
              required
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "가입 중..." : "회원가입"}
          </button>
        </form>

        <div className="auth-footer">
          이미 계정이 있나요? <Link to="/login">로그인</Link>
        </div>

        <Link className="back-link" to="/home">
          대시보드로 돌아가기
        </Link>
      </div>
    </div>
  );
}

export default Signup;
