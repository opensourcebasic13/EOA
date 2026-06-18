import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { useState } from "react";

import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("eoa_token"));
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("eoa_user");

    if (!savedUser) {
      return null;
    }

    try {
      return JSON.parse(savedUser);
    } catch {
      return null;
    }
  });

  const handleLogin = (nextToken, nextUser) => {
    localStorage.setItem("eoa_token", nextToken);
    localStorage.setItem("eoa_user", JSON.stringify(nextUser));

    setToken(nextToken);
    setUser(nextUser);
  };

  const handleLogout = () => {
    localStorage.removeItem("eoa_token");
    localStorage.removeItem("eoa_user");

    setToken(null);
    setUser(null);
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route
          path="/home"
          element={<Dashboard token={token} user={user} onLogout={handleLogout} />}
        />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/signup" element={<Signup onLogin={handleLogin} />} />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
